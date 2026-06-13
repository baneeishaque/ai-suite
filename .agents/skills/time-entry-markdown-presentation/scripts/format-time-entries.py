import json
import sys
import argparse
import re
from datetime import datetime, timedelta


def parse_time(t):
    parts = t.strip().split(":")
    h, m = int(parts[0]), int(parts[1])
    s = int(parts[2]) if len(parts) > 2 else 0
    return h, m, s


def time_to_minutes(t):
    h, m, s = parse_time(t)
    return h * 60 + m + s / 60.0


def format_duration(minutes):
    h = int(minutes // 60)
    m = int(minutes % 60)
    s = round((minutes - int(minutes)) * 60)
    if h > 0:
        if s:
            return f"{h}h {m:02d}m {s}s"
        return f"{h}h {m:02d}m"
    if m > 0:
        if s:
            return f"{m}m {s}s"
        return f"{m}m"
    return f"{s}s"


def calc_duration(start, end):
    smin = time_to_minutes(start)
    emin = time_to_minutes(end)
    if emin < smin:
        emin += 24 * 60
    return emin - smin


def render_table(entries, totals=None):
    lines = []
    lines.append("| Time | Duration | Title | Description |")
    lines.append("|------|----------|-------|-------------|")
    for e in entries:
        dur_str = format_duration(e["duration"])
        time_str = f"{e['start']} \u2013 {e['end']}"
        title = e.get("title", "")
        desc = e.get("description", "")
        lines.append(f"| {time_str} | {dur_str} | {title} | {desc} |")
    if totals:
        for row in totals:
            lines.append(f"| {row['time']} | {row['duration']} | {row['title']} | {row['description']} |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Format time entries as a markdown table.")
    parser.add_argument("--targeted", type=str, default=None, help="Targeted time (e.g. '6h')")
    parser.add_argument("--label-targeted", type=str, default="Targeted", help="Label for targeted row")
    parser.add_argument("--label-actual", type=str, default="Actual total", help="Label for actual total row")
    parser.add_argument("--label-remaining", type=str, default="Remaining", help="Label for remaining row")
    args = parser.parse_args()

    raw = sys.stdin.read()
    entries = json.loads(raw)

    parsed = []
    total_minutes = 0.0
    for e in entries:
        dur = calc_duration(e["start"], e["end"])
        e["duration"] = dur
        total_minutes += dur
        parsed.append(e)

    totals = []
    actual_str = format_duration(total_minutes)
    totals.append({"time": "", "duration": f"**{actual_str}**", "title": f"**{args.label_actual}**", "description": ""})

    if args.targeted:
        target_match = re.match(r"(\d+(?:\.\d+)?)\s*h", args.targeted)
        if target_match:
            target_minutes = float(target_match.group(1)) * 60
            target_str = format_duration(target_minutes)
            remaining = total_minutes - target_minutes
            remaining_str = format_duration(abs(remaining))
            sign = "-" if remaining > 0 else ""
            totals.append({"time": "", "duration": f"**{target_str}**", "title": f"**{args.label_targeted}**", "description": ""})
            totals.append({"time": "", "duration": f"**{sign}{remaining_str}**", "title": f"**{args.label_remaining}**", "description": ""})

    sys.stdout.write(render_table(parsed, totals))


if __name__ == "__main__":
    main()
