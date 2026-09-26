#!/usr/bin/env python3
"""
Apply Tool: edit payloads from an OpenCode session export to on-disk files.

Reads edit payloads via opencode-session-edit-extractor, then applies
oldString -> newString replacement to each target file.

Tiers:
  1. Invoke base edit extractor as subprocess -> JSONL payloads
  2. Read each target file, perform replacement, write back
  3. Verify oldString was found and replaced (count occurrences)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def find_extract_script() -> Path:
    """Locate opencode-session-edit-extractor's extract script."""
    candidate = (
        Path(__file__).resolve().parent.parent.parent
        / "opencode-session-edit-extractor"
        / "scripts"
        / "extract-session-edits.py"
    )
    if candidate.exists():
        return candidate

    print(
        f"Error: Extract script not found at {candidate}",
        file=sys.stderr,
    )
    print(
        "Ensure opencode-session-edit-extractor is installed at "
        ".agents/skills/opencode-session-edit-extractor/",
        file=sys.stderr,
    )
    sys.exit(3)


def extract_edits(
    session_path: Path, file_pattern: str | None
) -> list[dict]:
    """Extract edit payloads using the base skill script."""
    script = find_extract_script()
    cmd = [
        sys.executable,
        str(script),
        "--session",
        str(session_path),
    ]
    if file_pattern:
        cmd.extend(["--file-pattern", file_pattern])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 1:
        print("No edit payloads found.", file=sys.stderr)
        return []
    elif result.returncode != 0:
        print(
            f"Extraction failed (exit {result.returncode}):",
            file=sys.stderr,
        )
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    payloads: list[dict] = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payloads.append(json.loads(line))
        except json.JSONDecodeError:
            print(
                f"Warning: Skipping invalid JSONL line: {line[:80]}...",
                file=sys.stderr,
            )

    return payloads


def apply_edit(
    payload: dict,
    output_dir: Path | None,
    dry_run: bool,
    chained: dict[str, str] | None = None,
) -> tuple[dict, dict[str, str] | None]:
    """Apply a single edit payload to the target file. Returns (status, chained).

    In --output-dir mode, edits to the same file chain: each edit reads from
    the previous output (or original source for the first edit). The caller
    passes and receives a `chained` dict mapping file basename to content.
    """
    file_path = Path(payload["filePath"])
    old_string = payload.get("oldString", "")
    new_string = payload.get("newString", "")

    if output_dir:
        target = output_dir / file_path.name
    else:
        target = file_path

    status = {
        "filePath": str(target),
        "editSize": len(old_string) + len(new_string),
        "applied": False,
        "verified": False,
        "occurrences": 0,
        "error": None,
    }

    if dry_run:
        return status, chained

    # Determine source: chained content (output-dir mode, same file edited
    # previously), existing target (output-dir mode, previous write), or
    # original source file
    if chained is not None and file_path.name in chained:
        content = chained[file_path.name]
    elif output_dir and target.exists():
        content = target.read_text(encoding="utf-8")
    else:
        if not file_path.exists():
            status["error"] = f"Source file does not exist: {file_path}"
            return status, chained
        content = file_path.read_text(encoding="utf-8")

    if old_string not in content:
        status["error"] = f"oldString not found in {file_path}"
        return status, chained

    occurrences = content.count(old_string)
    status["occurrences"] = occurrences
    new_content = content.replace(old_string, new_string)

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(new_content, encoding="utf-8")
        status["applied"] = True
    except OSError as exc:
        status["error"] = f"Write failed: {exc}"
        return status, chained

    if new_string in new_content:
        status["verified"] = True

    # In output-dir mode, track chained content for subsequent edits
    if output_dir and chained is not None:
        chained[file_path.name] = new_content

    return status, chained


def print_summary(results: list[dict], dry_run: bool):
    """Print a formatted edit application summary."""
    total = len(results)
    applied = sum(1 for r in results if r["applied"])
    verified = sum(1 for r in results if r["verified"])
    failed = sum(1 for r in results if r["error"])

    if dry_run:
        print("\n=== DRY RUN SUMMARY ===\n")
        for r in results:
            print(f"  Would edit: {r['filePath']}")
            print(f"    Payload size: {r['editSize']} chars")
        print(f"\nTotal: {total} edit(s) to apply")
        return

    print("\n=== EDIT SUMMARY ===\n")
    for r in results:
        mark = "✓" if r["verified"] else "✗" if r["error"] else "?"
        occ = f" ({r['occurrences']} occurrence(s))" if r["occurrences"] else ""
        print(f"  {mark} {r['filePath']}{occ}")

    print(f"\nTotal: {total} | Applied: {applied} | "
          f"Verified: {verified} | Failed: {failed}")


def main():
    parser = argparse.ArgumentParser(
        description="Apply Tool: edit payloads from opencode session exports"
    )
    parser.add_argument(
        "--session",
        type=Path,
        required=True,
        help="Path to opencode session export (.md)",
    )
    parser.add_argument(
        "--file-pattern",
        help="Glob to filter edit payloads by filePath",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Write modified copies to this directory (originals unchanged)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview edits to apply without modifying files",
    )

    args = parser.parse_args()

    if not args.session.exists():
        print(
            f"Session file not found: {args.session}", file=sys.stderr
        )
        sys.exit(3)

    if args.dry_run:
        print(
            f"[DRY RUN] Would extract edits from: {args.session}",
            file=sys.stderr,
        )

    payloads = extract_edits(args.session, args.file_pattern)

    if not payloads:
        sys.exit(2)

    if args.output_dir and not args.dry_run:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    chained = {} if args.output_dir else None
    results = []
    for payload in payloads:
        status, chained = apply_edit(
            payload, args.output_dir, args.dry_run, chained
        )
        results.append(status)

    print_summary(results, args.dry_run)

    failed_count = sum(1 for r in results if r["error"])
    if failed_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
