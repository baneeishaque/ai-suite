#!/usr/bin/env python3
"""
create-url-shortcut.py — Create an HTML redirect shortcut file for a given URL.

Creates a self-contained .html file that, when opened, redirects the browser
to the target URL. Works on all operating systems.

Usage:
    python3 create-url-shortcut.py --url "https://youtu.be/abc123" --name "my-video"
    python3 create-url-shortcut.py --url "https://example.com" --name "example" --output-dir /tmp
"""
import argparse
import os
import sys


def parse_args():
    p = argparse.ArgumentParser(description="Create an HTML URL shortcut file")
    p.add_argument("--url", required=True, help="Target URL")
    p.add_argument("--name", required=True, help="Shortcut filename (without extension)")
    p.add_argument("--output-dir", default=os.getcwd(), help="Output directory (default: current dir)")
    return p.parse_args()


def main():
    args = parse_args()

    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, f"{args.name}.html")

    content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{args.name}</title>
  <meta http-equiv="refresh" content="0; url={args.url}">
</head>
<body>
  <p><a href="{args.url}">{args.name}</a></p>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(filepath)
    sys.exit(0)


if __name__ == "__main__":
    main()
