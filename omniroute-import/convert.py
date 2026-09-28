#!/usr/bin/env python3
"""Convert opencode auth.json to OmniRoute provider import format (JSON array).

Usage:
    convert.py [AUTH_JSON] [OUTPUT_JSON]

AUTH_JSON defaults to ~/.config/opencode/auth.json, then
~/.local/share/opencode/auth.json. OUTPUT_JSON defaults to
omniroute-providers.json next to this script.
"""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_AUTH_FILES = [
    Path.home() / ".config" / "opencode" / "auth.json",
    Path.home() / ".local" / "share" / "opencode" / "auth.json",
]


def find_auth_file(explicit_path):
    if explicit_path:
        path = Path(explicit_path).expanduser()
        if not path.exists():
            print(f"ERROR: auth file not found: {path}", file=sys.stderr)
            sys.exit(1)
        return path
    for path in DEFAULT_AUTH_FILES:
        if path.exists():
            return path
    return None


def convert(auth_data):
    entries = []
    for provider_id, config in auth_data.items():
        if not isinstance(config, dict):
            continue
        api_key = config.get("key", "")
        if not api_key:
            continue
        entry = {
            "provider": provider_id,
            "name": provider_id,
            "apiKey": api_key,
        }
        metadata = config.get("metadata", {})
        if metadata:
            entry["providerSpecificData"] = {}
            if "accountId" in metadata:
                entry["providerSpecificData"]["accountId"] = metadata["accountId"]
            if "gatewayId" in metadata:
                entry["providerSpecificData"]["gatewayId"] = metadata["gatewayId"]
        entries.append(entry)
    return entries


def main():
    parser = argparse.ArgumentParser(
        description="Convert opencode auth.json to OmniRoute provider import format.",
    )
    parser.add_argument(
        "auth_json",
        nargs="?",
        help="Path to opencode auth.json (default: standard opencode locations).",
    )
    parser.add_argument(
        "output_json",
        nargs="?",
        help="Output path (default: omniroute-providers.json next to this script).",
    )
    args = parser.parse_args()

    auth_file = find_auth_file(args.auth_json)
    if not auth_file:
        print(
            "ERROR: No opencode auth.json found. Pass its path as the first argument.",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"Reading: {auth_file}")
    with open(auth_file, "r") as f:
        auth_data = json.load(f)
    entries = convert(auth_data)
    out_file = (
        Path(args.output_json).expanduser()
        if args.output_json
        else Path(__file__).parent / "omniroute-providers.json"
    )
    with open(out_file, "w") as f:
        json.dump(entries, f, indent=2)
    print(f"Wrote {len(entries)} providers to {out_file}")
    for e in entries:
        print(f"  - {e['provider']}")


if __name__ == "__main__":
    main()
