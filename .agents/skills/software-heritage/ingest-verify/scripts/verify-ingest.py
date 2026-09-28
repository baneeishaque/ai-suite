#!/usr/bin/env python3
"""Verify Software Heritage ingest of the current HEADs.

Queries the public SWH REST API (no auth) and checks, per origin, that:
 1. the origin is known (GET /api/1/origin/<url>/get/),
 2. the expected revision is archived (GET /api/1/revision/<sha>/),
 3. the latest snapshot actually contains that revision as a branch target
    (GET /api/1/origin/<url>/visit/latest/ + GET /api/1/snapshot/<id>/).

Exit codes:
 0  VERIFIED — every check reports its HEAD in its latest snapshot.
 1  PENDING  — origin known but HEAD not yet in a snapshot; SWH ingest
    lags pushes by hours. CI should warn, not fail.
 2  FAILED   — origin unknown and no save could be triggered, or HTTP/API
    errors (incl. Anubis bot-challenge pages on non-browser clients).

With --trigger-save, a best-effort POST /api/1/origin/save/git/url/<origin>/
fires first — the API equivalent of the manual "Save code now" click that
swh-save-code-now performs in Chrome. Never fatal: save throttling/rejection
just yields a note in the report.
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

API_ROOT = "https://archive.softwareheritage.org/api/1"
USER_AGENT = (
    "ai-suite-swh-verify/1.0 (+https://github.com/baneeishaque/ai-suite)"
)


def api_get(path: str, timeout: float) -> Tuple[int, Any]:
    """GET a JSON API path. Returns (http_status, parsed_body_or_None)."""
    req = urllib.request.Request(
        API_ROOT + path,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.load(resp)
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError("GET %s failed: %s" % (path, exc))


def api_post_save(origin: str, timeout: float) -> Dict[str, Any]:
    """Best-effort Save-code-now POST for a git origin."""
    path = "/origin/save/git/url/%s/" % urllib.parse.quote(origin, safe="")
    req = urllib.request.Request(
        API_ROOT + path,
        data=b"",
        method="POST",
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.load(resp)
            body["_http_status"] = resp.status
            return body
    except urllib.error.HTTPError as exc:
        try:
            body = json.load(exc)
        except Exception:
            body = {}
        body["_http_status"] = exc.code
        try:
            body["_raw"] = exc.read(300).decode("utf-8", "replace")
        except Exception:
            pass
        return body
    except (urllib.error.URLError, TimeoutError) as exc:
        return {"_http_status": -1, "error": str(exc)}


def check_origin(origin: str, expected_rev: str, timeout: float) -> Dict[str, Any]:
    """Run the three ingest checks for one origin. Returns a report dict."""
    expected = expected_rev.lower()
    enc = urllib.parse.quote(origin, safe="")
    report: Dict[str, Any] = {
        "origin": origin,
        "expected_rev": expected,
        "origin_known": False,
        "revision_archived": False,
        "snapshot_contains_rev": False,
        "snapshot_swhid": None,
        "visit_date": None,
        "verdict": "FAILED",
    }

    status, _ = api_get("/origin/%s/get/" % enc, timeout)
    if status == 403:
        report["note"] = "HTTP 403 (Anubis challenge suspected; retry or use Chrome)"
        return report
    if status != 200:
        report["note"] = "origin not known to SWH (HTTP %s)" % status
        return report
    report["origin_known"] = True

    status, _ = api_get("/revision/%s/" % expected, timeout)
    report["revision_archived"] = status == 200

    status, latest = api_get(
        "/origin/%s/visit/latest/?require_snapshot=true" % enc, timeout
    )
    snapshot = (latest or {}).get("snapshot") if isinstance(latest, dict) else None
    if status == 200 and snapshot:
        report["snapshot"] = snapshot
        report["visit_date"] = (latest or {}).get("date")
        snap_status, snap = api_get("/snapshot/%s/" % snapshot, timeout)
        if snap_status == 200 and isinstance(snap, dict):
            branches = snap.get("branches") or {}
            for _name, branch in branches.items():
                target = (branch or {}).get("target", "")
                if isinstance(target, str) and target.lower() == expected:
                    report["snapshot_contains_rev"] = True
                    break
            if report["snapshot_contains_rev"]:
                report["snapshot_swhid"] = "swh:1:snp:%s" % snapshot

    if report["snapshot_contains_rev"]:
        report["verdict"] = "VERIFIED"
    elif report["origin_known"]:
        report["verdict"] = "PENDING"
        report["note"] = report.get(
            "note", "HEAD not yet in latest snapshot (ingest lag or save pending)"
        )
    return report


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Verify SWH archive holds the current HEADs."
    )
    parser.add_argument(
        "--check",
        action="append",
        default=[],
        metavar="ORIGIN_URL,EXPECTED_REV",
        help="Origin + expected git SHA, comma-separated. Repeatable.",
    )
    parser.add_argument(
        "--trigger-save",
        action="store_true",
        help="Best-effort Save-code-now POST before verifying.",
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON report."
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point. Returns process exit code."""
    args = parse_args(argv)
    if not args.check:
        print("error: at least one --check ORIGIN_URL,EXPECTED_REV required",
              file=sys.stderr)
        return 2

    specs: List[Tuple[str, str]] = []
    for raw in args.check:
        parts = [p.strip() for p in raw.split(",", 1)]
        if len(parts) != 2 or not parts[0] or not parts[1]:
            print("error: malformed --check %r (want URL,REVSHA)" % raw,
                  file=sys.stderr)
            return 2
        specs.append((parts[0], parts[1]))

    save_notes: List[Dict[str, Any]] = []
    if args.trigger_save:
        for origin, _ in specs:
            save_notes.append({"origin": origin,
                               "save": api_post_save(origin, args.timeout)})

    reports = [check_origin(o, r, args.timeout) for o, r in specs]
    overall = "VERIFIED"
    for rep in reports:
        if rep["verdict"] == "FAILED":
            overall = "FAILED"
            break
        if rep["verdict"] == "PENDING":
            overall = "PENDING"

    if args.json:
        print(json.dumps({"overall": overall, "saves": save_notes,
                          "checks": reports}, indent=2))
    else:
        for rep in reports:
            line = "[%s] %s rev %s" % (
                rep["verdict"], rep["origin"], rep["expected_rev"][:12])
            if rep.get("snapshot_swhid"):
                line += " snapshot %s" % rep["snapshot_swhid"]
            if rep.get("note"):
                line += " — %s" % rep["note"]
            print(line)
        print("overall: %s" % overall)

    return {"VERIFIED": 0, "PENDING": 1, "FAILED": 2}[overall]


if __name__ == "__main__":
    sys.exit(main())
