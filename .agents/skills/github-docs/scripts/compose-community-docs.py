#!/usr/bin/env python3
"""C5 composer: generate GitHub community documentation files.

Calls B13 (code-of-conduct), B14 (contributing), B15 (security), B16 (support).
"""
import argparse
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2]

DOC_SCRIPTS = {
    "code_of_conduct": "github-code-of-conduct/scripts/write-code-of-conduct.py",
    "contributing": "github-contributing-guide/scripts/write-contributing-guide.py",
    "security": "github-security-policy/scripts/write-security-policy.py",
    "support": "github-support-docs/scripts/write-support-docs.py",
}

DEFAULT_OUTPUTS = {
    "code_of_conduct": "CODE_OF_CONDUCT.md",
    "contributing": "CONTRIBUTING.md",
    "security": "SECURITY.md",
    "support": "SUPPORT.md",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate GitHub community documentation files"
    )
    parser.add_argument(
        "--owner", default="owner", help="Repository owner"
    )
    parser.add_argument(
        "--repo-name", default="repo", help="Repository name"
    )
    parser.add_argument(
        "--output-dir", default=".", help="Output directory"
    )
    args = parser.parse_args()

    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    results = []

    for key, rel_path in DOC_SCRIPTS.items():
        script = SKILLS_DIR / rel_path
        if not script.exists():
            results.append({"doc": key, "status": "skipped"})
            continue

        output_path = out / DEFAULT_OUTPUTS[key]
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [sys.executable, str(script), "--output", str(output_path)]
        if key in ("contributing", "support"):
            cmd.extend(["--owner", args.owner, "--repo-name", args.repo_name])
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            results.append({"doc": key, "status": "created", "path": str(output_path)})
        except subprocess.CalledProcessError as e:
            results.append({"doc": key, "status": "error", "stderr": e.stderr})

    import json
    json.dump(results, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
