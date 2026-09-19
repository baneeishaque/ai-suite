#!/usr/bin/env python3
"""Run the full 3-step markdown lint fix pipeline on one or more .md files.

Usage:
    python3 fix-markdown-pipeline.py <file.md> [<file.md> ...]

Pipeline:
    1. markdownlint-cli2 --fix  (auto-fix what it can)
    2. Companion scripts in §2.1 order  (fix what --fix cannot)
    3. markdownlint-cli2 audit  (verify clean; exit non-zero if issues remain)

Exit status:
    0  — all files lint-clean
    1  — one or more files have remaining lint issues
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

SCRIPTS_ORDER = [
    ("fix-table-separators.py", []),
    ("fix-fenced-code-language.py", []),
    ("fix-container-fence.py", []),
    ("wrap-long-lines.py", ["--max", "120"]),
    ("fix-emphasis-as-heading.py", []),
    ("fix-list-style.py", []),
    ("fix-heading-spacing.py", []),
]


def run(args, label):
    print(f"[{label}] {' '.join(args)}")
    r = subprocess.run(args, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip(), file=sys.stderr)
    return r


def main():
    files = sys.argv[1:]
    if not files:
        print("Usage: python3 fix-markdown-pipeline.py <file.md> [<file.md> ...]")
        sys.exit(1)

    total_ok = True

    print("=" * 60)
    print("STEP 1: markdownlint-cli2 --fix")
    print("=" * 60)
    r = run(["markdownlint-cli2", "--fix"] + files, "step-1")
    if r.returncode != 0:
        print("[INFO] --fix finished (non-zero exit is normal when unfixable issues remain)")

    print("\n" + "=" * 60)
    print("STEP 2: Companion scripts")
    print("=" * 60)
    for script_name, extra_args in SCRIPTS_ORDER:
        script_path = SCRIPTS_DIR / script_name
        if not script_path.exists():
            print(f"  [SKIP] {script_name} — not found at {script_path}")
            continue
        r = run([sys.executable, str(script_path)] + extra_args + files, f"  {script_name}")
        if r.returncode != 0:
            print(f"  [WARN] {script_name} exited with code {r.returncode}")

    print("\n" + "=" * 60)
    print("STEP 3: Final audit")
    print("=" * 60)
    r = run(["markdownlint-cli2"] + files, "audit")
    if r.returncode == 0:
        print("\nAll files lint-clean.")
        sys.exit(0)
    else:
        print("\nRemaining lint issues found. See output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
