"""
generate-content-guard-patterns.py — Generate fnmatch permission patterns
with correct last-match-wins ordering for commands that have dangerous
argument forms fnmatch alone cannot filter.

Given a command name and one or more dangerous substrings, produces a JSON
permission object where:
  1. The catch-all "*": "ask" comes first
  2. The broad allow "C *": "allow" comes second
  3. Each dangerous-substring pattern "C *S*": "<action>" follows, in order

Usage:
  python3 generate-content-guard-patterns.py awk --dangerous system --dangerous -f --action ask --display
  python3 generate-content-guard-patterns.py awk --dangerous system -f --action ask --display
  python3 generate-content-guard-patterns.py find --dangerous -delete -exec --action ask --output config.json
"""
import argparse
import json
import sys
from typing import Dict, List


def generate_patterns(
    command: str,
    dangerous: List[str],
    action: str = "ask",
    base_action: str = "allow",
) -> Dict[str, str]:
    patterns: Dict[str, str] = {}
    patterns["*"] = "ask"
    patterns[f"{command} *"] = base_action
    for substring in dangerous:
        patterns[f"{command} *{substring}*"] = action
    return patterns


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate fnmatch content-guard permission patterns"
    )
    parser.add_argument("command", help="Command name (e.g., awk, find, sort)")
    parser.add_argument(
        "--dangerous", "-d",
        action="append",
        default=[],
        dest="dangerous",
        help="Dangerous substring to guard against (repeatable). "
             "Substrings starting with dash can be passed as -d -f or --dangerous=-f",
    )
    parser.add_argument(
        "--action",
        default="ask",
        choices=["ask", "deny"],
        help="Action for dangerous patterns (default: ask)",
    )
    parser.add_argument(
        "--base-action",
        default="allow",
        choices=["allow", "ask", "deny"],
        help="Action for the broad allow pattern (default: allow)",
    )
    parser.add_argument(
        "--display",
        action="store_true",
        help="Display patterns in human-readable format",
    )
    parser.add_argument(
        "--output",
        help="Write JSON output to file instead of stdout",
    )

    args = parser.parse_args()

    if not args.dangerous:
        parser.error("at least one --dangerous substring is required")

    patterns = generate_patterns(
        command=args.command,
        dangerous=args.dangerous,
        action=args.action,
        base_action=args.base_action,
    )

    output = json.dumps(patterns, indent=2)

    if args.display:
        print(f"Content-guard patterns for '{args.command}':")
        print("  Insertion order (last-match-wins):")
        items = list(patterns.items())
        for i, (pattern, act) in enumerate(items):
            marker = "← LAST (wins)" if i == len(items) - 1 else "→"
            print(f"  {i+1}. \"{pattern}\": \"{act}\"  {marker}")
        print()
        print("JSON:")
        print(output)
    elif args.output:
        with open(args.output, "w") as f:
            f.write(output + "\n")
        print(f"Written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
