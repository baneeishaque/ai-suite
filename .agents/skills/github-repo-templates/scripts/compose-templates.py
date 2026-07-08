#!/usr/bin/env python3
"""C1 composer: generate all GitHub community standard templates.

Calls base skills B1-B6, B12-B17 to produce a complete template set.
"""
import argparse
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2]

TEMPLATE_SCRIPTS = {
    "gitignore": "github-gitignore-template/scripts/write-gitignore-template.py",
    "code_of_conduct": "github-code-of-conduct/scripts/write-code-of-conduct.py",
    "contributing": "github-contributing-guide/scripts/write-contributing-guide.py",
    "security": "github-security-policy/scripts/write-security-policy.py",
    "support": "github-support-docs/scripts/write-support-docs.py",
    "readme": "github-readme-template/scripts/write-readme-template.py",
    "bug_template": "github-issue-template-bug/scripts/write-bug-template.py",
    "feature_template": "github-issue-template-feature/scripts/write-feature-template.py",
    "doc_template": "github-issue-template-documentation/scripts/write-documentation-template.py",
    "pr_template": "github-pr-template/scripts/write-pr-template.py",
}

DEFAULT_OUTPUTS = {
    "gitignore": ".gitignore",
    "code_of_conduct": "CODE_OF_CONDUCT.md",
    "contributing": "CONTRIBUTING.md",
    "security": "SECURITY.md",
    "support": "SUPPORT.md",
    "readme": "README.md",
    "bug_template": ".github/ISSUE_TEMPLATE/bug_report.md",
    "feature_template": ".github/ISSUE_TEMPLATE/feature_request.md",
    "doc_template": ".github/ISSUE_TEMPLATE/documentation.md",
    "pr_template": ".github/PULL_REQUEST_TEMPLATE.md",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate all GitHub community standard templates"
    )
    parser.add_argument(
        "--owner", default="owner", help="Repository owner"
    )
    parser.add_argument(
        "--repo-name", default="repo", help="Repository name"
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory (default: current)",
    )
    parser.add_argument(
        "--language",
        default="generic",
        choices=["python", "node", "generic"],
        help="Project language for .gitignore",
    )
    args = parser.parse_args()

    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    results = []

    for key, rel_path in TEMPLATE_SCRIPTS.items():
        script = SKILLS_DIR / rel_path
        if not script.exists():
            results.append({"template": key, "status": "skipped", "reason": f"script not found: {script}"})
            continue

        output_path = out / DEFAULT_OUTPUTS[key]
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable, str(script),
            "--output", str(output_path),
        ]
        if key == "gitignore":
            cmd.extend(["--language", args.language])
        elif key in ("contributing", "support"):
            cmd.extend(["--owner", args.owner, "--repo-name", args.repo_name])
        elif key == "readme":
            cmd.extend(["--repo-name", args.repo_name])

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            results.append({"template": key, "status": "created", "path": str(output_path)})
        except subprocess.CalledProcessError as e:
            results.append({"template": key, "status": "error", "stderr": e.stderr})

    import json
    json.dump(results, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
