#!/usr/bin/env python3
"""Test an stdio MCP server — perform MCP initialize handshake then tools/list.

Usage:
    python3 scripts/test-pipe.py --command <command> [--args '["arg1","arg2"]'] [--timeout 15]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading


def read_line(stream, timeout: float, buffer: list[str]) -> None:
    try:
        line = stream.readline()
        if line:
            buffer.append(line)
    except ValueError:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", required=True, help="MCP server command")
    parser.add_argument("--args", default="[]", help="JSON array of argument strings")
    parser.add_argument("--timeout", type=int, default=15, help="Timeout in seconds")
    args = parser.parse_args()

    try:
        cmd_args = json.loads(args.args)
        if not isinstance(cmd_args, list):
            print("ERROR: --args must be a JSON array", file=sys.stderr)
            return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid --args JSON: {e}", file=sys.stderr)
        return 1

    try:
        proc = subprocess.Popen(
            [args.command, *cmd_args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        print(f"ERROR: command not found: {args.command}", file=sys.stderr)
        return 1

    def send(msg: dict) -> None:
        line = json.dumps(msg) + "\n"
        proc.stdin.write(line)
        proc.stdin.flush()

    def recv(timeout: float) -> dict | None:
        buffer: list[str] = []
        thread = threading.Thread(target=read_line, args=(proc.stdout, timeout, buffer))
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        if not buffer:
            return None
        try:
            return json.loads(buffer[0])
        except json.JSONDecodeError:
            return None

    # Phase 1: Initialize
    send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
          "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                     "clientInfo": {"name": "opencode-test", "version": "1.0.0"}}})
    init_resp = recv(args.timeout)
    if init_resp is None:
        print("ERROR: no response to initialize request", file=sys.stderr)
        proc.kill()
        return 1
    if "result" not in init_resp:
        print(f"ERROR: initialize failed: {init_resp.get('error', 'unknown')}", file=sys.stderr)
        proc.kill()
        return 1
    server_info = init_resp["result"].get("serverInfo", {})
    print(f"  server: {server_info.get('name', '?')} v{server_info.get('version', '?')}")

    # Phase 2: Initialized notification (no response expected)
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    # Phase 3: tools/list
    send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    tool_resp = recv(args.timeout)
    proc.kill()

    if tool_resp is None:
        print("ERROR: no response to tools/list", file=sys.stderr)
        return 1
    if "result" not in tool_resp:
        print(f"ERROR: tools/list failed: {tool_resp.get('error', 'unknown')}", file=sys.stderr)
        return 1

    tools = tool_resp["result"].get("tools", [])
    print(f"SUCCESS: JSON-RPC MCP server responded")
    print(f"  tools available: {len(tools)}")
    for t in tools:
        print(f"    - {t.get('name', '?')}: {t.get('description', '')[:80]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
