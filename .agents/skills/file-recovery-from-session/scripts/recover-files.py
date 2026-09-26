#!/usr/bin/env python3
##
# File Recovery from OpenCode Session
#
# Recovers files created during an OpenCode session by consuming base
# extractors for Tool: write and/or Tool: bash heredoc file writes.
#
# Tiers:
#   1. Invoke base extractor(s) as subprocess → get JSONL payloads
#   2. Write each payload's content to disk (original path or --output-dir)
#   3. Verify content integrity by comparing sizes

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def find_extract_script(name: str) -> Path:
    """Locate a base extractor script by skill directory name."""
    candidate = (
        Path(__file__).resolve().parent.parent.parent
        / name
        / "scripts"
    )
    # List scripts in that directory
    if candidate.exists():
        scripts = list(candidate.glob("extract-*.py"))
        if scripts:
            return scripts[0]

    print(
        f"Error: Extract script not found in {candidate}", file=sys.stderr
    )
    print(
        f"Ensure {name} is installed at "
        f".agents/skills/{name}/",
        file=sys.stderr,
    )
    sys.exit(3)


def extract_payloads(
    session_path: Path,
    file_pattern: str | None,
    mode: str,
) -> list[dict]:
    """Extract payloads using the appropriate base skill script(s)."""
    all_payloads: list[dict] = []

    if mode in ("write", "all"):
        script = find_extract_script("opencode-session-write-extractor")
        cmd = [sys.executable, str(script), "--session", str(session_path)]
        if file_pattern:
            cmd.extend(["--file-pattern", file_pattern])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode not in (0, 1):
            print(
                f"Write extractor failed (exit {result.returncode}):",
                file=sys.stderr,
            )
            print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)

        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    all_payloads.append(json.loads(line))
                except json.JSONDecodeError:
                    print(
                        f"Warning: Skipping invalid JSONL: {line[:80]}...",
                        file=sys.stderr,
                    )

    if mode in ("bash", "all"):
        script = find_extract_script("opencode-session-bash-write-extractor")
        cmd = [
            sys.executable, str(script), "--session", str(session_path),
            "--mode", "overwrite",
        ]
        if file_pattern:
            cmd.extend(["--file-pattern", file_pattern])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode not in (0, 1):
            print(
                f"Bash write extractor failed (exit {result.returncode}):",
                file=sys.stderr,
            )
            print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)

        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    all_payloads.append(json.loads(line))
                except json.JSONDecodeError:
                    print(
                        f"Warning: Skipping invalid JSONL: {line[:80]}...",
                        file=sys.stderr,
                    )

    return all_payloads


def write_payload(
    payload: dict,
    output_dir: Path | None,
    dry_run: bool,
) -> dict:
    """Write a single payload's content to disk. Returns status dict."""
    file_path = Path(payload["filePath"])
    content = payload.get("content", "")

    if output_dir:
        target = output_dir / file_path.name
    else:
        target = file_path

    status = {
        "filePath": str(target),
        "contentSize": len(content),
        "written": False,
        "verified": False,
        "error": None,
    }

    if dry_run:
        return status

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        status["error"] = f"Cannot create directory: {exc}"
        return status

    try:
        target.write_text(content, encoding="utf-8")
        status["written"] = True
    except OSError as exc:
        status["error"] = f"Write failed: {exc}"
        return status

    try:
        actual_size = target.stat().st_size
        expected_size = len(content.encode("utf-8"))
        status["verified"] = actual_size == expected_size
        if not status["verified"]:
            status["error"] = (
                f"Size mismatch: expected {expected_size}, "
                f"got {actual_size}"
            )
    except OSError as exc:
        status["error"] = f"Verification failed: {exc}"

    return status


def print_summary(results: list[dict], dry_run: bool):
    """Print a formatted recovery summary."""
    total = len(results)
    written = sum(1 for r in results if r["written"])
    verified = sum(1 for r in results if r["verified"])
    failed = sum(1 for r in results if r["error"])

    if dry_run:
        print("\n=== DRY RUN SUMMARY ===\n")
        for r in results:
            print(f"  Would write: {r['filePath']}")
            print(f"    Size: {r['contentSize']} chars")
        print(f"\nTotal: {total} file(s) to recover")
        return

    print("\n=== RECOVERY SUMMARY ===\n")
    for r in results:
        mark = "✓" if r["verified"] else "✗" if r["error"] else "?"
        print(f"  {mark} {r['filePath']}")
        print(f"    Size: {r['contentSize']} chars")

    print(f"\nTotal: {total} | Written: {written} | "
          f"Verified: {verified} | Failed: {failed}")


def main():
    parser = argparse.ArgumentParser(
        description="Recover files from opencode session exports"
    )
    parser.add_argument(
        "--session",
        type=Path,
        required=True,
        help="Path to opencode session export (.md)",
    )
    parser.add_argument(
        "--file-pattern",
        help="Glob to filter write payloads by filePath",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Redirect all recovered files to this directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview files to recover without writing",
    )
    parser.add_argument(
        "--mode",
        choices=["write", "bash", "all"],
        default="all",
        help="Source of file writes: 'write' (Tool: write), "
        "'bash' (bash heredocs), or 'all' (both, default)",
    )

    args = parser.parse_args()

    if not args.session.exists():
        print(
            f"Session file not found: {args.session}", file=sys.stderr
        )
        sys.exit(3)

    if args.dry_run:
        print(
            f"[DRY RUN] Would extract payloads from: {args.session} "
            f"(mode: {args.mode})",
            file=sys.stderr,
        )

    payloads = extract_payloads(args.session, args.file_pattern, args.mode)

    if not payloads:
        sys.exit(2)

    if args.output_dir and not args.dry_run:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for payload in payloads:
        status = write_payload(payload, args.output_dir, args.dry_run)
        results.append(status)

    print_summary(results, args.dry_run)

    failed_count = sum(1 for r in results if r["error"])
    if failed_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
