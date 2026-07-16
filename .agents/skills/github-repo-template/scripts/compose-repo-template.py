#!/usr/bin/env python3
"""C6 composer: generate the full repository template set.

Calls C1 (github-repo-templates), C5 (github-docs), and B18-B19
to produce a complete repository template with community standards,
workflows, and MaC maturity markers.
"""
import argparse
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2]

COMPOSER_SCRIPTS = {
    "templates": "github-repo-templates/scripts/compose-templates.py",
    "community_docs": "github-docs/scripts/compose-community-docs.py",
    "repo_structure": "github-repo-structure/scripts/write-repo-structure.py",
    "maturity_markers": "github-maturity-model-maC/scripts/write-maturity-markers.py",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the full repository template"
    )
    parser.add_argument("--owner", default="owner")
    parser.add_argument("--repo-name", default="repo")
    parser.add_argument(
        "--output-dir", default=".", help="Output directory"
    )
    parser.add_argument(
        "--maturity",
        default="experimental",
        choices=["experimental", "beta", "stable", "deprecated"],
        help="Project maturity level",
    )
    args = parser.parse_args()

    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    results = []

    for key, rel_path in COMPOSER_SCRIPTS.items():
        script = SKILLS_DIR / rel_path
        if not script.exists():
            results.append({"component": key, "status": "skipped"})
            continue

        cmd = [sys.executable, str(script), "--output-dir", str(out)]
        if key == "templates":
            cmd.extend(["--owner", args.owner, "--repo-name", args.repo_name])
        elif key == "community_docs":
            cmd.extend(["--owner", args.owner, "--repo-name", args.repo_name])
        elif key == "maturity_markers":
            readme = out / "README.md"
            if readme.exists():
                cmd.extend(["--maturity", args.maturity, "--output", str(readme)])
            else:
                results.append({"component": key, "status": "skipped", "reason": "README.md not found"})
                continue

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            results.append({"component": key, "status": "created"})
        except subprocess.CalledProcessError as e:
            results.append({"component": key, "status": "error", "stderr": e.stderr})

    import json
    json.dump(results, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
