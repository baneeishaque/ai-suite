#!/usr/bin/env python3
"""poll-until.py — bounded polling engine: repeat a check command until success.

Tier 1 (Python 3.12+) per scripting-language-selection-rules.md §2 (Tier 1
default): subprocess-orchestrated, pure-stdlib; no pip dependencies.

Runs a caller-supplied check command every --interval seconds, up to
--attempts times, until the command exits with the success code (default 0).
Emits one JSON object per attempt plus a final verdict object to stdout;
diagnostics go to stderr.

Usage:
    python3 poll-until.py [options] -- <check-cmd> [args...]

Exit codes:
    0  condition met
    1  exhausted (attempts ran out without success)
    2  usage / configuration error
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time

MAX_TAIL = 400


def die(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def tail(text: str) -> str:
    text = (text or "").strip()
    return text if len(text) <= MAX_TAIL else text[-MAX_TAIL:]


def main() -> int:
    argv = sys.argv[1:]
    if "--" in argv:
        sep = argv.index("--")
        head, check_cmd = argv[:sep], argv[sep + 1:]
    else:
        head, check_cmd = argv, []

    p = argparse.ArgumentParser(description="Bounded polling engine.")
    p.add_argument("--interval", type=float, default=10.0,
                   help="seconds between attempts (default 10)")
    p.add_argument("--attempts", type=int, default=12,
                   help="maximum attempts (default 12)")
    p.add_argument("--success-exit", type=int, default=0,
                   help="exit code that counts as met (default 0)")
    p.add_argument("--attempt-timeout", type=float, default=120.0,
                   help="seconds allowed per check attempt (default 120)")
    p.add_argument("--label", default="", help="label echoed into every record")
    args = p.parse_args(head)

    if not check_cmd:
        die("missing '-- <check-cmd>' (use --help for usage)")
    if args.attempts < 1:
        die("--attempts must be >= 1")
    if args.interval < 0:
        die("--interval must be >= 0")

    started = time.monotonic()
    for attempt in range(1, args.attempts + 1):
        attempt_start = time.monotonic()
        try:
            proc = subprocess.run(
                check_cmd, capture_output=True, text=True, encoding="utf-8",
                timeout=args.attempt_timeout,
            )
            exit_code, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as exc:
            exit_code = -1
            out = exc.stdout if isinstance(exc.stdout, str) else ""
            err = f"attempt timed out after {args.attempt_timeout}s"
        except OSError as exc:
            die(f"cannot run check command {check_cmd!r}: {exc}")

        met = exit_code == args.success_exit
        record = {
            "attempt": attempt,
            "label": args.label,
            "exit_code": exit_code,
            "elapsed_s": round(time.monotonic() - attempt_start, 3),
            "met": met,
            "stdout_tail": tail(out),
            "stderr_tail": tail(err),
        }
        print(json.dumps(record), flush=True)
        if met:
            print(json.dumps({
                "verdict": "met",
                "attempts_used": attempt,
                "total_elapsed_s": round(time.monotonic() - started, 3),
                "label": args.label,
            }), flush=True)
            return 0
        if attempt < args.attempts:
            time.sleep(args.interval)

    print(json.dumps({
        "verdict": "exhausted",
        "attempts_used": args.attempts,
        "total_elapsed_s": round(time.monotonic() - started, 3),
        "label": args.label,
    }), flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
