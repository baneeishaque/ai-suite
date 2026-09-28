#!/usr/bin/env python3
"""Emit shell exports for API keys stored in OpenCode auth.json.

Only environment-variable assignments are printed for providers whose explicit
OpenCode metadata declares an environment variable name. The script does not
guess or synthesize names, and it preserves the natural auth order.
"""

from __future__ import annotations

import json
import shlex
import sys
import argparse

from opencode_common import (
    JsonObject,
    default_auth_path,
    default_config_path,
    default_models_path,
    load_json_object,
    select_environment_key,
)


def merge_providers(
    model_providers: JsonObject, config_providers: JsonObject
) -> JsonObject:
    """Merge provider env lists from models and config metadata."""
    merged_environment_names: JsonObject = {}
    for provider_name in {*model_providers, *config_providers}:
        model_environment_names = model_providers.get(provider_name, [])
        config_environment_names = config_providers.get(provider_name, [])
        if not isinstance(model_environment_names, list):
            model_environment_names = []
        if not isinstance(config_environment_names, list):
            config_environment_names = []
        merged_provider_environment_names = list(model_environment_names)
        for environment_name in config_environment_names:
            if environment_name not in merged_provider_environment_names:
                merged_provider_environment_names.append(environment_name)
        merged_environment_names[provider_name] = (
            merged_provider_environment_names
        )
    return merged_environment_names


def main() -> int:
    """Emit exports for auth entries with explicit env names."""
    # Argument parsing
    parser = argparse.ArgumentParser(
        description="Emit exports for auth entries with explicit env names."
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress warnings about multiple environment key names.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed warnings (default is concise).")
    parser.add_argument("--env-name", metavar="NAME", help="Force the use of a specific environment variable name (must be present in the provider's env list).")
    args = parser.parse_args()
    auth_path = default_auth_path()
    models_path = default_models_path()
    config_path = default_config_path()
    try:
        auth = load_json_object(auth_path)
        models = {
            provider_name: provider_metadata.get("env", [])
            for provider_name, provider_metadata in load_json_object(models_path).items()
            if isinstance(provider_metadata, dict)
        }
        config_root = load_json_object(config_path).get("provider", {})
        if not isinstance(config_root, dict):
            config_root = {}
        config = {
            provider_name: provider_metadata.get("env", [])
            for provider_name, provider_metadata in config_root.items()
            if isinstance(provider_metadata, dict)
        }
        providers = merge_providers(models, config)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"# OpenCode auth export unavailable: {error}", file=sys.stderr)
        return 1

    for provider_name in auth:
        auth_entry = auth[provider_name]
        if not isinstance(auth_entry, dict):
            continue

        key = auth_entry.get("key")
        if not isinstance(key, str) or not key:
            continue

        # Determine environment variable name
        if args.env_name:
            # Validate forced name
            candidate_names = providers.get(provider_name, [])
            if args.env_name in candidate_names:
                environment_name = args.env_name
            else:
                if not args.quiet:
                    print(
                        f"[WARN] Requested env name '{args.env_name}' not found for provider "
                        f"'{provider_name}'. Falling back to default selection.",
                        file=sys.stderr,
                    )
                environment_name = select_environment_key(
                    provider_name, providers.get(provider_name, []), quiet=args.quiet
                )
        else:
            environment_name = select_environment_key(
                provider_name, providers.get(provider_name, []), quiet=args.quiet
            )
        if environment_name:
            print(f"export {environment_name}={shlex.quote(key)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
