#!/usr/bin/env python3
"""C2 composer: generate CI lint workflows for GitHub Actions.

Calls B7 (github-ci-markdown-lint) and B8 (github-ci-python-lint).
"""
import argparse
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2]

LINT_SCRIPTS = {
    "markdown_lint": "github-ci-markdown-lint/scripts/write-markdown-lint-job.py",
    "python_lint": "github-ci-python-lint/scripts/write-python-lint-job.py",
}

DEFAULT_OUTPUTS = {
    "markdown_lint": ".github/workflows/markdown-lint.yml",
    "python_lint": ".github/workflows/python-lint.yml",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate CI lint workflows for GitHub Actions"
    )
    parser.add_argument(
        "--output-dir", default=".", help="Output directory"
    )
    args = parser.parse_args()

    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    results = []

    for key, rel_path in LINT_SCRIPTS.items():
        script = SKILLS_DIR / rel_path
        if not script.exists():
            results.append({"workflow": key, "status": "skipped"})
            continue

        output_path = out / DEFAULT_OUTPUTS[key]
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [sys.executable, str(script), "--output", str(output_path)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            results.append({"workflow": key, "status": "created", "path": str(output_path)})
        except subprocess.CalledProcessError as e:
            results.append({"workflow": key, "status": "error", "stderr": e.stderr})

    import json
    json.dump(results, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
