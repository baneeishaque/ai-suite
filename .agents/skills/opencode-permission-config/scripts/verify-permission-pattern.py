"""
verify-permission-pattern.py — Evaluate opencode permission config patterns against commands.

Given a permission object (JSON) and one or more command strings, shows which pattern
matches each command under opencode's "last matching rule wins" semantics.

Usage:
  python3 verify-permission-pattern.py <permission-object.json> <command>...
  python3 verify-permission-pattern.py --spec <spec-file.json>

Spec file format (JSON array of test cases):
  [
    {"command": "git status", "expect": "allow"},
    {"command": "rm -rf /", "expect": "deny"}
  ]
"""
import json
import subprocess
import sys
import fnmatch
import os
from pathlib import Path


def load_permission_config(source: str) -> dict:
    if source.startswith("{"):
        return json.loads(source)
    script_dir = Path(__file__).resolve().parent.parent.parent
    reader = script_dir / "opencode-jsonc-util" / "scripts" / "read-jsonc.py"
    if reader.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(reader), source],
                capture_output=True, text=True, check=True, timeout=10
            )
            raw = json.loads(result.stdout)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError):
            raw = None
    else:
        raw = None
    if raw is None:
        with open(source) as f:
            raw = json.load(f)
    return extract_bash_permissions(raw)


def extract_bash_permissions(config: dict) -> dict:
    """Extract the bash permission object from an opencode.json config.

    Supports both flat {pattern: action} and nested {permission: {bash: ...}} formats.
    """
    if "bash" in config:
        return config
    if "permission" in config and isinstance(config["permission"], dict):
        perm = config["permission"]
        if "bash" in perm:
            return perm["bash"] if isinstance(perm["bash"], dict) else {}
    return config


def evaluate(config: dict, command: str) -> tuple[str | None, str]:
    last_match = None
    last_action = None
    for pattern, action in config.items():
        if fnmatch.fnmatch(command, pattern):
            last_match = pattern
            last_action = action
    return last_match, last_action


def run_spec(config: dict, spec_path: str) -> bool:
    with open(spec_path) as f:
        data = json.load(f)
        cases = data if isinstance(data, list) else []
    all_pass = True
    for i, case in enumerate(cases):
        cmd = case["command"]
        expected = case["expect"]
        _, action = evaluate(config, cmd)
        verdict = "PASS" if action == expected else "FAIL"
        status = f"[{verdict}]"
        if verdict == "FAIL":
            all_pass = False
        print(
            f"  {status}  '{cmd}'  →  {action or 'NO MATCH'}  "
            f"(expected {expected})"
        )
    return all_pass


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    if args[0] == "--spec":
        if len(args) < 2:
            print("error: --spec requires a spec file path")
            sys.exit(1)
        config_path = os.environ.get(
            "OPENCODE_PERMISSION_CONFIG",
            os.path.join(
                os.path.dirname(__file__), "..", "specs", "default-config.json"
            ),
        )
        config = load_permission_config(config_path)
        success = run_spec(config, args[1])
        sys.exit(0 if success else 1)

    config = load_permission_config(args[0])
    commands = args[1:]

    for cmd in commands:
        pattern, action = evaluate(config, cmd)
        if pattern is None:
            print(f"  '{cmd}'  →  NO MATCH  (no pattern matched)")
        else:
            print(f"  '{cmd}'  →  {action}  (matched '{pattern}')")

    if not commands:
        print("Pattern inventory:")
        for pattern, action in config.items():
            print(f"  {pattern}: {action}")


if __name__ == "__main__":
    main()
