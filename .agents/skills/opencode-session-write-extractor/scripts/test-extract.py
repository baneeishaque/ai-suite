#!/usr/bin/env python3
"""Test the opencode-session-write-extractor against known session data.

Creates mock session markdown with Tool: write blocks, runs the extractor,
and verifies output correctness.

Usage:
    python3 scripts/test-extract.py

Exits 0 on all tests passing, 1 on any failure.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
EXTRACTOR = THIS_DIR / "extract-session-writes.py"
PASS = 0
FAIL = 0


def run_extractor(
    session_path: Path,
    file_pattern: str | None = None,
) -> subprocess.CompletedProcess:
    """Run extractor against a session file, return subprocess result."""
    cmd = [sys.executable, str(EXTRACTOR), "--session", str(session_path)]
    if file_pattern:
        cmd.extend(["--file-pattern", file_pattern])
    return subprocess.run(cmd, capture_output=True, text=True)


def check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {name} {detail}", file=sys.stderr)


def make_session(blocks: list[dict]) -> Path:
    """Create a temporary session markdown file with Tool: write blocks."""
    lines = ["# Test Session Export\n"]
    for b in blocks:
        lines.append("**Tool: write**\n")
        lines.append("\n")
        lines.append("**Input:**\n")
        lines.append("```json\n")
        lines.append(json.dumps(b, indent=2) + "\n")
        lines.append("```\n")
        lines.append("\n")
        lines.append("**Output:**\n")
        lines.append("```\n")
        lines.append("Write applied successfully.\n")
        lines.append("```\n")
        lines.append("\n")
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    )
    f.writelines(lines)
    f.close()
    return Path(f.name)


def test_empty_session():
    """Session with no Tool: write blocks → exit 1."""
    content = "# No tools here\n\nSome text.\n"
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    )
    f.write(content)
    f.close()
    path = Path(f.name)
    try:
        result = run_extractor(path)
        check("empty session exits 1", result.returncode == 1)
        check("empty session stderr says no payloads",
              "No write payloads" in result.stderr)
    finally:
        path.unlink()


def test_single_write():
    """Single Tool: write block → one payload extracted."""
    blocks = [{"filePath": "/tmp/test-file.txt", "content": "hello world"}]
    session = make_session(blocks)
    try:
        result = run_extractor(session)
        check("single write exit 0", result.returncode == 0)
        payloads = [json.loads(l) for l in result.stdout.strip().splitlines()]
        check("single write → 1 payload", len(payloads) == 1)
        check("filePath correct", payloads[0]["filePath"] == "/tmp/test-file.txt")
        check("content correct", payloads[0]["content"] == "hello world")
    finally:
        session.unlink()


def test_multiple_writes():
    """Multiple Tool: write blocks → all extracted."""
    blocks = [
        {"filePath": "/tmp/a.txt", "content": "aaa"},
        {"filePath": "/tmp/b.txt", "content": "bbb"},
        {"filePath": "/tmp/c.txt", "content": "ccc"},
    ]
    session = make_session(blocks)
    try:
        result = run_extractor(session)
        check("multiple writes exit 0", result.returncode == 0)
        payloads = [json.loads(l) for l in result.stdout.strip().splitlines()]
        check("multiple writes → 3 payloads", len(payloads) == 3)
        for i, b in enumerate(blocks):
            check(f"payload {i} filePath", payloads[i]["filePath"] == b["filePath"])
            check(f"payload {i} content", payloads[i]["content"] == b["content"])
    finally:
        session.unlink()


def test_file_pattern():
    """--file-pattern filter narrows results."""
    blocks = [
        {"filePath": "/tmp/foo.md", "content": "md"},
        {"filePath": "/tmp/bar.py", "content": "py"},
        {"filePath": "/tmp/baz.md", "content": "md2"},
    ]
    session = make_session(blocks)
    try:
        result = run_extractor(session, file_pattern="*.md")
        check("file-pattern exit 0", result.returncode == 0)
        payloads = [json.loads(l) for l in result.stdout.strip().splitlines()]
        check("file-pattern → 2 payloads", len(payloads) == 2)
        for p in payloads:
            check(f"file-pattern {p['filePath']} ends .md",
                  p["filePath"].endswith(".md"))
    finally:
        session.unlink()


def test_missing_content_field():
    """Block missing 'content' field is skipped."""
    blocks = [{"filePath": "/tmp/bad.json"}]
    session = make_session(blocks)
    try:
        result = run_extractor(session)
        check("missing content exits 1", result.returncode == 1)
        check("missing content warns", "Skipping payload" in result.stderr)
    finally:
        session.unlink()


def test_content_with_unicode():
    """Content with unicode characters is preserved."""
    content = "Hello 世界\n🔥 emoji\nline 3"
    blocks = [{"filePath": "/tmp/unicode.txt", "content": content}]
    session = make_session(blocks)
    try:
        result = run_extractor(session)
        check("unicode exit 0", result.returncode == 0)
        payloads = [json.loads(l) for l in result.stdout.strip().splitlines()]
        check("unicode content preserved", payloads[0]["content"] == content)
    finally:
        session.unlink()


def test_file_not_found():
    """Non-existent session file → exit 3."""
    result = run_extractor(Path("/tmp/nonexistent-12345.md"))
    check("not found exit 3", result.returncode == 3)
    check("not found stderr", "not found" in result.stderr.lower())


def main():
    print("Testing opencode-session-write-extractor...", file=sys.stderr)

    test_empty_session()
    test_single_write()
    test_multiple_writes()
    test_file_pattern()
    test_missing_content_field()
    test_content_with_unicode()
    test_file_not_found()

    total = PASS + FAIL
    print(f"\nResults: {PASS} passed, {FAIL} failed, {total} total",
          file=sys.stderr)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
