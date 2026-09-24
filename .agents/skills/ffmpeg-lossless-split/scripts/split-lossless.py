#!/usr/bin/env python3
"""
split-lossless.py — Losslessly split a media file at a timestamp using ffmpeg -c copy.

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §2.3.
Uses: ffprobe (for duration/stream info), ffmpeg (for split/trim).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile


def parse_time(t: str) -> float:
    t = t.strip()
    if ":" in t:
        parts = [float(p) for p in t.split(":")]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
    return float(t)


def format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds - (h * 3600 + m * 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:06.3f}"
    return f"{m}:{s:06.3f}"


def probe_format(path: str) -> dict:
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format",
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
    duration = float(data["format"]["duration"])

    streams = data.get("streams", [])
    video = next((s for s in streams if s["codec_type"] == "video"), None)
    audio = next((s for s in streams if s["codec_type"] == "audio"), None)
    codec_summary = []
    if video:
        codec_summary.append(f"video: {video['codec_name']} {video.get('width','?')}x{video.get('height','?')}")
    if audio:
        codec_summary.append(f"audio: {audio['codec_name']} {audio.get('sample_rate','?')}Hz")

    return {
        "duration": duration,
        "codec_summary": ", ".join(codec_summary),
    }


def run_ffmpeg_split(
    input_path: str,
    output_path: str,
    ss: str,
    to: str | None,
) -> None:
    cmd = ["ffmpeg", "-y", "-i", input_path, "-c", "copy"]
    cmd += ["-ss", ss]
    if to:
        cmd += ["-to", to]
    cmd.append(output_path)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        lines = result.stderr.strip().splitlines()[-5:]
        print(f"ERROR: ffmpeg split failed (exit {result.returncode})", file=sys.stderr)
        for line in lines:
            print(f"  ffmpeg: {line}", file=sys.stderr)
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Losslessly split or extract a segment from a media file.",
    )
    parser.add_argument("--input", required=True, help="Path to source media file.")
    parser.add_argument(
        "--split-at",
        required=True,
        help="Timestamp to split at (HH:MM:SS, MM:SS, or seconds).",
    )
    parser.add_argument(
        "--to",
        help="End timestamp for segment extraction (HH:MM:SS, MM:SS, or seconds).",
    )
    parser.add_argument("--output", help="Output path (single file, requires --to).")
    parser.add_argument(
        "--output-prefix",
        help="Prefix for split output files (e.g. 'output' → output_part1.ext, output_part2.ext).",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only validate the timestamps without executing the split.",
    )
    args = parser.parse_args()

    if not args.output and not args.output_prefix and not args.verify_only:
        parser.error("specify --output (with --to) or --output-prefix (split) or --verify-only")

    if args.output and not args.to:
        parser.error("--output requires --to (extract a segment from --split-at to --to)")

    if args.output_prefix and args.to:
        parser.error("--output-prefix with --to is ambiguous; use --output for segment extraction")

    if not os.path.isfile(args.input):
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    split_time = parse_time(args.split_at)
    info = probe_format(args.input)
    duration = info["duration"]

    if split_time <= 0:
        print("ERROR: --split-at must be > 0", file=sys.stderr)
        sys.exit(1)

    if split_time >= duration:
        print(
            f"ERROR: --split-at {args.split_at} ({format_time(split_time)}) "
            f"exceeds file duration {format_time(duration)}",
            file=sys.stderr,
        )
        sys.exit(1)

    to_time = None
    if args.to:
        to_time = parse_time(args.to)
        if to_time <= split_time:
            print("ERROR: --to must be after --split-at", file=sys.stderr)
            sys.exit(1)
        if to_time > duration:
            to_time = duration

    print(f"  input: {args.input}")
    print(f"  duration: {format_time(duration)}")
    print(f"  split-at: {args.split_at} ({format_time(split_time)})")
    if to_time:
        print(f"  to: {args.to} ({format_time(to_time)})")
    print(f"  streams: {info['codec_summary']}")

    if args.verify_only:
        print("OK: timestamps valid (verify-only mode)")
        sys.exit(0)

    if args.output_prefix:
        ext = os.path.splitext(args.input)[1] or ".webm"
        part1 = f"{args.output_prefix}_part1{ext}"
        part2 = f"{args.output_prefix}_part2{ext}"

        print(f"  output (part 1): {part1}")
        print(f"  output (part 2): {part2}")

        print("Extracting part 1 (0 to split-at)...")
        run_ffmpeg_split(args.input, part1, "0", args.split_at)

        print("Extracting part 2 (split-at to end)...")
        run_ffmpeg_split(args.input, part2, args.split_at, None)

        print(f"OK: files written: {part1}, {part2}")
    else:
        run_ffmpeg_split(args.input, args.output, args.split_at, args.to)
        print(f"OK: segment written: {args.output}")


if __name__ == "__main__":
    main()
