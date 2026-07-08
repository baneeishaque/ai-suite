#!/usr/bin/env python3
"""C7 orchestrator: publish a GitHub repository with full community standards.

Calls B1 (gh-repo-create) to create the repo, then C6 (github-repo-template)
to generate all template files, then commits and pushes.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2]

BASE_SCRIPTS = {
    "repo_create": "gh-repo-create/scripts/gh-repo-create.py",
    "repo_metadata": "gh-repo-edit-metadata/scripts/gh-repo-edit-metadata.py",
    "repo_template": "github-repo-template/scripts/compose-repo-template.py",
    "workflows": "github-workflows/scripts/compose-workflows.py",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Publish a GitHub repository with full community standards"
    )
    parser.add_argument("--repo-name", required=True)
    parser.add_argument(
        "--description", default="", help="Repository description"
    )
    parser.add_argument(
        "--topics", nargs="*", default=[], help="Repository topics"
    )
    parser.add_argument("--owner", default="Baneeishaque")
    parser.add_argument(
        "--visibility",
        default="private",
        choices=["private", "public", "internal"],
    )
    parser.add_argument(
        "--maturity",
        default="experimental",
        choices=["experimental", "beta", "stable", "deprecated"],
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Generate files without pushing",
    )
    args = parser.parse_args()

    results = []

    # Step 1: Create repository
    create_script = SKILLS_DIR / BASE_SCRIPTS["repo_create"]
    cmd = [
        sys.executable, str(create_script),
        "--name", args.repo_name,
        "--visibility", args.visibility,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        results.append({"step": "create_repo", "status": "created"})
    except subprocess.CalledProcessError as e:
        results.append({"step": "create_repo", "status": "error", "stderr": e.stderr})
        json.dump(results, sys.stdout, indent=2)
        sys.exit(1)

    # Step 2: Set metadata
    metadata_script = SKILLS_DIR / BASE_SCRIPTS["repo_metadata"]
    cmd = [
        sys.executable, str(metadata_script),
        "--repo", args.repo_name,
        "--description", args.description,
    ]
    if args.topics:
        cmd.extend(["--topics", *args.topics])
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        results.append({"step": "set_metadata", "status": "updated"})
    except subprocess.CalledProcessError as e:
        results.append({"step": "set_metadata", "status": "error", "stderr": e.stderr})

    # Step 3: Clone the repo
    clone_dir = Path(tempfile.mkdtemp()) / args.repo_name
    try:
        subprocess.run(
            ["gh", "repo", "clone", f"{args.owner}/{args.repo_name}", str(clone_dir)],
            check=True, capture_output=True, text=True,
        )
        results.append({"step": "clone_repo", "status": "cloned"})
    except subprocess.CalledProcessError as e:
        results.append({"step": "clone_repo", "status": "error", "stderr": e.stderr})
        json.dump(results, sys.stdout, indent=2)
        sys.exit(1)

    # Step 4: Generate templates inside cloned repo
    template_script = SKILLS_DIR / BASE_SCRIPTS["repo_template"]
    cmd = [
        sys.executable, str(template_script),
        "--owner", args.owner,
        "--repo-name", args.repo_name,
        "--output-dir", str(clone_dir),
        "--maturity", args.maturity,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        results.append({"step": "generate_templates", "status": "generated"})
    except subprocess.CalledProcessError as e:
        results.append({"step": "generate_templates", "status": "error", "stderr": e.stderr})

    # Step 5: Generate workflows
    workflows_script = SKILLS_DIR / BASE_SCRIPTS["workflows"]
    cmd = [
        sys.executable, str(workflows_script),
        "--output-dir", str(clone_dir),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        results.append({"step": "generate_workflows", "status": "generated"})
    except subprocess.CalledProcessError as e:
        results.append({"step": "generate_workflows", "status": "error", "stderr": e.stderr})

    # Step 6: Commit and push
    if not args.no_push:
        try:
            subprocess.run(
                ["git", "-C", str(clone_dir), "add", "."],
                check=True, capture_output=True, text=True,
            )
            subprocess.run(
                ["git", "-C", str(clone_dir), "commit", "-m", "Add community standards and workflows"],
                check=True, capture_output=True, text=True,
            )
            subprocess.run(
                ["git", "-C", str(clone_dir), "push"],
                check=True, capture_output=True, text=True,
            )
            results.append({"step": "push", "status": "pushed"})
        except subprocess.CalledProcessError as e:
            results.append({"step": "push", "status": "error", "stderr": e.stderr})

    json.dump(results, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
