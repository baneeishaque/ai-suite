#!/usr/bin/env python3
"""Run an OpenCode command through mitmproxy and report observed endpoints.

Usage:
    python3 scripts/probe-opencode-endpoints.py -- \
        opencode run --model provider/model "Reply with exactly: OK"

The command after ``--`` is executed unchanged. The probe records sanitized
request metadata only; it never writes headers, authorization values, or bodies.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


DEFAULT_PORT = 9453
DEFAULT_OUTPUT = Path("scratch/opencode-endpoints.jsonl")
MITM_CERT = Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.pem"
ADDON = Path(__file__).with_name("opencode-endpoint-probe-addon.py")


def find_mitmdump() -> str:
    """Find mitmdump on PATH or in the active Python user-bin directory."""
    executable = shutil.which("mitmdump")
    if executable:
        return executable

    user_bin = Path(sys.executable).parent
    candidates = (
        user_bin / "mitmdump",
        Path.home() / "Library" / "Python" / f"{sys.version_info.major}.{sys.version_info.minor}" / "bin" / "mitmdump",
    )
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    raise FileNotFoundError("mitmdump is not installed or is not on PATH")


def parse_arguments() -> argparse.Namespace:
    """Parse probe options and the command to execute."""
    parser = argparse.ArgumentParser(
        description="Run an OpenCode command through mitmproxy and report endpoints."
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--startup-timeout", type=float, default=20.0)
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="OpenCode command, including arguments, after --",
    )
    arguments = parser.parse_args()
    if arguments.command[:1] == ["--"]:
        arguments.command = arguments.command[1:]
    if not arguments.command:
        parser.error("provide the OpenCode command after --")
    return arguments


def port_is_open(port: int) -> bool:
    """Return whether a local TCP port accepts connections."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.settimeout(0.2)
        return connection.connect_ex(("127.0.0.1", port)) == 0


def wait_for_proxy(port: int, timeout: float) -> None:
    """Wait until mitmdump is listening or fail with a useful error."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if port_is_open(port):
            return
        time.sleep(0.1)
    raise TimeoutError(f"mitmdump did not listen on 127.0.0.1:{port}")


def start_proxy(port: int, output: Path) -> subprocess.Popen[str]:
    """Start mitmdump with the endpoint-observation addon."""
    mitmdump = find_mitmdump()
    environment = os.environ.copy()
    environment["OPENCODE_PROBE_OUTPUT"] = str(output)
    return subprocess.Popen(
        [
            mitmdump,
            "--listen-host",
            "127.0.0.1",
            "--listen-port",
            str(port),
            "-s",
            str(ADDON),
        ],
        env=environment,
        stdout=None,
        stderr=None,
        text=True,
    )


def run_opencode(command: list[str], port: int) -> int:
    """Run OpenCode through the local proxy with Node's mitm CA trusted."""
    environment = os.environ.copy()
    proxy_url = f"http://127.0.0.1:{port}"
    environment.update(
        {
            "HTTP_PROXY": proxy_url,
            "HTTPS_PROXY": proxy_url,
            "http_proxy": proxy_url,
            "https_proxy": proxy_url,
            "ALL_PROXY": proxy_url,
            "all_proxy": proxy_url,
        }
    )
    if MITM_CERT.is_file():
        environment["NODE_EXTRA_CA_CERTS"] = str(MITM_CERT)
    print(f"running: {' '.join(command)}")
    completed = subprocess.run(command, env=environment, check=False)
    return completed.returncode


def read_observations(output: Path) -> list[dict[str, Any]]:
    """Read valid observations written by the addon."""
    if not output.is_file():
        return []
    observations: list[dict[str, Any]] = []
    for line in output.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            observations.append(value)
    return observations


def stop_proxy(proxy: subprocess.Popen[str]) -> None:
    """Terminate mitmdump and force-kill only if it does not exit promptly."""
    if proxy.poll() is not None:
        return
    proxy.send_signal(signal.SIGTERM)
    try:
        proxy.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proxy.kill()
        proxy.wait()


def main() -> int:
    """Run the proxy probe and print unique observed request URLs."""
    arguments = parse_arguments()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.unlink(missing_ok=True)

    proxy: subprocess.Popen[str] | None = None
    try:
        proxy = start_proxy(arguments.port, arguments.output)
        wait_for_proxy(arguments.port, arguments.startup_timeout)
        if not MITM_CERT.is_file():
            print(
                f"warning: mitmproxy CA not found at {MITM_CERT}; "
                "HTTPS clients may reject the proxy",
                file=sys.stderr,
            )
        command_exit = run_opencode(arguments.command, arguments.port)
    except (FileNotFoundError, TimeoutError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    finally:
        if proxy is not None:
            stop_proxy(proxy)

    observations = read_observations(arguments.output)
    unique_urls = dict.fromkeys(
        str(observation["url"])
        for observation in observations
        if isinstance(observation.get("url"), str)
    )
    print(f"observations: {len(observations)}")
    print(f"saved: {arguments.output}")
    print("unique URLs:")
    for url in unique_urls:
        print(f"  {url}")
    return command_exit


if __name__ == "__main__":
    raise SystemExit(main())
