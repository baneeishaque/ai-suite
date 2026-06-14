#!/usr/bin/env python3
"""
generate_filler_and_merge.py — Generate a filler transition between webm recording
segments and losslessly concatenate them using the ffmpeg-lossless-concat base skill.

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §2.3.
Requires: Pillow (python3 -m pip install Pillow)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap


def find_font(size: int):
    """Return the best available truetype font, or fall back to default bitmap."""
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.isfile(path):
            from PIL import ImageFont
            return ImageFont.truetype(path, size)
    from PIL import ImageFont
    return ImageFont.load_default()


def generate_filler_image(
    width: int,
    height: int,
    text: str,
    subtext: str,
    output_png: str,
) -> None:
    """Create a black PNG with centered text using Pillow."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(img)

    font_lg = find_font(max(56, width // 40))
    font_sm = find_font(max(40, width // 56))

    # Measure text size
    bbox1 = draw.textbbox((0, 0), text, font=font_lg)
    text_w1 = bbox1[2] - bbox1[0]
    text_h1 = bbox1[3] - bbox1[1]

    x1 = (width - text_w1) // 2
    y1 = (height // 2) - text_h1 - 20

    draw.text((x1, y1), text, fill="white", font=font_lg)

    if subtext:
        bbox2 = draw.textbbox((0, 0), subtext, font=font_sm)
        text_w2 = bbox2[2] - bbox2[0]
        x2 = (width - text_w2) // 2
        y2 = (height // 2) + 10
        draw.text((x2, y2), subtext, fill="#cccccc", font=font_sm)

    img.save(output_png)
    print(f"  filler image saved: {output_png}")


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


def generate_filler_video(
    width: int,
    height: int,
    fps: str,
    sample_rate: str,
    duration_sec: int,
    overlay_png: str,
    output_webm: str,
) -> None:
    """Generate a short filler webm with black background + text overlay."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s={width}x{height}:r={fps}:d={duration_sec}",
        "-f", "lavfi",
        "-i", f"anullsrc=r={sample_rate}:cl=stereo:d={duration_sec}",
        "-i", overlay_png,
        "-filter_complex", "[0:v][2:v]overlay=0:0",
        "-c:v", "libvpx-vp9",
        "-crf", "10",
        "-b:v", "0",
        "-c:a", "libopus",
        "-b:a", "256k",
        output_webm,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: filler generation failed (exit {result.returncode})", file=sys.stderr)
        for line in result.stderr.strip().splitlines()[-10:]:
            print(f"  ffmpeg: {line}", file=sys.stderr)
        sys.exit(result.returncode)
    print(f"  filler video saved: {output_webm}")


def build_concat_file(segment_paths: list[str], filler_webm: str, output_path: str) -> str:
    """Build the file list (plain paths, one per line) for the base skill.

    The base ffmpeg-lossless-concat script reads plain paths (NOT ffmpeg concat
    format) from the --files input.
    """
    fd, tmp_path = tempfile.mkstemp(suffix=".txt", prefix="concat_list_")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        for i, path in enumerate(segment_paths):
            fh.write(f"{path}\n")
            # Insert filler after the first segment and before the next
            if i == 0 and filler_webm:
                fh.write(f"{filler_webm}\n")
    return tmp_path


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

    # Locate base script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_script = os.path.join(
        script_dir, "..", "..", "ffmpeg-lossless-concat", "scripts", "ffmpeg_lossless_concat.py"
    )
    base_script = os.path.normpath(base_script)
    if not os.path.isfile(base_script):
        print(
            f"ERROR: base skill script not found at {base_script}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Probe first segment for video properties
    print("Probing first segment for video properties...")
    info = probe_video_info(args.segments[0])
    print(f"  resolution: {info['width']}x{info['height']}")
    print(f"  fps: {info['r_frame_rate']}")
    print(f"  sample_rate: {info['sample_rate']}")

    # Generate filler assets
    print("Generating filler overlay image...")
    png_path = os.path.join(
        os.path.dirname(args.output) or ".",
        ".filler_overlay.png",
    )
    generate_filler_image(
        width=info["width"],
        height=info["height"],
        text=args.filler_text,
        subtext=args.filler_subtext,
        output_png=png_path,
    )

    filler_webm_path = os.path.join(
        os.path.dirname(args.output) or ".",
        ".filler_segment.webm",
    )
    print("Generating filler video...")
    generate_filler_video(
        width=info["width"],
        height=info["height"],
        fps=info["r_frame_rate"],
        sample_rate=info["sample_rate"],
        duration_sec=args.filler_duration,
        overlay_png=png_path,
        output_webm=filler_webm_path,
    )

    # Build concat file list
    print("Building concat file list...")
    concat_list = build_concat_file(
        segment_paths=args.segments,
        filler_webm=filler_webm_path,
        output_path=args.output,
    )

    # Invoke base skill
    print("Invoking base skill for lossless concat...")
    base_result = subprocess.run(
        [sys.executable, base_script, "--files", concat_list, "--output", args.output],
        capture_output=True,
        text=True,
    )
    # Print base skill output
    if base_result.stdout:
        for line in base_result.stdout.strip().splitlines():
            print(f"  base: {line}")
    if base_result.stderr:
        for line in base_result.stderr.strip().splitlines():
            print(f"  base: {line}", file=sys.stderr)

    # Clean up temp files
    for tmp in [png_path, filler_webm_path, concat_list]:
        if os.path.isfile(tmp):
            os.unlink(tmp)

    if base_result.returncode != 0:
        print(f"ERROR: merge failed (base script exit {base_result.returncode})", file=sys.stderr)
        sys.exit(base_result.returncode)

    print(f"OK: merged output written to {args.output}")


if __name__ == "__main__":
    main()
