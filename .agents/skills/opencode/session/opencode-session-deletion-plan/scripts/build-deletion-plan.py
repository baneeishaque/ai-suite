#!/usr/bin/env python3
"""build-deletion-plan.py — render a session-deletion implementation plan.

Consumes a JSON spec and the sibling `plan.template` and emits the versioned
markdown plan the `opencode-session-deletion` composer executes.

Tier: 1 (Python 3.12+) — per scripting-language-selection-rules.md §3.
Stdlib only; deterministic; refuses to overwrite an existing plan unless
`--overwrite` is supplied.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = SCRIPT_DIR / "plan.template"

MATCH_MODES = {"case_insensitive", "exact"}
TOTAL_KEYS = (
    "SESSION_ID",
    "AUTHORING_SESSION_ID",
    "TARGET_TITLE",
    "DATE",
    "VERSION",
    "INVENTORY_ROWS",
    "MARKER_SECTION",
    "COMMIT_ROSTER",
    "GAP_CLOSURE",
    "RETIRE_ITEMS",
)


def fail(message: str, code: int = 1) -> int:
    print(f"error: {message}", file=sys.stderr)
    return code


def code_span(value: str) -> str:
    """Render a markdown inline code span that survives embedded backticks."""
    if "`" not in value:
        return f"`{value}`"
    if "``" in value:
        return f"`{value}`"
    return f"`` {value} ``"


def cell(value: str) -> str:
    """Escape a value for use inside a markdown table cell."""
    return code_span(str(value)).replace("|", "\\|")


def join_paths(paths: list[str]) -> str:
    if not paths:
        return "—"
    return "<br>".join(code_span(p).replace("|", "\\|") for p in paths)


def render_inventory_rows(inventory: dict) -> str:
    database = bool(inventory.get("database"))
    rows = [
        f"| Database record | {1 if database else 0} | "
        f"{code_span('opencode session list record') if database else '—'} |"
    ]
    for label, key in (
        ("Logger logs", "logs"),
        ("Scratch files", "scratch"),
        ("Docs artifacts", "docs"),
    ):
        paths = [str(p) for p in inventory.get(key) or []]
        rows.append(f"| {label} | {len(paths)} | {join_paths(paths)} |")
    return "\n".join(rows)


def render_marker_section(markers: list[dict], markers_none: bool) -> str:
    if markers_none:
        return (
            "**Markers: none** — the authoring session has no protected work; "
            "the executor does not need a survival baseline."
        )
    rows = [
        "| # | Path | Pattern | Match mode | Verification command |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for index, marker in enumerate(markers, start=1):
        path = str(marker["path"])
        pattern = str(marker["pattern"])
        mode = str(marker["match_mode"])
        flag = "-Fni" if mode == "case_insensitive" else "-Fn"
        command = f'grep {flag} -- "{pattern}" "{path}"'
        rows.append(
            f"| {index} | {cell(path)} | {cell(pattern)} | {mode} | "
            f"{code_span(command)} |"
        )
    return "\n".join(rows)


def render_commit_roster(roster: list[dict]) -> str:
    if not roster:
        return "No commit roster supplied."
    rows = [
        "| # | Commit | Subject |",
        "| :--- | :--- | :--- |",
    ]
    for index, entry in enumerate(roster, start=1):
        subject = str(entry.get("subject", "")).replace("|", "\\|")
        rows.append(f"| {index} | {cell(entry['sha'])} | {subject} |")
    return "\n".join(rows)


def render_gap_closure(gate: dict) -> str:
    pass_label = str(gate.get("pass", "—"))
    verdict = str(gate.get("verdict", "")).replace("|", "\\|")
    register = gate.get("register_path")
    register_cell = cell(str(register)) if register else "local-only / recovered from Trash"
    return (
        "| Pass | Verdict | Register |\n"
        "| :--- | :--- | :--- |\n"
        f"| {pass_label} | {verdict} | {register_cell} |\n\n"
        "Deletion is BLOCKED until this gate reports zero open gaps; "
        "`--execute` requires `--gap-closure-cleared`."
    )


def render_retire_items(inventory: dict) -> str:
    docs = [str(p) for p in inventory.get("docs") or []]
    lines = [f"- {code_span(p)}" for p in docs]
    lines.append("- This plan file last, after Phase 2 verification.")
    return "\n".join(lines)


def validate_spec(spec: dict) -> list[str]:
    errors: list[str] = []
    for key in ("date", "session_id"):
        if not str(spec.get(key, "")).strip():
            errors.append(f"`{key}` is required")
    if spec.get("date") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(spec["date"])):
        errors.append("`date` must be YYYY-MM-DD")
    markers = spec.get("markers") or []
    markers_none = bool(spec.get("markers_none"))
    if markers and markers_none:
        errors.append("`markers` and `markers_none: true` are mutually exclusive")
    if not markers and not markers_none:
        errors.append("supply `markers` or set `markers_none: true` explicitly")
    for index, marker in enumerate(markers, start=1):
        for key in ("path", "pattern", "match_mode"):
            if not str(marker.get(key, "")).strip():
                errors.append(f"marker {index}: `{key}` is required")
        mode = str(marker.get("match_mode", ""))
        if mode and mode not in MATCH_MODES:
            errors.append(
                f"marker {index}: `match_mode` must be one of {sorted(MATCH_MODES)}"
            )
    for index, entry in enumerate(spec.get("commit_roster") or [], start=1):
        if not str(entry.get("sha", "")).strip():
            errors.append(f"commit_roster {index}: `sha` is required")
    gate = spec.get("gap_closure") or {}
    if not str(gate.get("verdict", "")).strip():
        errors.append("`gap_closure.verdict` is required")
    return errors


def default_output(spec: dict, docs_dir: Path, version: int) -> Path:
    session = str(spec["session_id"])
    if session.startswith("ses_"):
        session = session[4:]
    slug = str(spec.get("session_slug") or "session-deletion")
    return docs_dir / (
        f"{spec['date']}_{session}_{slug}_implementation-plan_v{version}.md"
    )


def render(spec: dict, version: int, template: str) -> str:
    context = {
        "SESSION_ID": str(spec["session_id"]),
        "AUTHORING_SESSION_ID": str(spec.get("authoring_session_id") or "—"),
        "TARGET_TITLE": str(spec.get("target_title") or "—"),
        "DATE": str(spec["date"]),
        "VERSION": str(version),
        "INVENTORY_ROWS": render_inventory_rows(spec.get("inventory") or {}),
        "MARKER_SECTION": render_marker_section(
            spec.get("markers") or [], bool(spec.get("markers_none"))
        ),
        "COMMIT_ROSTER": render_commit_roster(spec.get("commit_roster") or []),
        "GAP_CLOSURE": render_gap_closure(spec.get("gap_closure") or {}),
        "RETIRE_ITEMS": render_retire_items(spec.get("inventory") or {}),
    }
    rendered = template
    for key, value in context.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", rendered)
    if leftover:
        raise ValueError(f"unresolved template placeholders: {sorted(set(leftover))}")
    return rendered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="JSON spec file")
    parser.add_argument("--output", help="output plan path (default: derived under --docs-dir)")
    parser.add_argument("--docs-dir", default="docs", help="docs directory for the default name")
    parser.add_argument("--version", type=int, default=1, help="plan version (default: 1)")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing output file")
    parser.add_argument("--dry-run", action="store_true", help="render and validate; write nothing")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    if not TEMPLATE_PATH.is_file():
        return fail(f"template not found: {TEMPLATE_PATH}", 2)
    spec_path = Path(args.spec).expanduser()
    if not spec_path.is_file():
        return fail(f"spec not found: {spec_path}", 2)
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return fail(f"invalid JSON spec: {exc}", 2)
    if not isinstance(spec, dict):
        return fail("spec must be a JSON object", 2)

    errors = validate_spec(spec)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    output = (
        Path(args.output).expanduser()
        if args.output
        else default_output(spec, Path(args.docs_dir).expanduser(), args.version)
    )
    if output.exists() and not args.overwrite and not args.dry_run:
        return fail(f"output already exists (use --overwrite): {output}", 3)

    try:
        rendered = render(spec, args.version, TEMPLATE_PATH.read_text(encoding="utf-8"))
    except ValueError as exc:
        return fail(str(exc), 1)

    result = {
        "mode": "dry-run" if args.dry_run else "build",
        "spec": str(spec_path),
        "output": str(output),
        "version": args.version,
        "markers": len(spec.get("markers") or []),
        "markers_none": bool(spec.get("markers_none")),
        "commit_roster": len(spec.get("commit_roster") or []),
        "bytes": len(rendered.encode("utf-8")),
    }
    if not args.dry_run:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"{result['mode']}: {output} "
            f"({result['bytes']}B, {result['markers']} markers, "
            f"{result['commit_roster']} commits)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
