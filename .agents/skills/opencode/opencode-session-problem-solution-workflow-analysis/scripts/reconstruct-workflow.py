#!/usr/bin/env python3
"""Reconstruct an opencode session's problem / solution / executed-workflow report.

Consumes the base `opencode-session-yaml-transcript-extractor` CLI (subprocess,
path anchored on this script's own location) and formats its transcript JSONL
into a deterministic markdown report skeleton: session meta, Workflow Executed
chronology (per-turn user text / thinking / tool calls), and clearly marked
placeholder blocks for the agent-judgement sections (Problem, Solution,
Rejected Paths, Final State).

Tier: Tier 1 (Python) per scripting-language-selection-rules.md §2 (Tier 1
default) and §4 (JSON/JSONL data manipulation + report generation) -- stdlib
only, no CPU bottleneck, no ecosystem mandate.
"""

from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import subprocess
import sys

BASE_REL = pathlib.Path(
    "opencode-session-yaml-transcript-extractor"
) / "scripts" / "extract-yaml-transcript.py"


def _find_base() -> pathlib.Path:
    base = pathlib.Path(__file__).resolve().parents[2] / BASE_REL
    return base


def _flatten(value: str, limit: int) -> str:
    value = " ".join(value.split())
    if len(value) > limit:
        return value[:limit] + f"... <truncated {len(value) - limit} chars>"
    return value


def _blockquote(text: str) -> str:
    return "\n".join(f"> {line}" for line in text.splitlines())


def build_report(records: list[dict], input_path: str, truncate: int) -> str:
    session_id = ""
    title = ""
    for rec in records:
        if rec.get("kind") == "session_header":
            session_id = rec.get("id") or rec.get("session_id") or ""
            title = rec.get("title") or ""
            break

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = []
    lines.append("# OpenCode Session Analysis — Problem / Solution / Workflow")
    lines.append("")
    lines.append(f"> **Session log:** `{input_path}`")
    lines.append(f"> **Generated:** `{now}`")
    if session_id:
        lines.append(f"> **Session ID:** `{session_id}`")
    if title:
        lines.append(f"> **Session title:** `{title}`")
    lines.append("")

    lines.append("## 1. Problem")
    lines.append("")
    lines.append("> **TBD — agent judgement.** Identify the problem from the user's")
    lines.append("> textual messages: the FIRST message states the original ask;")
    lines.append("> correction turns (e.g. \"no, this is wrong\") mark what the previous")
    lines.append("> answer got wrong. Quote the exact user text that defines the")
    lines.append("> problem.")
    lines.append("")

    lines.append("## 2. Solution")
    lines.append("")
    lines.append("> **TBD — agent judgement.** Identify the solution from the state the")
    lines.append("> user ultimately accepts. Cite the concrete evidence path that")
    lines.append("> produced it (DB key, file path, CLI command, output record).")
    lines.append("")

    lines.append("## 3. Workflow Executed")
    lines.append("")
    lines.append("Deterministic chronology extracted from the transcript — one")
    lines.append("section per turn. Per-turn tool-call counts are listed in the")
    lines.append("summary table below.")
    lines.append("")

    turns: dict[int, list[dict]] = {}
    for rec in records:
        if rec.get("kind") == "session_header":
            continue
        turns.setdefault(rec.get("turn", -1), []).append(rec)

    for turn in sorted(turns):
        items = turns[turn]
        lines.append(f"### Turn {turn}")
        lines.append("")
        for rec in items:
            kind = rec["kind"]
            if kind == "user_text":
                lines.append("**User:**")
                lines.append("")
                lines.append(_blockquote(rec.get("text") or ""))
                lines.append("")
            elif kind == "thinking":
                lines.append("**Thinking:**")
                lines.append("")
                lines.append(_blockquote(rec.get("text") or ""))
                lines.append("")
            elif kind == "tool_call":
                tool = rec.get("tool")
                args = _flatten(rec.get("args", ""), truncate) if isinstance(rec.get("args"), str) else _flatten(json.dumps(rec.get("args", {}), ensure_ascii=False), truncate)
                result = _flatten(rec.get("result") or "", truncate)
                lines.append(f"- **[{rec['index']}] {tool}**")
                lines.append(f"  - args: `{args}`")
                lines.append(f"  - result: `{result}`")
        lines.append("")

    total_calls = sum(1 for r in records if r.get("kind") == "tool_call")
    per_turn = {
        t: sum(1 for r in items if r.get("kind") == "tool_call")
        for t, items in turns.items()
    }
    lines.append("### Summary")
    lines.append("")
    lines.append(f"- Total tool calls: {total_calls}")
    lines.append("- Per turn:")
    lines.append("")
    lines.append("| Turn | Tool calls |")
    lines.append("| :--- | :--- |")
    for t in sorted(per_turn):
        lines.append(f"| {t} | {per_turn[t]} |")
    lines.append("")

    lines.append("## 4. Rejected / Alternative Paths")
    lines.append("")
    lines.append("> **TBD — agent judgement.** Tool sequences or answer candidates that")
    lines.append("> the thinking text or the user's corrections abandon. Each rejected")
    lines.append("> path is typically a prefix of the tool-call chronology in §3 that")
    lines.append("> ends in a correction turn.")
    lines.append("")

    lines.append("## 5. Final State")
    lines.append("")
    lines.append("> **TBD — agent judgement.** What was delivered in the last turn and")
    lines.append("> whether the user accepted it.")
    lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reconstruct problem/solution/workflow report skeleton from an opencode session log."
    )
    parser.add_argument("--input", required=True, help="Monolithic .yaml file OR per-turn session directory")
    parser.add_argument("--truncate", type=int, default=500, help="Truncate text/args/result to N chars")
    parser.add_argument("--output", help="Write report markdown to file instead of stdout")
    args = parser.parse_args(argv)

    base = _find_base()
    if not base.is_file():
        sys.stderr.write(
            f"error: base script not found at {base} — is the "
            f"opencode-session-yaml-transcript-extractor skill installed?\n"
        )
        return 4

    if not pathlib.Path(args.input).exists():
        sys.stderr.write(f"error: input path not found: {args.input}\n")
        return 3

    proc = subprocess.run(
        [sys.executable, str(base), "--input", args.input, "--truncate", str(args.truncate)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        return 2

    records = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
    report = build_report(records, args.input, args.truncate)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(report + "\n")
        sys.stderr.write(f"Report written to: {args.output}\n")
    else:
        sys.stdout.write(report + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
