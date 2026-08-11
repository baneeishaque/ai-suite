#!/usr/bin/env python3
"""Extract the per-turn transcript of an opencode logger-plugin YAML session log.

Emits one JSONL record per narrative element (session header, user text,
assistant thinking, assistant tool call) in chronological order, with global
index and per-turn identity. Superset of the tool-call-only extractor: the
user_text and thinking records are what make problem / rejected-path
identification possible in downstream analysis composers.

Tier: Tier 1 (Python) per scripting-language-selection-rules.md §2 (Tier 1
default) and §4 (JSON/YAML data manipulation) -- generic data-munging, no CPU
bottleneck, no ecosystem mandate.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        "error: PyYAML is required -- install with 'python3 -m pip install pyyaml'\n"
    )
    sys.exit(2)

KINDS = ("session_header", "user_text", "thinking", "tool_call")


def _truncate(value: str, limit: int) -> str:
    if limit is not None and len(value) > limit:
        return value[:limit] + f"... <truncated {len(value) - limit} chars>"
    return value


def _load_docs(path: pathlib.Path) -> list[dict | None]:
    docs: list[dict | None] = []
    with open(path, encoding="utf-8") as handle:
        for doc in yaml.safe_load_all(handle):
            docs.append(doc)
    return docs


def _iter_documents(input_path: str) -> list[tuple[pathlib.Path, int, dict]]:
    """Yield (source_file, doc_index, doc) for every doc, in chronological order.

    Layouts:
    - Monolithic: one .yaml file, multi-document; doc 1 = session header.
    - Per-turn dir: 000-header-*.yaml (session header) + NNN-<ts>.yaml turn files;
      filename order = chronological order.
    """
    path = pathlib.Path(input_path)
    if path.is_dir():
        files = sorted(p for p in path.iterdir() if p.suffix == ".yaml")
        if not files:
            raise FileNotFoundError(f"no .yaml files under directory: {input_path}")
    elif path.is_file():
        files = [path]
    else:
        raise FileNotFoundError(f"input path not found: {input_path}")

    result: list[tuple[pathlib.Path, int, dict]] = []
    for file in files:
        try:
            docs = _load_docs(file)
        except yaml.YAMLError as exc:
            sys.stderr.write(f"warning: skipping malformed YAML {file}: {exc}\n")
            continue
        for index, doc in enumerate(docs):
            if isinstance(doc, dict):
                result.append((file, index, doc))
    return result


def extract(input_path: str, kinds: list[str], tools: list[str], truncate: int | None) -> list[dict]:
    documents = _iter_documents(input_path)
    records: list[dict] = []
    global_index = 0
    turn = -1  # user docs open a turn; assistant docs join the current turn

    for file, doc_index, doc in documents:
        if "session" in doc:
            header = doc["session"] or {}
            if not isinstance(header, dict):
                header = {}
            record = {
                "index": global_index,
                "turn": -1,
                "kind": "session_header",
            }
            for key in ("id", "session_id", "title"):
                if key in header and isinstance(header[key], str):
                    record[key] = header[key]
            global_index += 1
            if not kinds or "session_header" in kinds:
                records.append(record)
            continue

        if "user" in doc:
            turn += 1
            user = doc["user"]
            text = ""
            time = None
            if isinstance(user, dict):
                text = user.get("text") or ""
                time = user.get("time")
            elif isinstance(user, str):
                text = user
            if not kinds or "user_text" in kinds:
                record = {
                    "index": global_index,
                    "turn": turn,
                    "kind": "user_text",
                    "role": "user",
                    "text": _truncate(text, truncate) if truncate else text,
                }
                if time is not None:
                    record["time"] = time
                records.append(record)
            global_index += 1

        if "assistant" in doc:
            assistant = doc["assistant"]
            items = assistant if isinstance(assistant, list) else [assistant]
            for item in items:
                if not isinstance(item, dict):
                    continue
                thinking = item.get("thinking")
                if thinking and (not kinds or "thinking" in kinds):
                    records.append(
                        {
                            "index": global_index,
                            "turn": turn,
                            "kind": "thinking",
                            "role": "assistant",
                            "text": _truncate(thinking, truncate) if truncate else thinking,
                        }
                    )
                    global_index += 1
                tool_calls = item.get("tool_calls") or []
                if isinstance(tool_calls, dict):
                    tool_calls = [tool_calls]
                for call in tool_calls:
                    if not isinstance(call, dict) or "tool" not in call:
                        continue
                    if tools and call.get("tool") not in tools:
                        continue
                    if kinds and "tool_call" not in kinds:
                        continue
                    record = {
                        "index": global_index,
                        "turn": turn,
                        "kind": "tool_call",
                        "role": "assistant",
                        "tool": call.get("tool"),
                    }
                    args = call.get("args") or {}
                    if truncate is not None:
                        args_json = json.dumps(args, ensure_ascii=False)
                        record["args"] = _truncate(args_json, truncate)
                    else:
                        record["args"] = args
                    result = call.get("result") or ""
                    if truncate is not None:
                        record["result"] = _truncate(result, truncate)
                    else:
                        record["result"] = result
                    records.append(record)
                    global_index += 1

    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract per-turn transcript JSONL from opencode logger YAML session logs."
    )
    parser.add_argument("--input", required=True, help="Monolithic .yaml file OR per-turn session directory")
    parser.add_argument("--kind", action="append", choices=KINDS, help="Record kind filter (repeatable)")
    parser.add_argument("--tool", action="append", help="Tool name filter for tool_call records (repeatable)")
    parser.add_argument("--truncate", type=int, default=None, help="Truncate text/args/result to N chars")
    parser.add_argument("--output", help="Write JSONL to file instead of stdout")
    args = parser.parse_args(argv)

    try:
        records = extract(args.input, args.kind or [], args.tool or [], args.truncate)
    except FileNotFoundError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 3

    if not records:
        sys.stderr.write("No records found matching criteria\n")
        return 1

    lines = [json.dumps(r, ensure_ascii=False) for r in records]
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        sys.stderr.write(f"Found {len(records)} record(s), JSONL written to: {args.output}\n")
    else:
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stderr.write(f"Found {len(records)} record(s)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
