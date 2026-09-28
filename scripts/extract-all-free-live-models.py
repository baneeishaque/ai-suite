#!/usr/bin/env python3
"""Generate free, live model lists for all OpenCode providers.

The script reads provider definitions from the models cache and config, then
writes one filtered JSON file per provider whether authenticated or not.
"""

from __future__ import annotations

import argparse
import json
import sys

from opencode_common import (
    add_model_config_arguments,
    add_output_dir_argument,
    load_json_object,
    load_provider_extractor,
)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate free live model files for all providers."
    )
    add_model_config_arguments(parser)
    add_output_dir_argument(parser)
    return parser.parse_args()


def main() -> int:
    """Generate filtered model files for all configured providers."""
    arguments = parse_arguments()
    try:
        provider_extractor = load_provider_extractor()
        model_providers = load_json_object(arguments.models)
        config_document = load_json_object(arguments.config)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    config_providers = config_document.get("provider", {})
    if not isinstance(config_providers, dict):
        config_providers = {}

    provider_names = {
        provider_name for provider_name, provider in model_providers.items()
        if isinstance(provider, dict)
    }
    provider_names.update(
        provider_name for provider_name, provider in config_providers.items()
        if isinstance(provider, dict)
    )

    generated = 0
    for provider in provider_names:
        wrote_file = provider_extractor.write_provider_file(
            arguments.output_dir,
            provider,
            model_providers.get(provider),
            config_providers.get(provider),
        )
        if wrote_file:
            generated += 1

    print(f"Generated {generated} files; skipped {len(provider_names) - generated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
