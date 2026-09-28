#!/usr/bin/env python3
"""Extract one provider definition containing only free, live models.

The script merges the models cache with configured provider overrides and writes
one provider metadata file containing the filtered model map.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from opencode_common import (
    JsonObject,
    add_model_config_arguments,
    add_output_dir_argument,
    load_json_object,
    write_json,
)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract provider metadata with free live models."
    )
    parser.add_argument("provider", help="Provider key in the models cache")
    add_model_config_arguments(parser)
    add_output_dir_argument(parser)
    return parser.parse_args()


def merge_provider_data(
    provider_name: str,
    cached_provider: JsonObject | None,
    configured_provider: JsonObject | None,
) -> JsonObject:
    """Merge provider metadata and models, with config values taking precedence."""
    if cached_provider is None and configured_provider is None:
        raise KeyError(f"Provider not found: {provider_name}")

    merged_provider: JsonObject = dict(cached_provider or {})
    merged_provider.update(configured_provider or {})
    merged_models: JsonObject = {}
    for provider in (cached_provider, configured_provider):
        provider_models = provider.get("models") if provider else None
        if isinstance(provider_models, dict):
            merged_models.update(provider_models)
    merged_provider["models"] = merged_models
    return merged_provider


def filter_free_live_models(provider_data: JsonObject) -> JsonObject:
    """Keep models with zero input cost and no deprecated status."""
    models = provider_data.get("models")
    if not isinstance(models, dict):
        raise ValueError("The provider object does not contain a models object")

    free_live_models: JsonObject = {}
    for model_name, model_data in models.items():
        if not isinstance(model_data, dict):
            continue
        cost = model_data.get("cost")
        if (
            isinstance(cost, dict)
            and cost.get("input") == 0
            and model_data.get("status", "") != "deprecated"
        ):
            free_live_models[model_name] = model_data
    return free_live_models


def write_provider_file(
    output_dir: Path,
    provider_name: str,
    cached_provider: JsonObject | None,
    configured_provider: JsonObject | None,
) -> bool:
    """Write a provider's free/live definition when models are available."""
    provider_data = merge_provider_data(
        provider_name,
        cached_provider,
        configured_provider,
    )
    provider_data["models"] = filter_free_live_models(provider_data)
    model_count = len(provider_data["models"])
    if model_count == 0:
        print(f"{provider_name}: no free live models; skipped provider file")
        return False

    output_path = output_dir / f"provider-free-live-{provider_name}.json"
    write_json(output_path, provider_data)
    print(f"{provider_name}: wrote {model_count} models")
    return True


def main() -> int:
    """Run the single-provider extraction workflow."""
    arguments = parse_arguments()
    try:
        model_providers = load_json_object(arguments.models)
        config_providers = load_json_object(arguments.config).get("provider", {})
        if not isinstance(config_providers, dict):
            config_providers = {}
        write_provider_file(
            arguments.output_dir,
            arguments.provider,
            model_providers.get(arguments.provider),
            config_providers.get(arguments.provider),
        )
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
