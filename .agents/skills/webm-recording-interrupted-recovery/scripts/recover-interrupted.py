#!/usr/bin/env python3
"""
recover-interrupted.py — Recover from a recording interruption by trimming the
continuation and merging with a filler transition.

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §2.3.
Requires: Pillow via the filler-merge composer.
Composes: ffmpeg-lossless-split (base) + webm-recording-merge-with-filler (composer).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile


def resolve_script(repo_relative: str) -> str:
    """Resolve a script path relative to this script's location."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(script_dir, "..", "..", repo_relative))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover from a recording interruption: trim continuation and merge with filler.",
    )
    parser.add_argument(
        "--main",
        required=True,
        help="Path to the main recording (first segment, before the interruption).",
    )
    parser.add_argument(
        "--continuation",
        required=True,
        help="Path to the continuation recording (post-interruption recording, may include pre-interruption overlap).",
    )
    parser.add_argument(
        "--split-at",
        required=True,
        help="Timestamp where the interruption occurred (HH:MM:SS, MM:SS, or seconds). "
             "Content before this in the continuation file will be trimmed.",
    )
    parser.add_argument(
        "--filler-text",
        default="Recording interrupted",
        help="Primary text for the filler (default: 'Recording interrupted').",
    )
    parser.add_argument(
        "--filler-subtext",
        default="\u2014 content missing \u2014",
        help="Subtitle text for the filler (default: '\u2014 content missing \u2014').",
    )
    parser.add_argument(
        "--filler-duration",
        type=int,
        default=3,
        help="Duration of the filler in seconds (default: 3).",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the final recovered output webm file.",
    )
    args = parser.parse_args()

    for path, label in [(args.main, "main"), (args.continuation, "continuation")]:
        if not os.path.isfile(path):
            print(f"ERROR: {label} file not found: {path}", file=sys.stderr)
            sys.exit(1)

    # Resolve scripts
    split_script = resolve_script(
        "ffmpeg-lossless-split/scripts/split-lossless.py"
    )
    filler_merge_script = resolve_script(
        "webm-recording-merge-with-filler/scripts/generate_filler_and_merge.py"
    )

    if not os.path.isfile(split_script):
        print(
            f"ERROR: split script not found at {split_script}. "
            "Ensure ffmpeg-lossless-split skill is present.",
            file=sys.stderr,
        )
        sys.exit(1)
    if not os.path.isfile(filler_merge_script):
        print(
            f"ERROR: filler-merge script not found at {filler_merge_script}. "
            "Ensure webm-recording-merge-with-filler skill is present.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Step 1: Trim the continuation recording
    output_dir = os.path.dirname(os.path.abspath(args.output)) or os.getcwd()
    fd, trimmed_path = tempfile.mkstemp(
        suffix=".webm",
        prefix=".trimmed_continuation_",
        dir=output_dir,
    )
    os.close(fd)

    print(f"Step 1: Trimming continuation recording at {args.split_at}...")
    split_cmd = [
        sys.executable,
        split_script,
        "--input", args.continuation,
        "--split-at", args.split_at,
        "--output", trimmed_path,
    ]
    split_result = subprocess.run(split_cmd, capture_output=True, text=True)
    if split_result.stdout:
        for line in split_result.stdout.strip().splitlines():
            print(f"  split: {line}")
    if split_result.stderr:
        for line in split_result.stderr.strip().splitlines():
            print(f"  split: {line}", file=sys.stderr)
    if split_result.returncode != 0:
        print(
            f"ERROR: trimming continuation failed (exit {split_result.returncode})",
            file=sys.stderr,
        )
        cleanup(trimmed_path)
        sys.exit(split_result.returncode)

    # Step 2: Merge main + filler + trimmed continuation
    print("Step 2: Merging with filler transition...")
    merge_cmd = [
        sys.executable,
        filler_merge_script,
        "--segment", args.main,
        "--segment", trimmed_path,
        "--filler-text", args.filler_text,
        "--filler-subtext", args.filler_subtext,
        "--filler-duration", str(args.filler_duration),
        "--output", args.output,
    ]
    merge_result = subprocess.run(merge_cmd, capture_output=True, text=True)
    if merge_result.stdout:
        for line in merge_result.stdout.strip().splitlines():
            print(f"  merge: {line}")
    if merge_result.stderr:
        for line in merge_result.stderr.strip().splitlines():
            print(f"  merge: {line}", file=sys.stderr)

    # Clean up trimmed temp file
    cleanup(trimmed_path)

    if merge_result.returncode != 0:
        print(
            f"ERROR: merge with filler failed (exit {merge_result.returncode})",
            file=sys.stderr,
        )
        sys.exit(merge_result.returncode)

    print(f"OK: recovered recording written to {args.output}")


def cleanup(path: str) -> None:
    try:
        if os.path.isfile(path):
            os.unlink(path)
    except OSError:
        pass


if __name__ == "__main__":
    main()
