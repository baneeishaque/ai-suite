"""Shared OpenCode paths and JSON-loading helpers."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

JsonObject = dict[str, Any]


def select_environment_key(
    provider_name: str, environment_names: Any
) -> str:
    """Select the first explicit uppercase ``_KEY`` environment name."""
    if not isinstance(environment_names, list):
        return ""

    matching_names = [
        environment_name
        for environment_name in environment_names
        if isinstance(environment_name, str)
        and environment_name
        and environment_name.isupper()
        and environment_name.endswith("_KEY")
    ]
    if len(matching_names) > 1:
        print(
            f"Warning: provider '{provider_name}' has {len(matching_names)} "
            f"key environment names. Selected: {matching_names[0]}. "
            f"Skipped: {', '.join(matching_names[1:])}.",
            file=sys.stderr,
        )
    return matching_names[0] if matching_names else ""


def load_provider_extractor() -> ModuleType:
    """Load the shared free/live provider extractor module."""
    script_path = Path(__file__).with_name("extract-provider-free-live-models.py")
    spec = importlib.util.spec_from_file_location(
        "provider_free_live_models", script_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load provider extractor: {script_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add_model_config_arguments(
    parser: argparse.ArgumentParser,
    *,
    models_default: Path | None = None,
    config_default: Path | None = None,
) -> argparse.ArgumentParser:
    """Add shared OpenCode models/config path options to an argument parser."""
    parser.add_argument(
        "--models",
        type=Path,
        default=models_default or default_models_path(),
        help="Path to OpenCode models.json",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=config_default or default_config_path(),
        help="Path to OpenCode opencode.json",
    )
    return parser


def add_output_dir_argument(
    parser: argparse.ArgumentParser,
    *,
    default: Path | None = None,
    help_text: str = "Directory for generated JSON files",
) -> argparse.ArgumentParser:
    """Add the shared generated-output directory option to a parser."""
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default or Path.cwd(),
        help=help_text,
    )
    return parser


def xdg_path(environment_name: str, fallback: str, *parts: str) -> Path:
    """Resolve a path beneath an XDG directory."""
    home = Path(os.environ.get(environment_name, fallback)).expanduser()
    return home.joinpath(*parts)


def default_auth_path() -> Path:
    """Return the OpenCode auth path under the XDG data home."""
    return xdg_path("XDG_DATA_HOME", "~/.local/share", "opencode", "auth.json")


def default_models_path() -> Path:
    """Return the OpenCode models path under the XDG cache home."""
    return xdg_path("XDG_CACHE_HOME", "~/.cache", "opencode", "models.json")


def default_config_path() -> Path:
    """Return the OpenCode config path under the XDG config home."""
    return xdg_path("XDG_CONFIG_HOME", "~/.config", "opencode", "opencode.json")


def load_json_object(path: Path) -> JsonObject:
    """Load and validate a top-level JSON object (supports JSONC: // comments and trailing commas)."""
    if not path.is_file():
        raise FileNotFoundError(f"Input file does not exist: {path}")

    text = path.read_text(encoding="utf-8")

    # Strip // comments (not inside quoted strings)
    lines = text.split("\n")
    stripped: list[str] = []
    for line in lines:
        if "//" in line:
            in_string = False
            for i, ch in enumerate(line):
                if ch == '"':
                    in_string = not in_string
                elif ch == "/" and i + 1 < len(line) and line[i + 1] == "/" and not in_string:
                    line = line[:i]
                    break
        stripped.append(line)

    cleaned = "\n".join(stripped)
    # Remove trailing commas before ] or }
    cleaned = re.sub(r",(\s*[\]}])", r"\1", cleaned)

    value = json.loads(cleaned)

    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def write_json(path: Path, value: JsonObject) -> None:
    """Write a readable JSON object with a trailing newline."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output_file:
        json.dump(value, output_file, indent=2, ensure_ascii=True)
        output_file.write("\n")
