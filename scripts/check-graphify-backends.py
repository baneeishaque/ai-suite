#!/usr/bin/env python3
"""Check Graphify provider/model backends against a generated code repository.

The checker creates a small temporary Python repository, sends one minimal
OpenAI-compatible request per Graphify registry entry, and writes a status
report containing the generated commands.
"""

from __future__ import annotations

import argparse
import json
import os
import selectors
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from opencode_common import default_auth_path, load_json_object, write_json

JsonObject = dict[str, Any]
DEFAULT_PROVIDERS = Path.home() / ".graphify" / "providers.json"
DEFAULT_AUTH = default_auth_path()
DEFAULT_REPO = Path("scratch/graphify-backend-check-repo")
DEFAULT_REPORT = Path("scratch/graphify-backend-check-report.json")


def safe_print(
    message: str,
    *,
    file: Any = sys.stdout,
    flush: bool = True,
    end: str = "\n",
    **kwargs: Any,
) -> None:
    """Print while tolerating a closed stdout pipe from consumers like head."""
    try:
        print(message, file=file, flush=flush, end=end, **kwargs)
    except BrokenPipeError:
        if file is sys.stdout:
            try:
                sys.stdout = open(os.devnull, "w", encoding="utf-8")
            except OSError:
                pass
            raise SystemExit(0)
        return


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Check every Graphify provider/model backend."
    )
    parser.add_argument("--providers", type=Path, default=DEFAULT_PROVIDERS)
    parser.add_argument("--auth", type=Path, default=DEFAULT_AUTH)
    parser.add_argument("--repo-dir", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def create_scratch_repo(repo_dir: Path) -> None:
    """Recreate a small deterministic code repository from scratch."""
    shutil.rmtree(repo_dir, ignore_errors=True)
    repo_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "calculator.py": (
            '"""Tiny calculator used for backend smoke checks."""\n\n'
            "def add(left: int, right: int) -> int:\n"
            "    return left + right\n"
        ),
        "symbol-notes.md": (
            "# Backend Check Fixture\n\n"
            "The `add` symbol returns the sum of two integer arguments.\n"
        ),
    }
    for name, content in files.items():
        (repo_dir / name).write_text(content, encoding="utf-8")


def copyable_command(
    command: list[str], base_url: str, model: str, api_key: str
) -> str:
    """Format a runnable command with the resolved API key."""
    parts = [
        f"OPENAI_API_KEY={shlex.quote(api_key)}",
        f"OPENAI_BASE_URL={shlex.quote(base_url)}",
        f"OPENAI_MODEL={shlex.quote(model)}",
        *(shlex.quote(part) for part in command),
    ]
    return " ".join(parts)


def graphify_command(
    entry_name: str,
    entry: JsonObject,
    repo_dir: Path,
    api_key: str,
) -> tuple[list[str], str] | dict[str, Any]:
    """Build the Graphify command or return a validation result."""
    base_url = entry.get("base_url")
    model = entry.get("default_model")
    if not isinstance(base_url, str) or not base_url:
        return {"backend": entry_name, "status": "ERROR", "error": "missing base_url"}
    if not isinstance(model, str) or not model:
        return {"backend": entry_name, "status": "ERROR", "error": "missing model"}

    command = [
        "graphify",
        "extract",
        str(repo_dir),
        "--backend",
        "openai",
        "--max-concurrency",
        "1",
        "--timing",
    ]
    return command, copyable_command(command, base_url, model, api_key)


def resolve_api_key(
    entry_name: str, entry: JsonObject, auth: JsonObject
) -> tuple[str | None, str]:
    """Resolve a key from the longest matching auth alias or environment."""
    matching_aliases = [
        alias
        for alias in auth
        if entry_name.startswith(alias + "-")
    ]
    for alias in sorted(matching_aliases, key=len, reverse=True):
        auth_value = auth[alias]
        if isinstance(auth_value, dict) and isinstance(auth_value.get("key"), str):
            return auth_value["key"], f"auth:{alias}"

    environment_key = entry.get("env_key")
    if isinstance(environment_key, str) and os.environ.get(environment_key):
        return os.environ[environment_key], f"env:{environment_key}"
    return None, "unavailable"


