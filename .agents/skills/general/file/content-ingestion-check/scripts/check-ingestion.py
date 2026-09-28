#!/usr/bin/env python3
"""Content Ingestion Check Engine — Verify content hashes are archived.

Generic HTTP client that checks whether git blob SHA-1 hashes are present
in a content-addressable archive (defaults to Software Heritage's public API).
Returns KNOWN/UNKNOWN per hash with a 0/1/2 exit-code contract.

Domain-agnostic — the archive base URL and lookup path templates are
configurable so this can target SWH, IPFS, or any hash-lookup API.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_API_BASE = "https://archive.softwareheritage.org/api/1"
DEFAULT_SINGLE_PATH = "/content/sha1_git:{hash}/"
DEFAULT_BATCH_PATH = "/content/known/{hashes}/"
USER_AGENT = (
    "ai-suite-swh-content-check/1.0 "
    "(+https://github.com/baneeishaque/ai-suite)"
)


class IngestionResult:
    """Holds the result of checking one or more hashes."""

    def __init__(self) -> None:
        self.checks: List[Dict[str, Any]] = []
        self.transport_error: Optional[str] = None

    @property
    def all_known(self) -> bool:
        """Return True iff every checked hash was known."""
        return all(c.get("known") for c in self.checks)

    @property
    def has_unknown(self) -> bool:
        """Return True iff at least one hash is unknown."""
        return any(not c.get("known") for c in self.checks)

    def exit_code(self) -> int:
        """Map results to process exit code: 0 all known, 1 any unknown, 2 transport."""
        if self.transport_error:
            return 2
        if self.has_unknown:
            return 1
        return 0


def http_get(url: str, timeout: float) -> Tuple[int, Any]:
    """GET url, return (http_status, parsed_json_or_None). Raises RuntimeError on transport failure."""
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            try:
                return resp.status, json.load(resp)
            except json.JSONDecodeError:
                return resp.status, None
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            raise RuntimeError(
                "HTTP 403 from archive (Anubis PoW challenge suspected; "
                "open the URL once in a real browser to clear, then retry)"
            )
        try:
            return exc.code, json.load(exc)
        except (json.JSONDecodeError, AttributeError):
            return exc.code, None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        raise RuntimeError("Transport error contacting archive: %s" % exc)


def check_single(hash_val: str, api_base: str, single_path: str,
                 timeout: float, result: IngestionResult) -> None:
    """Check one hash via the single-lookup endpoint."""
    url = api_base.rstrip("/") + single_path.format(hash=hash_val)
    try:
        status, _ = http_get(url, timeout)
    except RuntimeError as exc:
        result.transport_error = str(exc)
        return
    known = status == 200
    result.checks.append({"hash": hash_val, "known": known, "http_status": status})


def check_batch(hashes: List[str], api_base: str, batch_path: str,
                timeout: float, result: IngestionResult) -> None:
    """Check many hashes via the batch-known endpoint."""
    # SWH content/known/ accepts comma-joined sha1 values.
    encoded = ",".join(hashes)
    url = api_base.rstrip("/") + batch_path.format(hashes=encoded)
    try:
        status, body = http_get(url, timeout)
    except RuntimeError as exc:
        result.transport_error = str(exc)
        return
    if status != 200 or not isinstance(body, dict):
        # Fall back to per-hash single lookup if batch endpoint differs.
        for h in hashes:
            check_single(h, api_base, DEFAULT_SINGLE_PATH, timeout, result)
        return
    # SWH content/known returns {"known": ["sha1", ...], "missing": ["sha1", ...]}
    known_set = set(body.get("known", []))
    for h in hashes:
        result.checks.append({
            "hash": h,
            "known": h in known_set,
            "http_status": status,
        })


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Check whether content hashes are present in a content archive."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--hash", help="Single SHA-1 git blob hash to check.")
    group.add_argument("--hashes", help="File with one hash per line (batch).")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE,
                        help="Archive API root URL.")
    parser.add_argument("--single-path", default=DEFAULT_SINGLE_PATH,
                        help="URL template for single lookups (use {hash}).")
    parser.add_argument("--batch-path", default=DEFAULT_BATCH_PATH,
                        help="URL template for batch lookups (use {hashes}).")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--json", action="store_true", help="JSON output.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point. Returns process exit code."""
    args = parse_args(argv)
    result = IngestionResult()

    if args.hash:
        if len(args.hash) != 40:
            print("error: hash must be 40 hex chars, got %r" % args.hash[:8],
                  file=sys.stderr)
            return 2
        check_single(args.hash.lower(), args.api_base, args.single_path,
                     args.timeout, result)
    else:
        hashes: List[str] = []
        try:
            with open(args.hashes, "r", encoding="utf-8") as handle:
                for line in handle:
                    h = line.strip().split()[0] if line.strip() else ""
                    if h and len(h) == 40:
                        hashes.append(h.lower())
        except OSError as exc:
            print("error: cannot read hashes file: %s" % exc, file=sys.stderr)
            return 2
        if not hashes:
            print("error: no valid hashes found in %s" % args.hashes, file=sys.stderr)
            return 2
        check_batch(hashes, args.api_base, args.batch_path, args.timeout, result)

    if result.transport_error:
        print("error: %s" % result.transport_error, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({
            "checks": result.checks,
            "all_known": result.all_known,
        }, indent=2))
    else:
        for c in result.checks:
            verdict = "KNOWN" if c["known"] else "UNKNOWN"
            print("%s %s (http %s)" % (verdict, c["hash"][:12], c.get("http_status")))
    return result.exit_code()


if __name__ == "__main__":
    sys.exit(main())
