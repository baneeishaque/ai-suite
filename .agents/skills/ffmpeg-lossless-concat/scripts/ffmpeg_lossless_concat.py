#!/usr/bin/env python3
"""
ffmpeg_lossless_concat.py — Verify codec compatibility and losslessly concatenate
media files using ffmpeg's concat demuxer with stream copy (-c copy).

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §2.3.
Default tier for new scripts; no external PyPI dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile


def probe_streams(path: str) -> list[dict]:
    """Run ffprobe on *path* and return a list of stream dicts (video + audio only)."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: ffprobe failed on {path}: {exc.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: ffprobe not found. Install ffmpeg.", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    # Keep only video and audio streams
    return [s for s in streams if s.get("codec_type") in ("video", "audio")]


def stream_key(stream: dict) -> tuple:
    """Return a comparable tuple of the stream's salient codec parameters."""
    t = stream.get("codec_type", "?")
    if t == "video":
        return (
            "video",
            stream.get("codec_name", "?"),
            stream.get("width", -1),
            stream.get("height", -1),
            stream.get("pix_fmt", "?"),
            stream.get("r_frame_rate", "?"),  # "30/1" form
        )
    elif t == "audio":
        return (
            "audio",
            stream.get("codec_name", "?"),
            stream.get("sample_rate", "?"),
            stream.get("channels", -1),
            stream.get("channel_layout", "?"),
        )
    return (t,)


def verify_compatibility(file_paths: list[str]) -> list[dict]:
    """Probe all files and check that every stream index is compatible.

    Returns the list of all probed streams (one dict per stream). Exits with
    code 1 on the first incompatibility.
    """
    all_streams: list[dict] = []

    for path in file_paths:
        if not os.path.isfile(path):
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            sys.exit(1)

    # Collect all streams
    for path in file_paths:
        streams = probe_streams(path)
        if not streams:
            print(f"ERROR: no video or audio streams found in {path}", file=sys.stderr)
            sys.exit(1)
        for s in streams:
            s["_file"] = path
        all_streams.extend(streams)

    # Group by file
    from collections import defaultdict
    by_file: dict[str, list[dict]] = defaultdict(list)
    for s in all_streams:
        by_file[s["_file"]].append(s)

    # Check that every file has the same number and type of streams
    file_names = list(by_file.keys())
    ref_counts = [(s["codec_type"], s.get("codec_name", "?")) for s in by_file[file_names[0]]]

    for fname in file_names[1:]:
        cur_counts = [(s["codec_type"], s.get("codec_name", "?")) for s in by_file[fname]]
        if cur_counts != ref_counts:
            print(
                f"ERROR: stream layout mismatch\n"
                f"  {file_names[0]}: {ref_counts}\n"
                f"  {fname}: {cur_counts}",
                file=sys.stderr,
            )
            sys.exit(1)

    # Compare parameters per-stream-index
    max_streams = max(len(streams) for streams in by_file.values())
    for idx in range(max_streams):
        ref_file = file_names[0]
        ref_stream = by_file[ref_file][idx]
        ref_key = stream_key(ref_stream)

        for fname in file_names[1:]:
            cur_stream = by_file[fname][idx]
            cur_key = stream_key(cur_stream)

            if cur_key != ref_key:
                print(
                    f"ERROR: stream {idx} mismatch\n"
                    f"  {ref_file}: {ref_key}\n"
                    f"  {fname}: {cur_key}",
                    file=sys.stderr,
                )
                sys.exit(1)

    return all_streams


def generate_concat_file(file_paths: list[str]) -> str:
    """Write an ffmpeg concat demuxer file list and return its path.

    Paths are resolved to absolute form so ffmpeg resolves them correctly
    regardless of the concat file's location (which is a temp file in /tmp
    or equivalent). Relative paths would be resolved relative to the concat
    file's directory, not the caller's cwd.
    """
    fd, tmp_path = tempfile.mkstemp(suffix=".concat.txt", prefix="ffmpeg_concat_")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        for path in file_paths:
            abs_path = os.path.abspath(path)
            # Escape single quotes per ffmpeg concat demuxer syntax:
            #   file '/path/to/file'\''with quotes.webm'
            escaped = abs_path.replace("'", "'\\''")
            fh.write(f"file '{escaped}'\n")
    return tmp_path


def run_concat(concat_file: str, output_path: str) -> None:
    """Execute ffmpeg concat with -c copy."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: ffmpeg concat failed (exit {result.returncode})", file=sys.stderr)
        if result.stderr:
            # Print last 20 lines of ffmpeg stderr
            lines = result.stderr.strip().splitlines()
            for line in lines[-20:]:
                print(f"  ffmpeg: {line}", file=sys.stderr)
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify codec compatibility and losslessly concatenate media files.",
    )
    parser.add_argument(
        "--files",
        required=True,
        help="Path to a text file listing media files, one absolute/relative path per line.",
    )
    parser.add_argument("--output", help="Path for the merged output file.")
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only check compatibility; do not run the concat.",
    )
    args = parser.parse_args()

    if not args.verify_only and not args.output:
        parser.error("--output is required unless --verify-only is set")

    # Read file list
    if not os.path.isfile(args.files):
        print(f"ERROR: --files path not found: {args.files}", file=sys.stderr)
        sys.exit(1)

    file_paths: list[str] = []
    with open(args.files, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            file_paths.append(line)

    if len(file_paths) < 2:
        print("ERROR: need at least two files to concatenate", file=sys.stderr)
        sys.exit(1)

    # Deduplicate paths for verification (same file may appear multiple times
    # in the concat list, e.g. a filler segment inserted between every pair)
    unique_paths = list(dict.fromkeys(file_paths))
    # Verify compatibility
    verify_compatibility(unique_paths)
    print("OK: all files are compatible for lossless concat")

    if args.verify_only:
        sys.exit(0)

    # Generate concat file list
    concat_file = generate_concat_file(file_paths)
    try:
        run_concat(concat_file, args.output)
        print(f"OK: merged output written to {args.output}")
    finally:
        if os.path.isfile(concat_file):
            os.unlink(concat_file)


if __name__ == "__main__":
    main()
