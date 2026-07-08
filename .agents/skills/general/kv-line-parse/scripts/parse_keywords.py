import argparse
import json
import re
import sys


def parse_keywords(path_or_stream):
    mapping = {}
    for line in path_or_stream:
        line = line.strip()
        if not line:
            continue
        m = re.match(r'\"([^\"]+)\"\s+(\S+)', line)
        if m:
            mapping[m.group(1)] = m.group(2)
        else:
            parts = line.split(None, 1)
            if len(parts) == 2:
                mapping[parts[0]] = parts[1]
    return mapping


def main():
    parser = argparse.ArgumentParser(
        description="Parse key-value line format (quoted 'desc' value or unquoted name value) to JSON"
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to keywords file (default: stdin)"
    )
    args = parser.parse_args()

    try:
        if args.file:
            with open(args.file, encoding="utf-8") as f:
                result = parse_keywords(f)
        else:
            result = parse_keywords(sys.stdin)

        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
