#!/usr/bin/env python3
"""Read-only registry lookup for installed opencode plugins.

Emits one JSON record per plugin known to the local opencode installation:

- enabled: plugin name present in the top-level "plugin" array of the
  opencode config file (JSONC parsed via opencode-jsonc-util, never re-rolled)
- status: "enabled" / "installed-not-enabled" / "missing"
- plugin_files: *.ts files found in the user or project plugin dirs
- logs_dir + logs_convention: echoed for the "logger" plugin

Output:
{"name": str, "enabled": bool, "source": str, "plugin_files": [str],
 "status": str, "logs_dir": str|None, "logs_convention": str|None}

Exit codes: 0 = success, 1 = --plugin requested but not found, 2 = usage.

Usage:
  locate-installed-plugins.py [--plugin <name> ...] [--json]
      [--output <file>] [--user-config <file>] [--project-config <file>]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[4]  # .agents/skills/opencode/<skill>/scripts

JSONC_READER = (
    REPO_ROOT / ".agents/skills/opencode-jsonc-util" / "scripts" / "read-jsonc.py"
)
USER_CONFIG = Path.home() / ".config/opencode/opencode.json"
USER_PLUGIN_DIR = Path.home() / ".config/opencode/plugins"
PROJECT_CONFIG = Path(".opencode/opencode.json")
PROJECT_PLUGIN_DIR = Path(".opencode/plugins")

LOGGER_CONVENTION = "per-session YAML turn files (ses_<id>/NNN-<ts>.yaml) + <id>.jsonl / .state.json"


def read_jsonc(file: Path) -> dict | None:
    """Delegate to opencode-jsonc-util (never re-implement the parser)."""
    if not JSONC_READER.is_file():
        print(f"ERROR: read-jsonc.py not found at {JSONC_READER}", file=sys.stderr)
        return None
    try:
        r = subprocess.run(
            [sys.executable, str(JSONC_READER), str(file)],
            capture_output=True, text=True, timeout=30,
        )
    except subprocess.TimeoutExpired:
        print(f"ERROR: read-jsonc.py timed out on {file}", file=sys.stderr)
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def find_config(user_config: Path | None, project_config: Path | None) -> tuple[dict | None, str | None]:
    """First readable candidate config wins; returns (parsed, path)."""
    for label, path in (
        ("user", user_config if user_config is not None else USER_CONFIG),
        ("project", project_config if project_config is not None else PROJECT_CONFIG),
    ):
        if path is None or not path.is_file():
            continue
        data = log_jsonc_or_none(path)
        if data is None:
            print(f"WARN: unreadable config, skipping: {path}", file=sys.stderr)
            continue
        return data, str(path)
    return None, None


def log_jsonc_or_none(path: Path) -> dict | None:
    return read_jsonc(path)


def enabled_names(config: dict | None) -> list[str]:
    if config is None:
        return []
    plugins = config.get("plugin")
    if isinstance(plugins, list):
        return [str(p) for p in plugins if isinstance(p, str)]
    if isinstance(plugins, str):
        return [plugins]
    return []


def normalize(name: str) -> str:
    """opencode plugin names: '@scope/opencode-logger' or 'opencode-logger.ts'."""
    base = name.rsplit("/", 1)[-1]
    return base[:-3] if base.endswith(".ts") else base


ALIASES = {"opencode-logger": "logger"}  # canonical display name for the logger


def canonical(name: str) -> str:
    return ALIASES.get(normalize(name), normalize(name))


def plugin_files() -> list[Path]:
    found: list[Path] = []
    for d in (USER_PLUGIN_DIR, PROJECT_PLUGIN_DIR):
        if d.is_dir():
            found.extend(sorted(d.glob("*.ts")))
    return found


def main() -> int:
    ap = argparse.ArgumentParser(
        description="locate installed opencode plugins (read-only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--plugin", action="append", default=[],
                    metavar="NAME", help="filter output to this plugin; repeatable")
    ap.add_argument("--json", action="store_true",
                    help="emit one JSON array instead of JSONL")
    ap.add_argument("--output", help="write to a file instead of stdout")
    ap.add_argument("--user-config", help="override user config path")
    ap.add_argument("--project-config", help="override project config path")
    args = ap.parse_args()

    config, config_path = find_config(
        Path(args.user_config) if args.user_config else None,
        Path(args.project_config) if args.project_config else None,
    )
    enabled = [canonical(n) for n in enabled_names(config)]

    names = sorted(set(enabled))
    for f in plugin_files():
        names = sorted(set(names) | {canonical(f.name)})

    if args.plugin:
        wanted = {canonical(n) for n in args.plugin}
        names = [n for n in names if n in wanted]
        if not names:
            print("ERROR: requested plugin(s) not found in registry", file=sys.stderr)
            return 1

    records = []
    for name in names:
        files = [str(f) for f in plugin_files() if canonical(f.name) == name]
        in_config = name in enabled
        in_dirs = bool(files)
        if in_config:
            status = "enabled-config"
        elif in_dirs:
            status = "enabled-auto-dir"  # opencode auto-loads *.ts from plugins dirs
        else:
            status = "missing"
        logs_dir = str(REPO_ROOT / ".opencode/logs") if name == "logger" else None
        records.append({
            "name": name,
            "enabled": in_config or in_dirs,
            "status": status,
            "config_file": str(config_path) if config_path else None,
            "plugin_files": files,
            "logs_dir": logs_dir,
            "logs_convention": LOGGER_CONVENTION if name == "logger" else None,
        })

    if args.json:
        text = json.dumps(records, ensure_ascii=False, indent=2)
    else:
        text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)

    if args.output:
        Path(args.output).write_text(text)
        print(f"Wrote {len(records)} record(s) to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())