#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Classify a GitHub pull request's merge decision with a Laya/Jev System One model.

Scope: this script is the deterministic core of the `pr-merge-decision-classifier`
skill. It builds a read-only state object for a pull request via `gh`, asks a
System One endpoint (`POST /v1/systemone`) a fixed set of typed questions
(`choice` / `score` / `noul`), applies a deterministic confidence/risk gate, and
reports a `MERGE` / `HOLD` verdict with per-condition reasons. With `--execute`
it merges (rebase + delete branch) when — and only when — the gate returns MERGE.

Exit codes: 0 = MERGE, 1 = HOLD, 2 = error (backend / gh / parse / merge failure).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Paths and constants (all resolution is relative to this script's location)
# ---------------------------------------------------------------------------

SCRIPT_PATH = Path(__file__).resolve()
SCRIPTS_DIR = SCRIPT_PATH.parent
FIXTURES_DIR = SCRIPTS_DIR / "fixtures"
SKILLS_DIR = SCRIPT_PATH.parents[4]
READ_JSONC = SKILLS_DIR / "opencode-jsonc-util" / "scripts" / "read-jsonc.py"
OPENCODE_CONFIG = Path.home() / ".config" / "opencode" / "opencode.json"
AUTH_JSON = Path.home() / ".local" / "share" / "opencode" / "auth.json"

SYSTEMONE_PATH = "/v1/systemone"
GH_TIMEOUT_SECS = 60
MERGE_TIMEOUT_SECS = 180

PR_VIEW_FIELDS = (
    "number,title,body,state,baseRefName,headRefName,headRefOid,mergeable,"
    "mergeStateStatus,additions,deletions,changedFiles,author,labels,files,"
    "commits,reviews,comments"
)

POLICY: Dict[str, Any] = {
    "merge_method": "rebase",
    "delete_branch": True,
    "ci": "none",
    "review_required": True,
}

QUESTIONS: Dict[str, Any] = {
    "merge_decision": {
        "type": "choice",
        "instructions": "Should this pull request be merged into its base branch now?",
        "criteria": {
            "merge": "The change is complete, correct, scoped to its stated purpose, and safe to merge",
            "hold": "Unresolved issues, risks, missing verification, or out-of-scope changes mean it must not be merged yet",
        },
    },
    "risk": {
        "type": "score",
        "instructions": "Assess the risk of merging this pull request.",
        "criteria": ["Low", "Moderate", "High", "Critical"],
    },
    "breaking_change": {
        "type": "noul",
        "instructions": "Does this pull request introduce breaking changes or regressions to existing functionality?",
        "threshold": 0.5,
    },
    "scope_creep": {
        "type": "noul",
        "instructions": "Does this pull request contain changes unrelated to its stated purpose?",
        "threshold": 0.5,
    },
    "checks_satisfied": {
        "type": "noul",
        "instructions": "Are all required CI checks and review requirements satisfied for this pull request?",
        "threshold": 0.5,
    },
}

BACKEND_DEFAULTS: Dict[str, Dict[str, Optional[str]]] = {
    "laya": {
        "base_url": "http://127.0.0.1:8081",
        "model": "laya-multilingual",
        "env_key": None,
        "auth_provider": None,
        "provider_name": None,
    },
    "apimaster": {
        "base_url": "https://apimaster.ai/v1",
        "model": "jev-latest",
        "env_key": "APIMASTER_API_KEY",
        "auth_provider": "apimaster",
        "provider_name": "apimaster",
    },
    "morphllm": {
        "base_url": "https://api.morphllm.com/v1",
        "model": "systemone-latest",
        "env_key": "MORPHLLM_KEY",
        "auth_provider": "morphllm",
        "provider_name": "morphllm",
    },
    "typesafe": {
        "base_url": "https://api.typesafe.ai/v1",
        "model": "jev-latest",
        "env_key": "TYPESAFE_API_KEY",
        "auth_provider": None,
        "provider_name": None,
    },
}


class CtxError(RuntimeError):
    """Expected, user-facing failure that maps to exit code 2."""


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------


def timestamp_ist() -> str:
    """Return the current local time stamped with the machine's IST label."""
    return datetime.now().strftime("%Y-%m-%d %H:%M IST")


def run_cmd(cmd: Sequence[str], timeout: int = GH_TIMEOUT_SECS) -> Tuple[int, str, str]:
    """Run a command and return ``(returncode, stdout, stderr)`` without raising on failure.

    Args:
        cmd: Command and arguments.
        timeout: Maximum seconds to wait.

    Returns:
        Tuple of return code, captured stdout, captured stderr.

    Raises:
        CtxError: If the executable is missing or the command times out.
    """
    try:
        proc = subprocess.run(
            list(cmd), capture_output=True, text=True, timeout=timeout, check=False
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as exc:
        raise CtxError(f"command not found: {cmd[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise CtxError(f"command timed out after {timeout}s: {cmd[0]}") from exc


def truncate_text(text: str, limit: int) -> Tuple[str, bool]:
    """Truncate ``text`` to ``limit`` characters, appending a marker when cut."""
    if limit <= 0 or len(text) <= limit:
        return text, False
    return text[:limit] + "…[truncated]", True


def redact(text: str, secrets: Sequence[str]) -> str:
    """Replace any known secret value and Bearer tokens with ``***``."""
    out = text
    for secret in secrets:
        if secret:
            out = out.replace(secret, "***")
    return re.sub(r"(Bearer\s+)[A-Za-z0-9._\-]+", r"\1***", out)


def load_json_file(path: Path) -> Dict[str, Any]:
    """Read a JSON object from disk with a user-facing error on failure."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CtxError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CtxError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise CtxError(f"expected a JSON object in {path}")
    return data


# ---------------------------------------------------------------------------
# Backend resolution (provider base URLs, keys) — read-only, never echoes keys
# ---------------------------------------------------------------------------


def provider_api_base(provider: str) -> Optional[str]:
    """Read ``provider.<name>.api`` from the OpenCode JSONC config via read-jsonc.py."""
    if not READ_JSONC.exists() or not OPENCODE_CONFIG.exists():
        return None
    rc, out, _ = run_cmd(["python3", str(READ_JSONC), str(OPENCODE_CONFIG)])
    if rc != 0:
        return None
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return None
    api = data.get("provider", {}).get(provider, {}).get("api")
    return api if isinstance(api, str) and api else None


def auth_key(provider: str) -> Optional[str]:
    """Read ``auth.json[provider].key`` when present (value is never printed)."""
    if not AUTH_JSON.exists():
        return None
    try:
        data = json.loads(AUTH_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    entry = data.get(provider)
    if isinstance(entry, dict):
        key = entry.get("key")
        if isinstance(key, str) and key:
            return key
    return None


def resolve_base_url(name: str, override: Optional[str]) -> str:
    """Resolve the backend base URL: CLI override → provider config → built-in default."""
    if override:
        return override.rstrip("/")
    cfg = BACKEND_DEFAULTS[name]
    provider = cfg["provider_name"]
    if provider:
        api = provider_api_base(provider)
        if api:
            return api.rstrip("/")
    return str(cfg["base_url"]).rstrip("/")


def resolve_key(name: str, override: Optional[str]) -> Tuple[Optional[str], str]:
    """Resolve an API key as (value, source) where source is flag|env|auth.json|missing."""
    if override:
        return override, "flag"
    cfg = BACKEND_DEFAULTS[name]
    env_name = cfg["env_key"]
    if env_name and os.environ.get(env_name):
        return os.environ[env_name], "env"
    provider = cfg["auth_provider"]
    if provider:
        key = auth_key(provider)
        if key:
            return key, "auth.json"
    return None, "missing"


def laya_health(base_url: str) -> bool:
    """Return True when the local Laya server answers its /health endpoint."""
    try:
        with urllib.request.urlopen(base_url.rstrip("/") + "/health", timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def systemone_url(base_url: str) -> str:
    """Build the /v1/systemone URL without doubling a trailing /v1 on the base.

    Provider bases in opencode.json already include ``/v1`` (e.g.
    ``https://apimaster.ai/v1``), so the endpoint path is ``/systemone`` for
    them, while bare hosts (e.g. ``http://127.0.0.1:8081``) need the full
    ``/v1/systemone`` path.
    """
    base = base_url.rstrip("/")
    if base.endswith("/v1"):
        return base + "/systemone"
    return base + SYSTEMONE_PATH


# ---------------------------------------------------------------------------
# State builder (read-only `gh`)
# ---------------------------------------------------------------------------


def gh_json(args: Sequence[str]) -> Any:
    """Run a `gh` command expected to emit JSON and parse it."""
    rc, out, err = run_cmd(["gh", *args])
    if rc != 0:
        raise CtxError(f"gh {args[0]} {args[1]} failed (exit {rc}): {err.strip()[:300]}")
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        raise CtxError(f"gh returned invalid JSON: {exc}") from exc


def gh_checks(repo: str, pr: int) -> List[Dict[str, Any]]:
    """Fetch PR checks; a "no checks reported" result is a valid empty set."""
    rc, out, err = run_cmd(
        ["gh", "pr", "checks", str(pr), "--repo", repo, "--json", "name,state,bucket,link"]
    )
    if rc != 0:
        if "no checks reported" in (out + err).lower():
            return []
        raise CtxError(f"gh pr checks failed (exit {rc}): {err.strip()[:300]}")
    try:
        data = json.loads(out)
    except json.JSONDecodeError as exc:
        raise CtxError(f"gh pr checks returned invalid JSON: {exc}") from exc
    return data if isinstance(data, list) else []


def gh_diff(repo: str, pr: int) -> str:
    """Fetch the PR diff as plain text."""
    rc, out, err = run_cmd(["gh", "pr", "diff", str(pr), "--repo", repo])
    if rc != 0:
        raise CtxError(f"gh pr diff failed (exit {rc}): {err.strip()[:300]}")
    return out


def enforce_state_budget(state: Dict[str, Any], max_chars: int) -> Dict[str, Any]:
    """Shrink the state deterministically until its serialized size fits the budget.

    Reduction order: diff excerpt → comments → reviews → commits → files → body.
    Every reduction sets its truncation flag; ``total_state_chars`` is always the
    final serialized size.
    """
    flags = state["truncation"]

    def size() -> int:
        return len(json.dumps(state, ensure_ascii=False))

    while size() > max_chars:
        if state["diff_excerpt"]:
            state["diff_excerpt"] = state["diff_excerpt"][: max(0, len(state["diff_excerpt"]) // 2)]
            flags["diff"] = True
            continue
        if state["comments"]:
            state["comments"].pop()
            flags["comments"] = True
            continue
        if state["reviews"]:
            state["reviews"].pop()
            flags["reviews"] = True
            continue
        if state["commits"]:
            state["commits"].pop()
            flags["commits"] = True
            continue
        if state["files"]:
            state["files"].pop()
            flags["files"] = True
            continue
        if state["pr"]["body"]:
            state["pr"]["body"] = ""
            flags["body"] = True
            continue
        break
    flags["total_state_chars"] = size()
    return state


def build_state(args: argparse.Namespace) -> Dict[str, Any]:
    """Build the literal state object from read-only `gh` calls."""
    view = gh_json(["pr", "view", str(args.pr), "--repo", args.repo, "--json", PR_VIEW_FIELDS])
    checks = gh_checks(args.repo, args.pr)
    diff = gh_diff(args.repo, args.pr)

    body, body_trunc = truncate_text(view.get("body") or "", args.body_chars)

    reviews: List[Dict[str, str]] = []
    reviews_trunc = False
    for review in view.get("reviews") or []:
        rbody, cut = truncate_text(review.get("body") or "", args.review_chars)
        reviews_trunc = reviews_trunc or cut
        reviews.append(
            {
                "author": (review.get("author") or {}).get("login") or "",
                "state": review.get("state") or "",
                "body": rbody,
            }
        )

    comments: List[Dict[str, str]] = []
    for comment in view.get("comments") or []:
        cbody, _ = truncate_text(comment.get("body") or "", args.review_chars)
        comments.append(
            {
                "author": (comment.get("author") or {}).get("login") or "",
                "body": cbody,
            }
        )

    diff_excerpt, diff_trunc = truncate_text(diff, args.diff_chars)

    state: Dict[str, Any] = {
        "repo": args.repo,
        "pr": {
            "number": view.get("number", args.pr),
            "title": view.get("title") or "",
            "body": body,
            "state": view.get("state") or "",
            "base": view.get("baseRefName") or "",
            "head": view.get("headRefName") or "",
            "head_oid": view.get("headRefOid") or "",
            "mergeable": view.get("mergeable") or "",
            "merge_state_status": view.get("mergeStateStatus") or "",
            "additions": view.get("additions", 0),
            "deletions": view.get("deletions", 0),
            "changed_files": view.get("changedFiles", 0),
            "author": (view.get("author") or {}).get("login") or "",
            "labels": [label.get("name") for label in (view.get("labels") or [])],
        },
        "files": [
            {
                "path": item.get("path", ""),
                "additions": item.get("additions", 0),
                "deletions": item.get("deletions", 0),
            }
            for item in (view.get("files") or [])
        ],
        "commits": [
            {"oid": item.get("oid", ""), "headline": item.get("messageHeadline", "")}
            for item in (view.get("commits") or [])
        ],
        "reviews": reviews,
        "comments": comments,
        "checks": [
            {
                "name": item.get("name", ""),
                "state": item.get("state", ""),
                "bucket": item.get("bucket", ""),
            }
            for item in checks
        ],
        "diff_excerpt": diff_excerpt,
        "policy": dict(POLICY),
        "truncation": {
            "body": body_trunc,
            "reviews": reviews_trunc,
            "diff": diff_trunc,
            "comments": False,
            "commits": False,
            "files": False,
            "total_state_chars": 0,
        },
    }
    return enforce_state_budget(state, args.max_state_chars)


# ---------------------------------------------------------------------------
# System One call and gate
# ---------------------------------------------------------------------------


def call_systemone(
    url: str,
    key: Optional[str],
    model: str,
    state: Dict[str, Any],
    timeout: int,
    secrets: Sequence[str],
) -> Dict[str, Any]:
    """POST ``{state, questions, model}`` to a System One endpoint and parse the response."""
    payload = {"state": state, "questions": QUESTIONS, "model": model}
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    if key:
        request.add_header("Authorization", f"Bearer {key}")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
        except Exception:
            detail = ""
        raise CtxError(f"backend HTTP {exc.code} for {url}: {redact(detail, secrets)}") from exc
    except urllib.error.URLError as exc:
        raise CtxError(f"backend unreachable at {url}: {exc.reason}") from exc
    except (TimeoutError, socket.timeout) as exc:
        raise CtxError(f"backend timed out after {timeout}s for {url}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CtxError(f"backend returned invalid JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("answers"), dict):
        raise CtxError("backend response is missing the answers object")
    return data


def evaluate_gate(
    answers: Dict[str, Any], min_confidence: float, max_risk: float
) -> Tuple[str, List[str]]:
    """Apply the deterministic gate and return ``(verdict, reasons)``.

    MERGE iff the choice is ``merge`` AND its confidence ≥ ``min_confidence`` AND
    the risk score ≤ ``max_risk`` AND ``breaking_change``/``scope_creep`` are False
    AND ``checks_satisfied`` is True. HOLD lists every failed condition with its
    observed value.
    """
    reasons: List[str] = []

    decision = answers.get("merge_decision", {})
    choice = decision.get("choice")
    confidence = float(decision.get("confidence", 0.0) or 0.0)
    if choice != "merge":
        reasons.append(f'merge_decision.choice="{choice}" != "merge"')
    if confidence < min_confidence:
        reasons.append(f"merge_decision.confidence={confidence} < {min_confidence}")

    risk = answers.get("risk", {})
    score = float(risk.get("score", 999.0) or 999.0)
    if score > max_risk:
        reasons.append(f"risk.score={score} > {max_risk}")

    for key, expected, label in (
        ("breaking_change", False, "breaking_change.decision"),
        ("scope_creep", False, "scope_creep.decision"),
        ("checks_satisfied", True, "checks_satisfied.decision"),
    ):
        answer = answers.get(key, {})
        observed = answer.get("decision")
        if observed is not expected:
            noul = answer.get("noul")
            suffix = f" (noul={noul})" if noul is not None else ""
            reasons.append(f"{label}={observed}{suffix}")

    return ("HOLD" if reasons else "MERGE"), reasons


# ---------------------------------------------------------------------------
# Backends
# ---------------------------------------------------------------------------


def call_single_backend(
    args: argparse.Namespace,
    state: Dict[str, Any],
    results: Dict[str, Any],
    secrets: Sequence[str],
) -> Dict[str, Any]:
    """Call the one selected backend and return its answers."""
    name = args.backend
    cfg = BACKEND_DEFAULTS[name]
    base_url = resolve_base_url(name, args.base_url)
    key, key_source = resolve_key(name, args.api_key)
    if name != "laya" and key is None:
        raise CtxError(f"no key for backend {name} (env {cfg['env_key']} or auth.json)")
    model = args.model or str(cfg["model"])
    if name == "laya" and not laya_health(base_url):
        raise CtxError(f"laya server not reachable at {base_url} (start it with laya-server.sh start)")
    response = call_systemone(
        systemone_url(base_url), key, model, state, args.timeout, secrets
    )
    answers = response["answers"]
    results[name] = {
        "ok": True,
        "model": response.get("model", model),
        "answers": answers,
        "key_source": key_source,
    }
    return answers


def call_all_backends(
    args: argparse.Namespace,
    state: Dict[str, Any],
    results: Dict[str, Any],
    secrets: Sequence[str],
) -> Tuple[List[Tuple[str, Dict[str, Any]]], List[str]]:
    """Call every backend whose server is up / key is present.

    Returns the responding ``(name, answers)`` pairs and the error strings of
    backends that were attempted but failed (a failed backend never counts as
    agreement).
    """
    responding: List[Tuple[str, Dict[str, Any]]] = []
    errors: List[str] = []
    for name in ("laya", "apimaster", "morphllm", "typesafe"):
        cfg = BACKEND_DEFAULTS[name]
        base_url = resolve_base_url(name, None)
        if name == "laya":
            if not laya_health(base_url):
                results[name] = {"ok": False, "skipped": True, "error": "server not up"}
                continue
            key, key_source = None, "none"
        else:
            key, key_source = resolve_key(name, None)
            if key is None:
                results[name] = {"ok": False, "skipped": True, "error": "no key"}
                continue
        model = str(cfg["model"])
        try:
            response = call_systemone(
                systemone_url(base_url), key, model, state, args.timeout, secrets
            )
            answers = response["answers"]
            results[name] = {
                "ok": True,
                "model": response.get("model", model),
                "answers": answers,
                "key_source": key_source,
            }
            responding.append((name, answers))
        except CtxError as exc:
            results[name] = {"ok": False, "error": str(exc)}
            errors.append(f"{name}: {exc}")
    return responding, errors


# ---------------------------------------------------------------------------
# Merge execution (only via --execute + MERGE verdict)
# ---------------------------------------------------------------------------


def merge_command(args: argparse.Namespace) -> List[str]:
    """Return the exact, fixed merge command (rebase merge + delete branch)."""
    return ["gh", "pr", "merge", str(args.pr), "--repo", args.repo, "--rebase", "--delete-branch"]


def run_merge(args: argparse.Namespace, secrets: Sequence[str]) -> Dict[str, Any]:
    """Execute the fixed merge command and record the resulting merge commit."""
    cmd = merge_command(args)
    rc, _, err = run_cmd(cmd, timeout=MERGE_TIMEOUT_SECS)
    if rc != 0:
        return {
            "executed": False,
            "command": " ".join(cmd),
            "result": "failed",
            "merge_commit": "",
            "timestamp_ist": timestamp_ist(),
            "error": f"gh pr merge failed (exit {rc}): {redact(err.strip()[:300], secrets)}",
        }
    merge_commit = ""
    rc2, out2, _ = run_cmd(
        ["gh", "pr", "view", str(args.pr), "--repo", args.repo, "--json", "mergeCommit"]
    )
    if rc2 == 0:
        try:
            merge_commit = (json.loads(out2).get("mergeCommit") or {}).get("oid", "") or ""
        except json.JSONDecodeError:
            merge_commit = ""
    return {
        "executed": True,
        "command": " ".join(cmd),
        "result": "merged",
        "merge_commit": merge_commit,
        "timestamp_ist": timestamp_ist(),
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def build_output(
    args: argparse.Namespace,
    verdict: str,
    reasons: List[str],
    backends: Dict[str, Any],
    state: Dict[str, Any],
    execution: Dict[str, Any],
) -> Dict[str, Any]:
    """Assemble the literal verdict JSON contract."""
    return {
        "verdict": verdict,
        "reasons": reasons,
        "backends": backends,
        "thresholds": {"min_confidence": args.min_confidence, "max_risk": args.max_risk},
        "state_summary": {
            "repo": state.get("repo", args.repo),
            "pr": state.get("pr", {}).get("number", args.pr),
            "head_oid": state.get("pr", {}).get("head_oid", ""),
            "files": len(state.get("files", [])),
            "checks": len(state.get("checks", [])),
        },
        "suggested_next_command": " ".join(merge_command(args)),
        "execution": execution,
        "timestamp_ist": timestamp_ist(),
    }


def text_to_human(obj: Dict[str, Any]) -> str:
    """Render the output object as a short human-readable summary."""
    if obj.get("dry_run"):
        return "DRY RUN: state + questions built; no HTTP call, no merge."
    if "error" in obj and "verdict" not in obj:
        return f"ERROR: {obj['error']}"
    lines = [f"VERDICT: {obj.get('verdict')}"]
    if obj.get("error"):
        lines.append(f"ERROR: {obj['error']}")
    for reason in obj.get("reasons", []):
        lines.append(f"  - {reason}")
    for name, backend in (obj.get("backends") or {}).items():
        if backend.get("ok"):
            answers = backend.get("answers", {})
            decision = answers.get("merge_decision", {})
            risk = answers.get("risk", {})
            lines.append(
                f"  {name}: choice={decision.get('choice')} "
                f"confidence={decision.get('confidence')} risk={risk.get('score')}"
            )
        else:
            state = "skipped" if backend.get("skipped") else "error"
            lines.append(f"  {name}: {state} ({backend.get('error', '')})")
    execution = obj.get("execution") or {}
    if execution:
        extra = f" commit={execution['merge_commit']}" if execution.get("merge_commit") else ""
        lines.append(f"EXECUTION: {execution.get('result')}{extra}")
    return "\n".join(lines)


def emit(obj: Dict[str, Any], args: argparse.Namespace, secrets: Sequence[str]) -> None:
    """Print the object (JSON or text) and optionally write the JSON to --out."""
    rendered = redact(json.dumps(obj, indent=2, ensure_ascii=False), secrets)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")
    print(rendered if args.json else text_to_human(obj))


# ---------------------------------------------------------------------------
# Self-test (offline gate verification over the canned fixtures)
# ---------------------------------------------------------------------------

SELF_TEST_CASES: List[Tuple[str, str, Optional[str]]] = [
    ("answers-merge.json", "MERGE", None),
    ("answers-hold-confidence.json", "HOLD", "confidence=0.62"),
    ("answers-hold-risk.json", "HOLD", "risk.score=2.41"),
    ("answers-hold-breaking.json", "HOLD", "breaking_change.decision=True"),
    ("answers-hold-risk-moderate.json", "HOLD", "risk.score=0.8"),
]


def run_self_test() -> int:
    """Run every canned fixture through the gate and report PASS/FAIL."""
    failures: List[str] = []
    for filename, expected, needle in SELF_TEST_CASES:
        path = FIXTURES_DIR / filename
        if not path.exists():
            failures.append(f"{filename}: fixture missing")
            continue
        try:
            response = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{filename}: invalid JSON ({exc})")
            continue
        verdict, reasons = evaluate_gate(response.get("answers", {}), 0.9, 0.5)
        if verdict != expected:
            failures.append(f"{filename}: expected {expected}, got {verdict}")
            continue
        if needle and not any(needle in reason for reason in reasons):
            failures.append(f"{filename}: no reason contains {needle!r} (got {reasons})")
    if failures:
        print(f"SELF-TEST: FAIL ({len(SELF_TEST_CASES) - len(failures)}/{len(SELF_TEST_CASES)})")
        for failure in failures:
            print(f"  - {failure}")
        return 2
    print(f"SELF-TEST: PASS ({len(SELF_TEST_CASES)}/{len(SELF_TEST_CASES)})")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse the command line contract (see the skill's SKILL.md)."""
    parser = argparse.ArgumentParser(
        description="Classify a PR merge decision with a System One (Laya/Jev) model."
    )
    parser.add_argument("--repo", default="anushadpk/acers-web")
    parser.add_argument("--pr", type=int)
    parser.add_argument(
        "--backend",
        choices=["laya", "apimaster", "morphllm", "typesafe", "all"],
        default="laya",
    )
    parser.add_argument("--base-url")
    parser.add_argument("--api-key")
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--min-confidence", type=float, default=0.9)
    parser.add_argument("--max-risk", type=float, default=0.5)
    parser.add_argument("--max-state-chars", type=int, default=20000)
    parser.add_argument("--diff-chars", type=int, default=8000)
    parser.add_argument("--body-chars", type=int, default=2000)
    parser.add_argument("--review-chars", type=int, default=500)
    parser.add_argument("--state-file")
    parser.add_argument("--answers-file")
    parser.add_argument("--out")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true")
    output.add_argument("--text", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the classifier and return the exit code (0 MERGE, 1 HOLD, 2 error)."""
    args = parse_args(argv)

    if args.self_test:
        return run_self_test()
    if args.pr is None:
        print("ERROR: --pr is required", file=sys.stderr)
        return 2
    if args.execute and args.answers_file:
        print(
            "ERROR: refusing --execute with --answers-file (canned answers must never merge)",
            file=sys.stderr,
        )
        return 2
    if args.backend == "all" and (args.base_url or args.api_key or args.model):
        print(
            "ERROR: --base-url/--api-key/--model require a single --backend",
            file=sys.stderr,
        )
        return 2

    secrets: List[str] = [args.api_key] if args.api_key else []
    backends_result: Dict[str, Any] = {}

    try:
        if not args.state_file and not shutil.which("gh"):
            raise CtxError("gh CLI not found on PATH")

        state = load_json_file(Path(args.state_file)) if args.state_file else build_state(args)

        if args.dry_run:
            execution = {
                "executed": False,
                "command": " ".join(merge_command(args)),
                "result": "skipped_dry_run",
                "merge_commit": "",
                "timestamp_ist": timestamp_ist(),
            }
            emit(
                {
                    "dry_run": True,
                    "state": state,
                    "questions": QUESTIONS,
                    "execution": execution,
                    "timestamp_ist": timestamp_ist(),
                },
                args,
                secrets,
            )
            return 0

        if args.answers_file:
            response = load_json_file(Path(args.answers_file))
            answers = response.get("answers", {})
            backends_result["file"] = {
                "ok": True,
                "model": response.get("model", "answers-file"),
                "answers": answers,
            }
            verdict, reasons = evaluate_gate(answers, args.min_confidence, args.max_risk)
        elif args.backend == "all":
            responding, errors = call_all_backends(args, state, backends_result, secrets)
            if errors:
                raise CtxError("backend errors: " + "; ".join(errors))
            if not responding:
                raise CtxError("no backend responded")
            verdicts = [
                (name, evaluate_gate(answers, args.min_confidence, args.max_risk))
                for name, answers in responding
            ]
            if all(item_verdict == "MERGE" for _, (item_verdict, _) in verdicts):
                verdict, reasons = "MERGE", []
            else:
                verdict = "HOLD"
                reasons = [
                    f"{name}: {reason}"
                    for name, (_, item_reasons) in verdicts
                    for reason in item_reasons
                ]
        else:
            answers = call_single_backend(args, state, backends_result, secrets)
            verdict, reasons = evaluate_gate(answers, args.min_confidence, args.max_risk)

        execution: Dict[str, Any] = {
            "executed": False,
            "command": " ".join(merge_command(args)) if args.execute else "",
            "result": "not_requested",
            "merge_commit": "",
            "timestamp_ist": "",
        }
        if args.execute:
            if verdict == "MERGE":
                execution = run_merge(args, secrets)
                if execution["result"] == "failed":
                    output = build_output(args, verdict, reasons, backends_result, state, execution)
                    output["error"] = execution.pop("error", "merge failed")
                    emit(output, args, secrets)
                    return 2
            else:
                execution["result"] = "skipped_hold"

        emit(build_output(args, verdict, reasons, backends_result, state, execution), args, secrets)
        return 0 if verdict == "MERGE" else 1
    except CtxError as exc:
        output = {"error": str(exc)}
        if backends_result:
            output["backends"] = backends_result
        emit(output, args, secrets)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
