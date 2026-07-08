#!/usr/bin/env python3
"""
download-from-manifest.py — Download video from manifest URL via ffmpeg.

Reads from args (see --help).
Exit: 0=success, 1=failure

Tier: 1 (Python 3.12+) per scripting-language-selection-rules §Tier 1
"""
import argparse
import os
import subprocess
import sys


def parse_args():
    p = argparse.ArgumentParser(
        description="Download video from manifest URL via ffmpeg"
    )
    p.add_argument(
        "--manifest-url", required=True,
        help="Manifest, playlist, or direct video URL"
    )
    p.add_argument(
        "--output", required=True,
        help="Output file path (e.g., ~/Downloads/video.mp4)"
    )
    p.add_argument(
        "--timeout", type=int, default=600,
        help="ffmpeg timeout in seconds (default: 600)"
    )
    return p.parse_args()


def main():
    args = parse_args()
    output = os.path.expanduser(args.output)

    # Create output directory if needed
    output_dir = os.path.dirname(os.path.abspath(output))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    print(f"Downloading: {args.manifest_url[:120]}...")
    print(f"Output: {output}")

    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", args.manifest_url,
                "-codec", "copy",
                output,
            ],
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
    except subprocess.TimeoutExpired:
        print(
            f"ERROR: ffmpeg timed out after {args.timeout}s",
            file=sys.stderr,
        )
        sys.exit(1)

    if result.returncode == 0:
        size = os.path.getsize(output)
        print(
            f"Download complete: {output} "
            f"({size / (1024 * 1024):.1f} MB)"
        )
        sys.exit(0)
    else:
        print(
            f"ffmpeg failed (exit {result.returncode})",
            file=sys.stderr,
        )
        if result.stderr:
            print(result.stderr[-500:], file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
