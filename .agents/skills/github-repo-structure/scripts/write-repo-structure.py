#!/usr/bin/env python3
"""Generate the .github repository structure from template files."""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

STRUCTURE_TEMPLATES = {
    "ISSUE_TEMPLATE": {
        "bug_report.md": "bug_report.md.template",
        "feature_request.md": "feature_request.md.template",
    },
    "workflows": {
        "ci.yml": "ci.yml.template",
    },
}

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate .github directory structure")
    parser.add_argument("--output-dir", default=".github", help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing")
    args = parser.parse_args()

    for subdir, files in STRUCTURE_TEMPLATES.items():
        target_dir = Path(args.output_dir) / subdir
        if args.dry_run:
            print(f"mkdir -p {target_dir}")
        else:
            target_dir.mkdir(parents=True, exist_ok=True)

        for fname, tmpl_name in files.items():
            fpath = target_dir / fname
            if args.dry_run:
                print(f"write {fpath}")
            else:
                content = (SCRIPTS_DIR / tmpl_name).read_text()
                fpath.write_text(content)
                print(f"Wrote {fpath}", file=sys.stderr)

    if not args.dry_run:
        print(json.dumps({"created": args.output_dir}), file=sys.stderr)

if __name__ == "__main__":
    main()
