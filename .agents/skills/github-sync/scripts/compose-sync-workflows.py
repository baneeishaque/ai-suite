#!/usr/bin/env python3
"""C3 composer: generate GitHub sync workflows.

Calls B9 (github-sync-description) and B10 (github-sync-topics).
"""
import argparse
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2]

SYNC_SCRIPTS = {
    "sync_description": "github-sync-description/scripts/write-description-sync-workflow.py",
    "sync_topics": "github-sync-topics/scripts/write-topics-sync-workflow.py",
}

DEFAULT_OUTPUTS = {
    "sync_description": ".github/workflows/sync-description.yml",
    "sync_topics": ".github/workflows/sync-topics.yml",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate GitHub sync workflows"
    )
    parser.add_argument(
        "--output-dir", default=".", help="Output directory"
    )
    args = parser.parse_args()

    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    results = []

    for key, rel_path in SYNC_SCRIPTS.items():
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
