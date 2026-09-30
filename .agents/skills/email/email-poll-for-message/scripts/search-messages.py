#!/usr/bin/env python3
"""search-messages.py — one-shot IMAP search; check command for email pollers.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): pure-stdlib (imaplib + email); no pip dependencies.

Connects to an IMAP mailbox, runs a bounded search (server-side UNSEEN/SINCE
prefilter, client-side case-insensitive subject/from contains filters), and
prints one JSON object per matching message. Exits 0 when at least one match
exists — making it directly usable as the check command of a bounded poller.

`--source-file` switches to offline fixture mode: the same filters run against
a JSONL file of messages ({uid, subject, from, date, unseen}) instead of IMAP.

Usage:
    python3 search-messages.py --imap-host <host> --username <user> \
        [--subject-contains <text>] [--from-contains <text>] [--unseen]
    python3 search-messages.py --source-file fixtures.jsonl --subject-contains <text>

Exit codes:
    0  at least one message matched
    1  no matching message
    2  usage / configuration / connection error
"""
from __future__ import annotations

import argparse
import email
import email.header
import imaplib
import json
import os
import sys
from datetime import date, timedelta
from typing import NoReturn


def die(msg: str, code: int = 2) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def decode_header_value(raw: str | None) -> str:
    if not raw:
        return ""
    try:
        return str(email.header.make_header(email.header.decode_header(raw)))
    except (ValueError, email.errors.MessageError):
        return str(raw)


def passes_filters(subject: str, sender: str, unseen: bool,
                   args: argparse.Namespace) -> bool:
    if args.subject_contains and args.subject_contains.lower() not in subject.lower():
        return False
    if args.from_contains and args.from_contains.lower() not in sender.lower():
        return False
    if args.unseen and not unseen:
        return False
    return True


def emit(record: dict) -> None:
    print(json.dumps(record), flush=True)


def search_fixture(args: argparse.Namespace) -> int:
    count = 0
    try:
        with open(args.source_file, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError as exc:
                    die(f"bad fixture line: {exc}")
                subject = str(msg.get("subject", ""))
                sender = str(msg.get("from", ""))
                unseen = bool(msg.get("unseen", True))
                if passes_filters(subject, sender, unseen, args):
                    emit({"uid": msg.get("uid"), "subject": subject,
                          "from": sender, "date": msg.get("date", ""),
                          "source": "fixture"})
                    count += 1
                    if count >= args.limit:
                        break
    except OSError as exc:
        die(f"cannot read --source-file: {exc}")
    return 0 if count else 1


def search_imap(args: argparse.Namespace) -> int:
    password = os.environ.get(args.password_env)
    if not password:
        die(f"password env var {args.password_env!r} is not set")

    try:
        if args.ssl:
            conn = imaplib.IMAP4_SSL(args.imap_host, args.imap_port)
        else:
            conn = imaplib.IMAP4(args.imap_host, args.imap_port)
    except OSError as exc:
        die(f"cannot connect to {args.imap_host}:{args.imap_port}: {exc}")

    try:
        conn.login(args.username, password)
        typ, data = conn.select(args.mailbox, readonly=True)
        if typ != "OK":
            die(f"cannot select mailbox {args.mailbox!r}: {data}")

        criteria: list[str] = []
        if args.unseen:
            criteria.append("UNSEEN")
        if args.since_days:
            since = (date.today() - timedelta(days=args.since_days))
            criteria.append(f"SINCE {since.strftime('%d-%b-%Y')}")
        if not criteria:
            criteria = ["ALL"]

        typ, data = conn.search(None, *criteria)
        if typ != "OK":
            die(f"IMAP search failed: {data}")
        uids = data[0].split()

        count = 0
        for uid in reversed(uids):
            typ, msg_data = conn.fetch(
                uid, "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])")
            if typ != "OK" or not msg_data or not isinstance(msg_data[0], tuple):
                continue
            message = email.message_from_bytes(msg_data[0][1])
            subject = decode_header_value(message.get("Subject"))
            sender = decode_header_value(message.get("From"))
            if passes_filters(subject, sender, True, args):
                emit({"uid": uid.decode(), "subject": subject, "from": sender,
                      "date": message.get("Date", ""), "source": "imap"})
                count += 1
                if count >= args.limit:
                    break
        return 0 if count else 1
    except imaplib.IMAP4.error as exc:
        die(f"IMAP error: {exc}")
    finally:
        try:
            conn.logout()
        except (imaplib.IMAP4.error, OSError):
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description="One-shot IMAP search.")
    parser.add_argument("--imap-host", help="IMAP host (or use --source-file)")
    parser.add_argument("--imap-port", type=int, default=993)
    parser.add_argument("--username", help="mailbox login (or use --source-file)")
    parser.add_argument("--password-env", default="EMAIL_PASSWORD",
                        help="environment variable holding the password")
    parser.add_argument("--mailbox", default="INBOX")
    parser.add_argument("--subject-contains",
                        help="case-insensitive subject substring filter")
    parser.add_argument("--from-contains",
                        help="case-insensitive from substring filter")
    parser.add_argument("--unseen", action="store_true",
                        help="only unseen messages")
    parser.add_argument("--since-days", type=int,
                        help="server-side SINCE prefilter in days")
    parser.add_argument("--limit", type=int, default=20,
                        help="maximum matches to emit (default 20)")
    parser.add_argument("--source-file",
                        help="offline JSONL fixture instead of IMAP")
    parser.add_argument("--ssl", action=argparse.BooleanOptionalAction,
                        default=True, help="use IMAP over SSL (default)")
    args = parser.parse_args()

    if args.limit < 1:
        die("--limit must be >= 1")
    if args.source_file:
        return search_fixture(args)
    if not args.imap_host or not args.username:
        die("--imap-host and --username are required (or use --source-file)")
    return search_imap(args)


if __name__ == "__main__":
    sys.exit(main())
