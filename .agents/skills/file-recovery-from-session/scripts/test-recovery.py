#!/usr/bin/env python3
"""Test the file-recovery-from-session composer.

Creates mock session files with Tool: write blocks, runs the recovery
composer in various modes, and verifies output correctness.

Usage:
    python3 scripts/test-recovery.py

Exits 0 on all tests passing, 1 on any failure.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
RECOVER = THIS_DIR / "recover-files.py"
PASS = 0
FAIL = 0


def run_recover(
    session_path: Path,
    mode: str = "write",
    file_pattern: str | None = None,
    output_dir: Path | None = None,
    dry_run: bool = False,
) -> subprocess.CompletedProcess:
    """Run recover-files.py and return subprocess result."""
    cmd = [
        sys.executable,
        str(RECOVER),
        "--session", str(session_path),
        "--mode", mode,
    ]
    if file_pattern:
        cmd.extend(["--file-pattern", file_pattern])
    if output_dir:
        cmd.extend(["--output-dir", str(output_dir)])
    if dry_run:
        cmd.append("--dry-run")
    return subprocess.run(cmd, capture_output=True, text=True)


def check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {name} {detail}", file=sys.stderr)


def make_write_session(blocks: list[dict]) -> Path:
    """Create a temp session file with Tool: write blocks."""
    lines = ["# Test Session\n"]
    for b in blocks:
        lines.append("**Tool: write**\n\n**Input:**\n```json\n")
        lines.append(json.dumps(b, indent=2) + "\n")
        lines.append("```\n\n**Output:**\n```\nWrite applied.\n```\n\n")
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    )
    f.writelines(lines)
    f.close()
    return Path(f.name)


def test_dry_run():
    """--dry-run lists files without writing."""
    block = {"filePath": "/tmp/test-dry-run.txt", "content": "should not write"}
    session = make_write_session([block])
    try:
        result = run_recover(session, dry_run=True)
        check("dry-run exit 0", result.returncode == 0)
        check("dry-run says DRY RUN", "DRY RUN" in result.stderr.upper()
              or "DRY RUN" in result.stdout)
        check("dry-run did not create file",
              not Path("/tmp/test-dry-run.txt").exists())
    finally:
        session.unlink()
        Path("/tmp/test-dry-run.txt").unlink(missing_ok=True)


def test_output_dir():
    """--output-dir recovers files to the specified directory."""
    block = {"filePath": "/tmp/original-path.txt", "content": "redirected content"}
    session = make_write_session([block])
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir)
        result = run_recover(session, output_dir=out)
        check("output-dir exit 0", result.returncode == 0)
        target = out / "original-path.txt"
        check("output-dir file exists", target.exists())
        check("output-dir content matches", target.read_text() == "redirected content")
        check("output-dir did NOT write to original path",
              not Path("/tmp/original-path.txt").exists())
    # Clean up if the file somehow exists
    Path("/tmp/original-path.txt").unlink(missing_ok=True)


def test_verification():
    """Recovered file has correct content size."""
    content = "hello\nworld\n" * 100
    block = {"filePath": "/tmp/test-verify.tmp", "content": content}
    session = make_write_session([block])
    try:
        result = run_recover(session)
        check("verify exit 0", result.returncode == 0)
        written = Path("/tmp/test-verify.tmp")
        check("verify file exists", written.exists())
        check("verify size matches",
              written.stat().st_size == len(content.encode("utf-8")))
        check("verify content matches", written.read_text() == content)
    finally:
        session.unlink()
        Path("/tmp/test-verify.tmp").unlink(missing_ok=True)


def test_empty_session():
    """Session with no write blocks → exit 2."""
    content = "# No writes here\n"
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    )
    f.write(content)
    f.close()
    path = Path(f.name)
    try:
        result = run_recover(path)
        check("empty session exit 2", result.returncode == 2)
    finally:
        path.unlink()


def test_file_pattern_filter():
    """--file-pattern narrows recovery scope."""
    blocks = [
        {"filePath": "/tmp/include.md", "content": "md content"},
        {"filePath": "/tmp/exclude.py", "content": "py content"},
    ]
    session = make_write_session(blocks)
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir)
        result = run_recover(session, file_pattern="*.md", output_dir=out)
        check("file-pattern exit 0", result.returncode == 0)
        recovered = list(out.iterdir())
        check("file-pattern only 1 file", len(recovered) == 1)
        check("file-pattern correct file", recovered[0].name == "include.md")
    # Clean up
    for p in ["/tmp/include.md", "/tmp/exclude.py"]:
        Path(p).unlink(missing_ok=True)


def test_session_not_found():
    """Non-existent session → exit 3."""
    result = run_recover(Path("/tmp/nonexistent-12345.md"))
    check("not found exit 3", result.returncode == 3)
    check("not found stderr", "not found" in result.stderr.lower())


def main():
    print("Testing file-recovery-from-session...", file=sys.stderr)

    test_dry_run()
    test_output_dir()
    test_verification()
    test_empty_session()
    test_file_pattern_filter()
    test_session_not_found()

    total = PASS + FAIL
    print(f"\nResults: {PASS} passed, {FAIL} failed, {total} total",
          file=sys.stderr)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