def check_backend(
    entry_name: str,
    entry: JsonObject,
    api_key: str,
    repo_dir: Path,
    timeout: float,
    *,
    command: list[str] | None = None,
    display_command: str | None = None,
) -> dict[str, Any]:
    """Run Graphify extraction for one entry and classify its output."""
    if command is None or display_command is None:
        command_result = graphify_command(entry_name, entry, repo_dir, api_key)
        if isinstance(command_result, dict):
            return command_result
        command, display_command = command_result
    base_url = entry["base_url"]
    model = entry["default_model"]

    environment = os.environ.copy()
    environment.update(
        {
            "OPENAI_API_KEY": api_key,
            "OPENAI_BASE_URL": base_url,
            "OPENAI_MODEL": model,
        }
    )
    started = time.monotonic()
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    process: subprocess.Popen[str] | None = None
    try:
        process = subprocess.Popen(
            command,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        selector = selectors.DefaultSelector()
        assert process.stdout is not None
        assert process.stderr is not None
        selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        selector.register(process.stderr, selectors.EVENT_READ, "stderr")
        deadline = time.monotonic() + timeout
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                process.kill()
                process.wait()
                raise subprocess.TimeoutExpired(command, timeout)
            for key, _ in selector.select(remaining):
                line = key.fileobj.readline()
                if not line:
                    selector.unregister(key.fileobj)
                    continue
                target = stdout_lines if key.data == "stdout" else stderr_lines
                target.append(line)
                safe_print(f"[{entry_name} {key.data}] {line}", end="", flush=True)
        exit_code = process.wait()
    except (OSError, subprocess.TimeoutExpired) as error:
        return {
            "backend": entry_name,
            "status": "FAIL",
            "error": type(error).__name__,
            "duration_seconds": round(time.monotonic() - started, 3),
            "command": display_command,
            "stdout": "".join(stdout_lines),
            "stderr": "".join(stderr_lines),
        }

    output = f"{''.join(stdout_lines)}\n{''.join(stderr_lines)}".strip()
    wrote_graph = "[graphify extract] wrote " in output
    result = {
        "backend": entry_name,
        "status": "PASS" if exit_code == 0 and wrote_graph else "FAIL",
        "exit_code": exit_code,
        "duration_seconds": round(time.monotonic() - started, 3),
        "command": display_command,
        "stdout": "".join(stdout_lines),
        "stderr": "".join(stderr_lines),
        "graphify_output": output,
    }
    return result


def main() -> int:
    """Check all configured Graphify backends."""
    arguments = parse_arguments()
    try:
        providers = load_json_object(arguments.providers)
        auth = load_json_object(arguments.auth)
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    results: list[dict[str, Any]] = []
    for entry_name in providers:
        entry = providers[entry_name]
        if not isinstance(entry, dict):
            results.append({"backend": entry_name, "status": "ERROR", "error": "invalid entry"})
            continue
        api_key, source = resolve_api_key(entry_name, entry, auth)
        command_result = graphify_command(
            entry_name,
            entry,
            arguments.repo_dir,
            api_key or "",
        )
        if isinstance(command_result, dict):
            results.append(command_result)
            safe_print(f"command: unavailable ({command_result['error']})")
            continue
        command, display_command = command_result
        safe_print(f"command: {display_command}")
        if api_key is None:
            results.append(
                {
                    "backend": entry_name,
                    "status": "ERROR",
                    "credential_source": source,
                    "error": "missing api_key",
                }
            )
            continue
        if arguments.dry_run:
            results.append(
                {
                    "backend": entry_name,
                    "status": "READY",
                    "credential_source": source,
                    "command": display_command,
                }
            )
            continue
        create_scratch_repo(arguments.repo_dir)
        result = check_backend(
            entry_name,
            entry,
            api_key,
            arguments.repo_dir,
            arguments.timeout,
            command=command,
            display_command=display_command,
        )
        result["credential_source"] = source
        results.append(result)

    report = {
        "repo_dir": str(arguments.repo_dir),
        "backend_count": len(providers),
        "results": results,
    }
    try:
        write_json(arguments.report, report)
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    counts: dict[str, int] = {}
    for result in results:
        status = str(result["status"])
        counts[status] = counts.get(status, 0) + 1
    summary = ", ".join(f"{status.lower()}={count}" for status, count in sorted(counts.items()))
    safe_print(f"Checked {len(providers)} backends: {summary}")
    safe_print(f"Report: {arguments.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
