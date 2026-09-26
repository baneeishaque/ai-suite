#!/usr/bin/env python3
"""Parse an iCalendar (.ics) file into a JSON event spec.

Base primitive for the calendar/ skill domain. Reads a .ics file, unfolds
physical lines (RFC 5545 section 3.1), unescapes TEXT values, parses
properties and parameters, nests VALARM sub-components per event, and emits
a JSON document on stdout.

Handles multi-VEVENT calendars. When a TZID parameter is resolvable via
zoneinfo, the datetime object additionally carries computed `utc` and `iso`
forms (the ISO form includes the local offset, e.g. 2026-09-26T19:00:00+05:30).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UNESCAPE_MAP = {"n": "\n", "N": "\n"}


class ParseError(Exception):
    """Raised for any parse or IO failure (maps to exit code 1)."""


def unfold(text: str) -> str:
    """Join folded physical lines: CRLF normalization then LF+space removal."""
    return text.replace("\r\n", "\n").replace("\n ", "")


def unescape_text(value: str) -> str:
    """Reverse RFC 5545 TEXT escaping in a single pass.

    The single-pass group replacement is correct for both `\\n` (escaped
    newline) and `\\\\n` (escaped backslash followed by a literal `n`).
    """
    return re.sub(r"\\(.)", lambda m: UNESCAPE_MAP.get(m.group(1), m.group(1)), value)


def parse_property(line: str) -> tuple[str, dict[str, str], str]:
    """Split NAME;PARAM=VALUE:VALUE into (NAME, params, value)."""
    if ":" not in line:
        raise ParseError(f"property line without ':': {line!r}")
    head, value = line.split(":", 1)
    parts = head.split(";")
    name = parts[0].upper()
    params: dict[str, str] = {}
    for part in parts[1:]:
        if "=" not in part:
            raise ParseError(f"malformed parameter: {part!r}")
        key, param_value = part.split("=", 1)
        params[key.upper()] = param_value
    return name, params, value


def split_escaped_commas(value: str) -> list[str]:
    """Split a comma-separated list, honoring backslash-escaped commas."""
    parts: list[str] = []
    current = ""
    index = 0
    while index < len(value):
        char = value[index]
        if char == "\\" and index + 1 < len(value):
            current += value[index : index + 2]
            index += 2
            continue
        if char == ",":
            parts.append(current)
            current = ""
        else:
            current += char
        index += 1
    parts.append(current)
    return parts


def datetime_value(value: str, params: dict[str, str]) -> dict:
    """Build the datetime dict for DTSTART/DTEND, adding utc/iso when resolvable."""
    result: dict = {"value": value}
    tzid = params.get("TZID")
    if tzid:
        result["tzid"] = tzid
    if re.fullmatch(r"\d{8}T\d{6}Z", value):
        parsed = dt.datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(
            tzinfo=dt.timezone.utc
        )
        result["utc"] = value
        result["iso"] = parsed.isoformat()
        return result
    if tzid and re.fullmatch(r"\d{8}T\d{6}", value):
        try:
            zone = ZoneInfo(tzid)
        except ZoneInfoNotFoundError:
            return result
        local = dt.datetime.strptime(value, "%Y%m%dT%H%M%S").replace(tzinfo=zone)
        result["utc"] = local.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        result["iso"] = local.isoformat()
    return result


def parse_calendar(text: str) -> dict:
    """Parse unfolded content lines into the output document."""
    calendar: dict = {"prodid": None, "version": None, "method": None}
    timezones: list[str] = []
    events: list[dict] = []
    current_event: dict | None = None
    current_alarm: dict | None = None
    in_timezone = False

    for line in unfold(text).split("\n"):
        if not line.strip():
            continue
        name, params, value = parse_property(line)
        upper = value.upper()
        if name == "BEGIN":
            if upper == "VEVENT":
                current_event = {"alarms": []}
            elif upper == "VALARM":
                current_alarm = {}
            elif upper == "VTIMEZONE":
                in_timezone = True
            continue
        if name == "END":
            if upper == "VEVENT":
                if current_event is not None:
                    events.append(current_event)
                current_event = None
            elif upper == "VALARM":
                if current_alarm is not None and current_event is not None:
                    current_event["alarms"].append(current_alarm)
                current_alarm = None
            elif upper == "VTIMEZONE":
                in_timezone = False
            continue
        if name == "TZID" and in_timezone:
            timezones.append(value)
            continue
        target = current_alarm if current_alarm is not None else current_event
        if target is None:
            if name == "PRODID":
                calendar["prodid"] = value
            elif name == "VERSION":
                calendar["version"] = value
            elif name == "METHOD":
                calendar["method"] = value
            continue
        if name in ("DTSTART", "DTEND"):
            target[name.lower()] = datetime_value(value, params)
        elif name in ("UID", "DTSTAMP", "SUMMARY", "STATUS", "CLASS", "TRANSP"):
            target[name.lower()] = value
        elif name in ("DESCRIPTION", "LOCATION"):
            target[name.lower()] = unescape_text(value)
        elif name == "URL":
            target["url"] = value
        elif name == "ORGANIZER":
            email = value[7:] if value.lower().startswith("mailto:") else value
            target["organizer"] = {"cn": params.get("CN", ""), "email": email}
        elif name == "CATEGORIES":
            target["categories"] = [
                unescape_text(item) for item in split_escaped_commas(value)
            ]
        elif name == "ACTION":
            target["action"] = value
        elif name == "TRIGGER":
            target["trigger"] = value
    return {"calendar": calendar, "timezones": timezones, "events": events}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Parse an iCalendar .ics file into a JSON event spec."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--pretty", action="store_true", help="pretty-print the JSON")
    args = parser.parse_args(argv)

    try:
        text = args.input.read_text(encoding="utf-8")
        document = parse_calendar(text)
    except (ParseError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    indent = 2 if args.pretty else None
    print(json.dumps(document, indent=indent, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
