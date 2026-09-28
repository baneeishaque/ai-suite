#!/usr/bin/env python3
"""
generate-renovate-config.py

Tier-1 (Python) script for assembling Renovate config from templates.

Usage:
    python3 generate-renovate-config.py \
        --template <base|automerge|monorepo|docker|python> \
        --output <path> \
        --params '<json-string>' \
        [--validate]

Exit codes:
    0 = success
    1 = template not found / render error / validation failure
    2 = invalid arguments
"""

import argparse
import json
import sys
from pathlib import Path
from string import Template
from typing import Any, Dict


SCRIPT_DIR = Path(__file__).parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"

# Default values for optional parameters per template
DEFAULTS = {
    "base": {
        "extends": ["config:recommended"],
        "schedule": ["at any time"],
        "timezone": "UTC",
    },
    "automerge": {
        "rebaseWhen": "behind-base-branch",
        "automerge": True,
        "automergeType": "pr",
        "automergeStrategy": "auto",
        "automergeSchedule": ["at any time"],
        "packageRules": [],
    },
    "monorepo": {
        "baseBranchPatterns": ["$default"],
        "schedule": ["at any time"],
        "timezone": "UTC",
        "packageRules": [],
    },
    "docker": {
        "pinDigests": True,
        "dockerfileMatch": ["**/Dockerfile*"],
    },
    "python": {
        "constraintsFiltering": "strict",
        "constraints": {},
    },
}

TEMPLATES = {
    "base": "renovate-config-base.json.template",
    "automerge": "renovate-config-automerge.json.template",
    "monorepo": "renovate-config-monorepo.json.template",
    "docker": "renovate-config-docker.json.template",
    "python": "renovate-config-python.json.template",
}


def load_template(template_name: str) -> Template:
    """Load a template file and return a string.Template object."""
    template_file = TEMPLATES.get(template_name)
    if not template_file:
        raise ValueError(f"Unknown template: {template_name}. Available: {list(TEMPLATES.keys())}")

    template_path = SCRIPT_DIR / "templates" / template_file
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    content = template_path.read_text(encoding="utf-8")
    return Template(content)


def merge_params(template_name: str, user_params: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user params with defaults for the given template."""
    merged = DEFAULTS.get(template_name, {}).copy()
    merged.update(user_params)
    return merged


def render_template(template_name: str, params: Dict[str, Any]) -> str:
    """Render a template with the given parameters."""
    template = load_template(template_name)
    # Convert all values to JSON-serializable strings for Template substitution
    safe_params = {}
    for key, value in params.items():
        if isinstance(value, (bool, int, float)):
            safe_params[key] = json.dumps(value)
        elif isinstance(value, (list, dict)):
            safe_params[key] = json.dumps(value, separators=(",", ":"))
        else:
            safe_params[key] = str(value)
    template = load_template(template_name)
    return template.safe_substitute(safe_params)


def validate_json(json_str: str) -> bool:
    """Validate that the rendered output is valid JSON."""
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError as e:
        print(f"JSON validation failed: {e}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Renovate config from template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available templates:
  base       - Minimal recommended config
  automerge  - Auto-merge + auto-rebase enabled
  monorepo   - Monorepo-aware with package groups
  docker     - Docker-specific with pin digests
  python     - Python-specific with constraints filtering

Example:
  python3 generate-renovate-config.py \\
      --template automerge \\
      --output renovate.json \\
      --params '{"rebaseWhen": "behind-base-branch", "automerge": true}'
        """,
    )
    parser.add_argument(
        "--template",
        required=True,
        choices=list(TEMPLATES.keys()),
        help="Template name to use",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path",
    )
    parser.add_argument(
        "--params",
        required=True,
        help="JSON string of parameters for template substitution",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate output JSON syntax",
    )

    args = parser.parse_args()

    try:
        user_params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Invalid --params JSON: {e}", file=sys.stderr)
        return 2

    try:
        params = merge_params(args.template, user_params)
        rendered = render_template(args.template, params)
    except (ValueError, FileNotFoundError) as e:
        print(f"Template error: {e}", file=sys.stderr)
        return 1

    if args.validate and not validate_json(rendered):
        return 1

    try:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        print(f"Generated: {output_path}")
        return 0
    except OSError as e:
        print(f"Failed to write output: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())