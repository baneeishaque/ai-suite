#!/usr/bin/env python3
"""Generate Graphify provider entries from OpenCode configuration sources.

The script reuses the single-provider merge and free-live filtering functions
from extract-provider-free-live-models.py, then converts each
model into Graphify's flattened provider registry format.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from opencode_common import (
    add_model_config_arguments,
    add_output_dir_argument,
    default_auth_path,
    load_json_object,
    load_provider_extractor,
    select_environment_key,
    write_json,
)

JsonObject = dict[str, Any]


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a Graphify provider registry from OpenCode data."
    )
    parser.add_argument("--auth", type=Path, default=default_auth_path())
    add_model_config_arguments(parser)
    add_output_dir_argument(
        parser,
        default=Path.home() / ".graphify",
        help_text=(
            "Directory for the generated Graphify providers.json "
            "(default: ~/.graphify)"
        ),
    )
    return parser.parse_args()


def slug(value: str) -> str:
    """Convert an identifier into a stable Graphify key fragment."""
    return re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()


def provider_base_url(provider: JsonObject) -> str:
    """Return the provider endpoint explicitly present in provider metadata."""
    configured_url = provider.get("api")
    if isinstance(configured_url, str) and configured_url:
        return configured_url
    return ""


def is_openai_compatible(provider: JsonObject) -> bool:
    """Return whether metadata selects the OpenAI-compatible AI SDK adapter."""
    return provider.get("npm") == "@ai-sdk/openai-compatible"


def graphify_entry(
    provider_name: str, provider: JsonObject, model: JsonObject
) -> JsonObject:
    """Convert an OpenCode model definition to one Graphify entry."""
    cost = model.get("cost")
    cost_data = cost if isinstance(cost, dict) else {}
    model_id = model["id"]
    base_url = provider_base_url(provider)
    return {
        "base_url": base_url,
        "default_model": model_id,
        "env_key": select_environment_key(provider_name, provider.get("env"), quiet=True),
        "pricing": {
            "input": cost_data.get("input", 0.0),
            "output": cost_data.get("output", 0.0),
        },
        "temperature": 0,
    }


def generate_registry(
    provider_extractor: ModuleType,
    auth: JsonObject,
    models: JsonObject,
    config_providers: JsonObject,
) -> JsonObject:
    """Build the flattened Graphify provider registry."""
    registry: JsonObject = {}
    for provider_name in auth:
        cached_provider = models.get(provider_name)
        configured_provider = config_providers.get(provider_name)
        if not isinstance(cached_provider, dict) and not isinstance(
            configured_provider, dict
        ):
            continue

        provider = {}
        if isinstance(cached_provider, dict):
            provider.update(cached_provider)
        if isinstance(configured_provider, dict):
            provider.update(configured_provider)
        if not is_openai_compatible(provider):
            print(
                f"warning: provider '{provider_name}' is not marked "
                "@ai-sdk/openai-compatible; skipped Graphify entries",
                file=sys.stderr,
            )
            continue
        if not provider_base_url(provider):
            print(
                f"warning: provider '{provider_name}' has no api; "
                "skipped Graphify entries",
                file=sys.stderr,
            )
            continue
        environment_key = select_environment_key(
            provider_name, provider.get("env"), quiet=True
        )
        if not environment_key:
            print(
                f"warning: provider '{provider_name}' has no key environment "
                "name; skipped Graphify entries",
                file=sys.stderr,
            )
            continue
        free_live_models = provider_extractor.filter_free_live_models(
            provider_extractor.merge_provider_data(
                provider_name,
                cached_provider if isinstance(cached_provider, dict) else None,
                configured_provider if isinstance(configured_provider, dict) else None,
            )
        )
        for model_name, model in free_live_models.items():
            if not isinstance(model, dict):
                continue
            if not isinstance(model.get("id"), str) or not model["id"]:
                print(
                    f"warning: provider '{provider_name}' model '{model_name}' "
                    "has no id; skipped Graphify entry",
                    file=sys.stderr,
                )
                continue
            entry_name = f"{slug(provider_name)}-{slug(str(model_name))}"
            registry[entry_name] = graphify_entry(
                provider_name, provider, model
            )
    return registry


def main() -> int:
    """Generate the Graphify provider registry."""
    arguments = parse_arguments()
    output_path = arguments.output_dir / "providers.json"
    try:
        provider_extractor = load_provider_extractor()
        auth = load_json_object(arguments.auth)
        models = load_json_object(arguments.models)
        config_providers = load_json_object(arguments.config).get("provider", {})
        if not isinstance(config_providers, dict):
            config_providers = {}
        registry = generate_registry(
            provider_extractor, auth, models, config_providers
        )
        write_json(output_path, registry)
    except (
        FileNotFoundError,
        ImportError,
        json.JSONDecodeError,
        OSError,
        ValueError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"Wrote {len(registry)} Graphify provider entries to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
