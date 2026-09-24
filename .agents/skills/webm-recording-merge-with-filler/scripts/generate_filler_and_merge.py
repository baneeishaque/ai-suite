#!/usr/bin/env python3
"""
generate_filler_and_merge.py — Merge discontinuous webm recording segments with a
filler transition between each pair, then losslessly concatenate.

Composes two base skills:
  1. ffmpeg-filler-generator  — generates the filler transition video
  2. ffmpeg-lossless-concat   — losslessly concatenates source + filler segments

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §2.3.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile


def probe_video_info(path: str) -> dict:
    """Run ffprobe on *path* and return relevant stream parameters."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        "-show_format",
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
    video = None
    audio = None
    for s in data.get("streams", []):
        if s["codec_type"] == "video" and video is None:
            video = s
        elif s["codec_type"] == "audio" and audio is None:
            audio = s

    if video is None:
        print(f"ERROR: no video stream found in {path}", file=sys.stderr)
        sys.exit(1)

    info: dict = {
        "width": video["width"],
        "height": video["height"],
        "r_frame_rate": video.get("r_frame_rate", "30/1"),
        "duration": float(data["format"]["duration"]),
    }
    if audio:
        info["sample_rate"] = audio.get("sample_rate", "48000")
        info["channels"] = audio.get("channels", 2)
    else:
        info["sample_rate"] = "48000"
        info["channels"] = 2

    return info


def build_concat_file(segment_paths: list[str], filler_webm: str) -> str:
    """Build the file list (plain paths, one per line) for the base skill.

    All paths are resolved to absolute form so the base script (which reads
    this list and writes a concat file to a temp directory in /tmp) can
    resolve them regardless of its working directory. Filler is inserted
    between each pair of consecutive segments (N segments -> N-1 fillers).
    """
    fd, tmp_path = tempfile.mkstemp(suffix=".txt", prefix="concat_list_")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        for i, path in enumerate(segment_paths):
            fh.write(f"{os.path.abspath(path)}\n")
            if i < len(segment_paths) - 1 and filler_webm:
                fh.write(f"{os.path.abspath(filler_webm)}\n")
    return tmp_path


def resolve_base_script(script_dir: str, skill_dir: str, script_path: str) -> str:
    """Resolve a base skill script path relative to this script's location."""
    result = os.path.normpath(os.path.join(script_dir, "..", "..", skill_dir, "scripts", script_path))
    if not os.path.isfile(result):
        print(f"ERROR: base skill script not found at {result}", file=sys.stderr)
        sys.exit(1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge webm recording segments with a filler transition.",
    )
    parser.add_argument(
        "--segment",
        required=True,
        action="append",
        dest="segments",
        help="Path to a webm segment (repeatable, in play order).",
    )
    parser.add_argument(
        "--filler-text",
        default="Recording interrupted",
        help="Primary text for the filler (default: 'Recording interrupted').",
    )
    parser.add_argument(
        "--filler-subtext",
        default="— content missing —",
        help="Subtitle text for the filler (default: '— content missing —').",
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
        help="Path for the merged output webm file.",
    )
    args = parser.parse_args()

    if len(args.segments) < 2:
        parser.error("need at least two --segment files")

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Resolve base skill scripts
    filler_script = resolve_base_script(
        script_dir, "ffmpeg-filler-generator", "generate_filler.py"
    )
    concat_script = resolve_base_script(
        script_dir, "ffmpeg-lossless-concat", "ffmpeg_lossless_concat.py"
    )

    # Probe first segment for video properties
    print("Probing first segment for video properties...")
    info = probe_video_info(args.segments[0])
    print(f"  resolution: {info['width']}x{info['height']}")
    print(f"  fps: {info['r_frame_rate']}")
    print(f"  sample_rate: {info['sample_rate']}")

    # Generate filler via the ffmpeg-filler-generator base skill
    filler_path = os.path.join(
        os.path.dirname(os.path.abspath(args.output)) or ".",
        ".filler_segment.webm",
    )
    print("Generating filler via ffmpeg-filler-generator...")
    filler_cmd = [
        sys.executable, filler_script,
        "--width", str(info["width"]),
        "--height", str(info["height"]),
        "--fps", info["r_frame_rate"],
        "--sample-rate", info["sample_rate"],
        "--duration", str(args.filler_duration),
        "--text", args.filler_text,
        "--subtext", args.filler_subtext,
        "--output", filler_path,
    ]
    filler_result = subprocess.run(filler_cmd, capture_output=True, text=True)
    if filler_result.stdout:
        for line in filler_result.stdout.strip().splitlines():
            print(f"  filler: {line}")
    if filler_result.stderr:
        for line in filler_result.stderr.strip().splitlines():
            print(f"  filler: {line}", file=sys.stderr)
    if filler_result.returncode != 0:
        print(f"ERROR: filler generation failed (exit {filler_result.returncode})", file=sys.stderr)
        sys.exit(filler_result.returncode)

    # Build concat file list
    print("Building concat file list...")
    concat_list = build_concat_file(
        segment_paths=args.segments,
        filler_webm=filler_path,
    )

    # Invoke base skill for lossless concat
    print("Invoking base skill for lossless concat...")
    concat_result = subprocess.run(
        [sys.executable, concat_script, "--files", concat_list, "--output", args.output],
        capture_output=True,
        text=True,
    )
    if concat_result.stdout:
        for line in concat_result.stdout.strip().splitlines():
            print(f"  base: {line}")
    if concat_result.stderr:
        for line in concat_result.stderr.strip().splitlines():
            print(f"  base: {line}", file=sys.stderr)

    # Clean up temp files
    for tmp in [filler_path, concat_list]:
        if os.path.isfile(tmp):
            os.unlink(tmp)

    if concat_result.returncode != 0:
        print(f"ERROR: merge failed (base script exit {concat_result.returncode})", file=sys.stderr)
        sys.exit(concat_result.returncode)

    print(f"OK: merged output written to {args.output}")


if __name__ == "__main__":
    main()
