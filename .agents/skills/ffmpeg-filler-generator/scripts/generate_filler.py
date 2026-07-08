#!/usr/bin/env python3
"""
generate_filler.py — Generate a filler/transition video segment: black background,
centered text overlay, silent audio, with configurable codecs and duration.

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §2.3.
Requires: Pillow (python3 -m pip install Pillow)

Usage:
  python3 generate_filler.py \
      --width 1920 --height 1080 \
      --fps 30/1 --sample-rate 48000 \
      --duration 3 \
      --text "Recording interrupted" \
      --subtext "— content missing —" \
      --output filler.webm
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


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


def generate_overlay_image(
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


def generate_filler(
    width: int,
    height: int,
    fps: str,
    sample_rate: str,
    duration_sec: int,
    overlay_png: str,
    output_path: str,
    codec_video: str,
    codec_audio: str,
) -> None:
    """Generate a filler video with black background + centered text overlay + silent audio."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s={width}x{height}:r={fps}:d={duration_sec}",
        "-f", "lavfi",
        "-i", f"anullsrc=r={sample_rate}:cl=stereo:d={duration_sec}",
        "-i", overlay_png,
        "-filter_complex", "[0:v][2:v]overlay=0:0",
        "-c:v", codec_video,
        "-crf", "10",
        "-b:v", "0",
        "-c:a", codec_audio,
        "-b:a", "256k",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: filler generation failed (exit {result.returncode})", file=sys.stderr)
        for line in result.stderr.strip().splitlines()[-10:]:
            print(f"  ffmpeg: {line}", file=sys.stderr)
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a filler/transition video segment (black + text + silent audio).",
    )
    parser.add_argument("--width", type=int, required=True, help="Video width in pixels.")
    parser.add_argument("--height", type=int, required=True, help="Video height in pixels.")
    parser.add_argument("--fps", default="30/1", help="Frame rate (default: 30/1).")
    parser.add_argument("--sample-rate", default="48000", help="Audio sample rate in Hz (default: 48000).")
    parser.add_argument("--duration", type=int, required=True, help="Filler duration in seconds.")
    parser.add_argument("--text", default="Recording interrupted", help="Primary text displayed on the filler.")
    parser.add_argument("--subtext", default="— content missing —", help="Secondary subtitle text.")
    parser.add_argument("--codec-video", default="libvpx-vp9", help="Video codec (default: libvpx-vp9).")
    parser.add_argument("--codec-audio", default="libopus", help="Audio codec (default: libopus).")
    parser.add_argument("--output", required=True, help="Path for the output filler video file.")
    args = parser.parse_args()

    output_dir = os.path.dirname(args.output) or "."
    os.makedirs(output_dir, exist_ok=True)

    # Generate overlay PNG
    png_path = os.path.join(output_dir, ".filler_overlay.png")
    print(f"Generating overlay image ({args.width}x{args.height})...")
    generate_overlay_image(
        width=args.width,
        height=args.height,
        text=args.text,
        subtext=args.subtext,
        output_png=png_path,
    )

    # Generate filler video
    print(f"Generating filler video ({args.duration}s, {args.codec_video}/{args.codec_audio})...")
    generate_filler(
        width=args.width,
        height=args.height,
        fps=args.fps,
        sample_rate=args.sample_rate,
        duration_sec=args.duration,
        overlay_png=png_path,
        output_path=args.output,
        codec_video=args.codec_video,
        codec_audio=args.codec_audio,
    )

    # Clean up overlay PNG
    if os.path.isfile(png_path):
        os.unlink(png_path)

    print(f"OK: filler video written to {args.output}")


if __name__ == "__main__":
    main()
