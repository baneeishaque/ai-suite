#!/usr/bin/env python3
"""
generate-summary.py — Composer script: produce a human-readable summary of
media files sorted by epoch-ms timestamp embedded in their filenames.

Resolves the base skill script (file-glob-sort-by-regex-capture) via a
relative path anchored to this script's own location, then consumes its JSON
Lines output to build the summary.

Usage:
  python3 generate-summary.py --directory /path/to/media/files
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate a timestamp-sorted summary of media files"
    )
    p.add_argument("--directory", required=True, help="Directory containing media files")
    p.add_argument("--glob", default="video-*.webm", help="Glob pattern (default: video-*.webm)")
    p.add_argument("--regex", default=r"video-(\d+)", help="Regex with timestamp capture group (default: video-(\\\\d+))")
    p.add_argument("--output", default="video-info.txt", help="Output filename (default: video-info.txt)")
    return p.parse_args()


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_SCRIPT = os.path.normpath(
    os.path.join(SCRIPT_DIR, "../../file-glob-sort-by-regex-capture/scripts/sort-by-capture.py")
)


def epoch_ms_to_utc(ms: int) -> str:
    dt = datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")


def format_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} B"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def main() -> None:
    args = parse_args()

    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print(f"error: directory does not exist: {directory}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(BASE_SCRIPT):
        print(f"error: base script not found at: {BASE_SCRIPT}", file=sys.stderr)
        sys.exit(1)

    # ---- Step 1: Call base skill ----
    result = subprocess.run(
        [sys.executable, BASE_SCRIPT,
         "--directory", directory,
         "--glob", args.glob,
         "--regex", args.regex,
         "--sort-type", "int"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"error: base script failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    entries: list[dict] = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        entries.append(json.loads(line))

    if not entries:
        print("error: no entries returned from base script", file=sys.stderr)
        sys.exit(1)

    # ---- Step 2: Build summary ----
    total_size_bytes = sum(e["size_bytes"] for e in entries)
    total_size_hr = format_size(total_size_bytes)

    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("  VIDEO FILES — Chronological Order (Earliest to Latest)")
    lines.append(f"  Folder: {os.path.basename(directory)}")
    now_utc = datetime.now(timezone.utc).strftime("%d %b %Y")
    lines.append(f"  Generated: {now_utc}")
    lines.append("=" * 80)
    lines.append("")
    lines.append(" Unix Timestamps are in milliseconds (epoch ms).")
    lines.append("")

    # Table
    header = f" {'#':<3} | {'Filename':<40} | {'Timestamp (ms)':<18} | {'Readable Time (UTC)':<30} | {'File Size':>10}"
    sep = "-" * len(header)
    lines.append(header)
    lines.append(sep)

    prev_ms: int | None = None
    for i, e in enumerate(entries, 1):
        key_ms = int(e["key"])
        readable = epoch_ms_to_utc(key_ms)
        size_hr = format_size(e["size_bytes"])
        fname = e["filename"]
        if len(fname) > 38:
            fname = fname[:35] + "..."
        lines.append(
            f" {i:<3} | {fname:<40} | {e['key']:<18} | {readable:<30} | {size_hr:>10}"
        )
        prev_ms = key_ms

    lines.append(sep)
    lines.append("")
    lines.append("--- DETAILS ---")
    lines.append("")

    prev_ms = None
    for i, e in enumerate(entries, 1):
        key_ms = int(e["key"])
        readable = epoch_ms_to_utc(key_ms)
        size_hr = format_size(e["size_bytes"])
        lines.append(f"{i}. {e['filename']}")
        lines.append(f"   - Timestamp:   {e['key']} ms  ({readable})")
        lines.append(f"   - File Size:   {size_hr}")
        if i == 1:
            lines.append(f"   - Notes:       First/earliest file.")
        else:
            gap = key_ms - prev_ms
            gap_sec = gap / 1000.0
            if gap_sec < 60:
                lines.append(f"   - Notes:       {gap_sec:.0f} sec after #{i-1}.")
            elif gap_sec < 3600:
                lines.append(f"   - Notes:       {gap_sec/60:.1f} min after #{i-1}.")
            else:
                lines.append(f"   - Notes:       {gap_sec/3600:.2f} hr after #{i-1}.")
        lines.append("")
        prev_ms = key_ms

    # Spacing summary
    lines.append("--- TIME SPACING ---")
    lines.append("")
    prev_ms = None
    for i, e in enumerate(entries, 1):
        key_ms = int(e["key"])
        if prev_ms is not None:
            gap = key_ms - prev_ms
            gap_sec = gap / 1000.0
            if gap_sec < 60:
                lines.append(f"  #{i-1} → #{i}:     {gap_sec:.0f} sec")
            elif gap_sec < 3600:
                lines.append(f"  #{i-1} → #{i}:     {gap_sec/60:.1f} min")
            else:
                lines.append(f"  #{i-1} → #{i}:     {gap_sec/3600:.2f} hr")
        prev_ms = key_ms

    if len(entries) >= 2:
        first_ms = int(entries[0]["key"])
        last_ms = int(entries[-1]["key"])
        total_span_sec = (last_ms - first_ms) / 1000.0
        if total_span_sec < 60:
            lines.append(f"\n  Total span: {total_span_sec:.0f} sec")
        elif total_span_sec < 3600:
            lines.append(f"\n  Total span: {total_span_sec/60:.1f} min")
        else:
            hrs = int(total_span_sec // 3600)
            mins = int((total_span_sec % 3600) // 60)
            secs = int(total_span_sec % 60)
            lines.append(f"\n  Total span:  {hrs} hr {mins:02d} min {secs:02d} sec")

    lines.append("")
    lines.append("--- TOTAL ---")
    lines.append("")
    lines.append(f"  Total files: {len(entries)}")
    lines.append(f"  Total size:  {total_size_hr}")

    summary = "\n".join(lines) + "\n"

    # ---- Step 3: Write summary file ----
    output_path = os.path.join(directory, args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to: {output_path}")
    print(summary)


if __name__ == "__main__":
    main()
