#!/usr/bin/env python3
"""
OpenCode Session YAML Conversation Extractor

Extract a conversation-only transcript from opencode logger-plugin YAML
session logs. For each turn, keep ONLY:
  - user.text            (drop user.time)
  - assistant[].response (drop model, thinking, tool_calls, time, duration*)
  - assistant[].agent     ONLY when value == "compaction" (drop when "build");
                           ordered BEFORE response when present

Header documents (session:) pass through unchanged (session + model + title).

Output preserves YAML structure via ruamel.yaml round-trip (comments, scalar
styles, key ordering, --- separators). One <stem>-transcript.yaml per input
file, written to a transcripts/ subfolder.

Tier: Tier 1 (Python) per scripting-language-selection-rules.md intro (Tier 1
default) +  4 (YAML/JSON data manipulation) -- generic YAML filtering, no CPU
bottleneck, no ecosystem mandate.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


def _normalize_list(value):
    """Normalize a single-dict-or-list value to a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _filter_turn(doc: dict) -> CommentedMap:
    """Build a conversation-only copy of a turn document (round-trip safe)."""
    out = CommentedMap()

    if "user" in doc:
        user = doc["user"]
        nu = CommentedMap()
        if isinstance(user, dict) and "text" in user:
            nu["text"] = user["text"]
        out["user"] = nu

    if "assistant" in doc:
        src_items = _normalize_list(doc["assistant"])
        na = []
        for it in src_items:
            if not isinstance(it, dict):
                continue
            if "response" not in it:
                continue
            ne = CommentedMap()
            if it.get("agent") == "compaction":
                ne["agent"] = "compaction"
            ne["response"] = it["response"]
            na.append(ne)
        if na:
            out["assistant"] = na

    return out


def _iter_input_files(input_path: Path):
    """Yield input YAML files in chronological order (per-turn dir or single file)."""
    if input_path.is_dir():
        files = sorted(p for p in input_path.iterdir() if p.suffix == ".yaml")
        if not files:
            sys.stderr.write(
                f"warning: no *.yaml files under directory: {input_path}\n"
            )
        return files
    if input_path.is_file():
        return [input_path]
    sys.stderr.write(f"error: Input path not found: {input_path}\n")
    sys.exit(3)


def _default_output_dir(input_path: Path) -> Path:
    return (
        input_path.parent / "transcripts"
        if input_path.is_file()
        else input_path / "transcripts"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Extract conversation-only YAML transcripts from opencode "
        "logger-plugin session logs (per-turn dir or monolithic file)."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Monolithic ``ses_<id>_.yaml`` file OR per-turn "
        "``ses_<id>_/`` directory of ``NNN-*.yaml`` files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory. Default: ``<input>/transcripts`` (dir input) or "
        "``<input-dir>/transcripts`` (file input)",
    )
    args = parser.parse_args()

    input_path = args.input
    if not input_path.exists():
        sys.stderr.write(f"error: Input path not found: {input_path}\n")
        sys.exit(3)

    output_dir = args.output_dir or _default_output_dir(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    yaml_rt = YAML(typ="rt")
    yaml_rt.preserve_quotes = True
    yaml_rt.width = 4096
    yaml_rt.indent(mapping=2, sequence=4, offset=2)

    in_files = _iter_input_files(input_path)
    if not in_files:
        sys.stderr.write(f"warning: no input YAML files found for: {input_path}\n")
        sys.exit(1)

    processed = 0
    for in_file in in_files:
        try:
            with open(in_file, encoding="utf-8") as handle:
                docs = list(yaml_rt.load_all(handle))
        except Exception as exc:
            sys.stderr.write(f"warning: skipping {in_file}: {exc}\n")
            continue

        out_docs = []
        for doc in docs:
            if doc is None:
                continue
            if "session" in doc:
                out_docs.append(doc)
            elif "user" in doc or "assistant" in doc:
                out_docs.append(_filter_turn(doc))

        if not out_docs:
            continue

        stem = in_file.stem
        out_path = output_dir / f"{stem}-transcript.yaml"
        with open(out_path, "w", encoding="utf-8") as handle:
            yaml_rt.dump_all(out_docs, handle)
        processed += 1
        sys.stderr.write(f"Written: {out_path}\n")

    if processed == 0:
        sys.stderr.write("error: no turn documents found to process\n")
        sys.exit(1)

    sys.stderr.write(
        f"Found {processed} file(s), transcripts written to: {output_dir}\n"
    )


if __name__ == "__main__":
    main()
