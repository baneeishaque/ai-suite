#!/usr/bin/env python3
"""
macos-app-control.py — Python wrapper for macOS app control via JXA.

Provides a structured CLI interface to JXA functions for detecting,
launching, navigating, and interacting with macOS applications.

Reads from args (see --help).
Exit: 0=success, 1=failure, 2=error

Tier: 1 (Python 3.12+) per scripting-language-selection-rules §Tier 1
"""
import argparse
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JXA_HELPER = os.path.join(SCRIPT_DIR, "macos-app-control.jxa")


def parse_args():
    p = argparse.ArgumentParser(
        description="macOS app control via JXA"
    )
    p.add_argument(
        "--modifiers", default="",
        help="Keyboard modifiers for send-keys (e.g., 'command down,shift down')"
    )
    p.add_argument(
        "--menu", default="",
        help="Menu path for menu-click (e.g., 'Microsoft Teams>Show Main Window')"
    )
    p.add_argument(
        "--json", action="store_true",
        help="Output JSON with structured result"
    )

    sub = p.add_subparsers(dest="command", required=True)

    # app-running
    sp = sub.add_parser("app-running", help="Check if app is running")
    sp.add_argument("app_name", help="Application name")

    # app-launch
    sp = sub.add_parser("app-launch", help="Launch app")
    sp.add_argument("app_name", help="Application name")

    # app-show
    sp = sub.add_parser("app-show", help="Show app main window")
    sp.add_argument("app_name", help="Application name")

    # app-activate
    sp = sub.add_parser("app-activate", help="Bring app to foreground")
    sp.add_argument("app_name", help="Application name")

    # send-keys
    sp = sub.add_parser("send-keys", help="Send keyboard shortcut")
    sp.add_argument("key", help="Key to send (e.g., 'c', 'e')")

    # menu-click
    sp = sub.add_parser("menu-click", help="Click menu item")
    sp.add_argument("app_name", help="Application name")

    # chrome-open
    sp = sub.add_parser("chrome-open", help="Open URL in Chrome")
    sp.add_argument("url", help="URL to open")

    # chrome-open-tab
    sp = sub.add_parser("chrome-open-tab", help="Open URL in new Chrome tab")
    sp.add_argument("url", help="URL to open")

    return p.parse_args()


def jxa_run(subcommand, args=None):
    """Run a JXA subcommand and return (success, output, stderr)."""
    cmd = ["osascript", "-l", "JavaScript", JXA_HELPER, subcommand]
    if args:
        cmd.extend(args)
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15
        )
        output = result.stdout.strip()
        stderr = result.stderr.strip()
        return result.returncode == 0, output, stderr
    except Exception as e:
        return False, "", str(e)


def main():
    args = parse_args()

    # Build JXA arguments
    jxa_args = []
    if args.command in ("app-running", "app-launch", "app-show", "app-activate"):
        jxa_args.append(args.app_name)
    elif args.command == "send-keys":
        jxa_args.append(args.key)
        if args.modifiers:
            jxa_args.append("--modifiers")
            jxa_args.append(args.modifiers)
    elif args.command == "menu-click":
        jxa_args.append(args.app_name)
        if args.menu:
            jxa_args.append("--menu")
            jxa_args.append(args.menu)
    elif args.command in ("chrome-open", "chrome-open-tab"):
        jxa_args.append(args.url)

    success, output, stderr = jxa_run(args.command, jxa_args)

    if args.json:
        result = {
            "success": success,
            "command": args.command,
            "output": output,
            "stderr": stderr,
        }
        print(json.dumps(result, indent=2))
    else:
        if output:
            print(output)
        if stderr:
            print(stderr, file=sys.stderr)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
