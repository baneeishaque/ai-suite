#!/usr/bin/env python3
"""Generate an RFC 5545 iCalendar (.ics) file from a JSON event spec.

Base primitive for the calendar/ skill domain. Reads a JSON spec, emits a
CRLF-terminated, 75-octet-folded .ics file, and (by default) runs structural
verification assertions before exiting.

Canonical emission order (RFC 5545 does not mandate property order; this
generator fixes one order so output is deterministic):

    BEGIN:VCALENDAR / VERSION / PRODID / CALSCALE / METHOD / [VTIMEZONE]
    BEGIN:VEVENT / UID / DTSTAMP / DTSTART / DTEND / SUMMARY / DESCRIPTION /
    LOCATION / URL / ORGANIZER / CATEGORIES / STATUS / CLASS / TRANSP /
    [VALARMs] / END:VEVENT / END:VCALENDAR
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TIMEZONES_DIR = SCRIPT_DIR / "timezones"


class SpecError(Exception):
    """Raised for any spec validation or IO failure (maps to exit code 1)."""


def escape_text(value: str) -> str:
    """Escape an RFC 5545 TEXT value (backslash, semicolon, comma, newline)."""
    value = value.replace("\\", "\\\\")
    value = value.replace(";", "\\;")
    value = value.replace(",", "\\,")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return value.replace("\n", "\\n")


def fold_line(line: str, limit: int = 75) -> list[str]:
    """Fold one logical content line into physical lines of <= limit octets.

    Continuation lines begin with a single space, which counts toward the
    limit, so their content budget is limit - 1. Splitting is UTF-8 safe:
    a multi-byte character is never divided across physical lines.
    """
    chunks: list[str] = []
    current = ""
    current_octets = 0
    budget = limit
    for char in line:
        char_octets = len(char.encode("utf-8"))
        if current_octets + char_octets > budget:
            chunks.append(current)
            current = ""
            current_octets = 0
            budget = limit - 1
        current += char
        current_octets += char_octets
    chunks.append(current)
    return [chunks[0]] + [" " + chunk for chunk in chunks[1:]]


def unfold(text: str) -> str:
    """Unfold physical lines (RFC 5545 section 3.1) for verification."""
    return text.replace("\r\n ", "")


def load_timezone_block(spec: dict) -> list[str] | None:
    """Return the VTIMEZONE logical lines for spec['timezone'], or None."""
    tz = spec.get("timezone")
    if tz is None:
        return None
    if "block" in tz:
        block_text = tz["block"]
    else:
        name = tz.get("template")
        if not name:
            raise SpecError("timezone requires either 'template' or 'block'")
        if not re.fullmatch(r"[a-z0-9-]+", name):
            raise SpecError(f"invalid timezone template name: {name!r}")
        template_path = TIMEZONES_DIR / f"{name}.template"
        if not template_path.is_file():
            raise SpecError(f"timezone template not found: {template_path}")
        block_text = template_path.read_text(encoding="utf-8")
    lines = [line for line in block_text.replace("\r\n", "\n").split("\n") if line]
    if not lines or lines[0] != "BEGIN:VTIMEZONE" or lines[-1] != "END:VTIMEZONE":
        raise SpecError("timezone block must span BEGIN:VTIMEZONE..END:VTIMEZONE")
    tzid = tz.get("tzid")
    if tzid and f"TZID:{tzid}" not in lines:
        raise SpecError(f"timezone block does not declare TZID:{tzid}")
    return lines


def datetime_line(name: str, value: dict) -> tuple[str, str | None]:
    """Build a DTSTART/DTEND logical line; return (line, tzid-or-None)."""
    if "utc" in value:
        return f"{name}:{value['utc']}", None
    if "value" in value:
        tzid = value.get("tzid")
        if not tzid:
            raise SpecError(f"{name} with 'value' requires 'tzid'")
        return f"{name};TZID={tzid}:{value['value']}", tzid
    raise SpecError(f"{name} must use the 'utc' or 'value'+'tzid' form")


def build_lines(spec: dict) -> tuple[list[str], str | None]:
    """Assemble the full VCALENDAR as unfolded logical lines."""
    event = spec.get("event")
    if not isinstance(event, dict):
        raise SpecError("spec requires an 'event' object")

    tz_lines = load_timezone_block(spec)
    tzid_from_block = None
    if tz_lines:
        tzid_from_block = next(
            (line.split(":", 1)[1] for line in tz_lines if line.startswith("TZID:")),
            None,
        )

    dtstart_line, tzid_start = datetime_line("DTSTART", event.get("dtstart", {}))
    dtend_line, tzid_end = datetime_line("DTEND", event.get("dtend", {}))
    used_tzids = {tzid for tzid in (tzid_start, tzid_end) if tzid}
    if used_tzids and not tz_lines:
        raise SpecError("TZID datetimes require a 'timezone' block in the spec")
    if len(used_tzids) > 1:
        raise SpecError("exactly one TZID per calendar is supported")
    if used_tzids and tzid_from_block and next(iter(used_tzids)) != tzid_from_block:
        raise SpecError("timezone block TZID does not match the datetime TZID")

    dtstamp = event.get("dtstamp") or dt.datetime.now(dt.timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:"
        + spec.get("prodid", "-//ai-suite//ics-event-generation-from-json//EN"),
        "CALSCALE:GREGORIAN",
        "METHOD:" + spec.get("method", "PUBLISH"),
    ]
    if tz_lines:
        lines.extend(tz_lines)
    lines.extend(
        [
            "BEGIN:VEVENT",
            "UID:" + event.get("uid", ""),
            "DTSTAMP:" + dtstamp,
            dtstart_line,
            dtend_line,
            "SUMMARY:" + escape_text(event.get("summary", "")),
        ]
    )
    if event.get("description"):
        lines.append("DESCRIPTION:" + escape_text(event["description"]))
    if event.get("location"):
        lines.append("LOCATION:" + escape_text(event["location"]))
    if event.get("url"):
        lines.append("URL:" + event["url"])
    organizer = event.get("organizer")
    if organizer:
        lines.append(
            "ORGANIZER;CN="
            + organizer.get("cn", "")
            + ":mailto:"
            + organizer.get("email", "")
        )
    if event.get("categories"):
        lines.append("CATEGORIES:" + ",".join(event["categories"]))
    if event.get("status"):
        lines.append("STATUS:" + event["status"])
    if event.get("class"):
        lines.append("CLASS:" + event["class"])
    if event.get("transp"):
        lines.append("TRANSP:" + event["transp"])
    for alarm in event.get("alarms", []):
        lines.append("BEGIN:VALARM")
        lines.append("ACTION:" + alarm.get("action", "DISPLAY"))
        lines.append("DESCRIPTION:" + escape_text(alarm.get("description", "")))
        lines.append("TRIGGER:" + alarm.get("trigger", "-PT15M"))
        lines.append("END:VALARM")
    lines.extend(["END:VEVENT", "END:VCALENDAR"])
    return lines, tzid_from_block


def verify_calendar(text: str, logical_lines: list[str], expect_tzid: str | None) -> None:
    """Assert structural invariants; raise SpecError on any violation."""
    if text.count("\n") != text.count("\r\n"):
        raise SpecError("verification failed: bare LF found")
    physical_lines = text[:-2].split("\r\n")  # drop trailing CRLF
    over = [line for line in physical_lines if len(line.encode("utf-8")) > 75]
    if over:
        raise SpecError(f"verification failed: lines over 75 octets: {over[:3]}")
    expected = "\r\n".join(logical_lines) + "\r\n"
    if unfold(text) != expected:
        raise SpecError("verification failed: unfold round-trip mismatch")
    flat = unfold(text)
    required = (
        "BEGIN:VCALENDAR",
        "END:VCALENDAR",
        "BEGIN:VEVENT",
        "END:VEVENT",
        "UID:",
        "DTSTAMP:",
        "DTSTART",
        "DTEND",
        "SUMMARY:",
    )
    for token in required:
        if token not in flat:
            raise SpecError(f"verification failed: missing {token}")
    if flat.count("BEGIN:VEVENT") != 1 or flat.count("END:VEVENT") != 1:
        raise SpecError("verification failed: expected exactly one VEVENT")
    if expect_tzid:
        if f"TZID:{expect_tzid}" not in flat:
            raise SpecError("verification failed: VTIMEZONE missing")
    elif "BEGIN:VTIMEZONE" in flat:
        raise SpecError("verification failed: unexpected VTIMEZONE")
    print("VERIFY OK")
    print(f"  bytes={len(text.encode('utf-8'))}  physical_lines={len(physical_lines)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate an RFC 5545 .ics file from a JSON event spec."
    )
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--no-verify", action="store_true")
    args = parser.parse_args(argv)

    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        logical_lines, expect_tzid = build_lines(spec)
        physical: list[str] = []
        for line in logical_lines:
            physical.extend(fold_line(line))
        text = "\r\n".join(physical) + "\r\n"
        if not args.no_verify:
            verify_calendar(text, logical_lines, expect_tzid)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(text.encode("utf-8"))
    except (SpecError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"WROTE {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
