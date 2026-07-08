#!/usr/bin/env python3
"""
Export Claude/MCP session JSONL files into structured markdown.

See ../SKILL.md for the full CLI contract.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

DEFAULT_TYPES = ["tool_use", "tool_result", "text", "thinking"]

SESSION_ID_RE = re.compile(r"([a-f0-9-]{36})\.jsonl$")

EXTRACTION_PATHS = [
    {"label": "user_text", "keys": ["type:user", "message", "content"]},
    {"label": "typed_blocks", "keys": ["message", "content", "type:%s"]},
    {"label": "attachments", "keys": ["attachment", "type:skill_listing"]},
    {"label": "hookInfos", "keys": ["hookInfos"]},
    {"label": "toolUseResult", "keys": ["toolUseResult"]},
]


def get_session_id(filepath: str) -> str:
    basename = os.path.basename(filepath)
    m = SESSION_ID_RE.search(basename)
    if m:
        return m.group(1)
    return os.path.splitext(basename)[0]


def is_empty_text(entry: dict) -> bool:
    if entry.get("value") == "text":
        block = entry.get("block", {})
        text = block.get("text", "") if isinstance(block, dict) else ""
        return not text.strip()
    return False


def render_block_markdown(entry: dict) -> str:
    line = entry["line"]
    line_data = entry.get("line_data", {})
    role = line_data.get("type", "unknown")
    source = entry.get("_source", "content")
    content_type = entry.get("value", "unknown")
    block = entry.get("block", {})

    if source == "unmatched":
        label = f"Line {line} (type: {role})"
        lines = [f"## {label}", "", ""]
        return "\n".join(lines)

    if source == "user_text":
        text = content_type if isinstance(content_type, str) else json.dumps(content_type, indent=2, ensure_ascii=False)
        lines = [f"## Line {line} (user — text)", "", text, ""]
        return "\n".join(lines)

    if source == "attachments":
        label = f"Line {line} (skill_listing)"
        lines = [f"## {label}"]
        lines.append("```json")
        lines.append(json.dumps(block, indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")
        return "\n".join(lines)

    if source == "hookInfos":
        label = f"Line {line} (hookInfos)"
        lines = [f"## {label}"]
        payload = content_type if content_type != "unknown" else block
        lines.append("```json")
        lines.append(json.dumps(payload, indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")
        return "\n".join(lines)

    if source == "toolUseResult":
        label = f"Line {line} (toolUseResult)"
        lines = [f"## {label}"]
        payload = content_type if content_type != "unknown" else block
        lines.append("```json")
        lines.append(json.dumps(payload, indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")
        return "\n".join(lines)

    label = f"Line {line} ({role} — {content_type})"
    lines = [f"## {label}"]

    if content_type == "text":
        text = block.get("text", "") if isinstance(block, dict) else ""
        lines.append("")
        lines.append(text)
    elif content_type == "thinking":
        text = block.get("thinking", "") if isinstance(block, dict) else ""
        lines.append("")
        lines.append(text.lstrip("\n"))
    else:
        lines.append("```json")
        lines.append(json.dumps(block, indent=2, ensure_ascii=False))
        lines.append("```")

    lines.append("")
    return "\n".join(lines)


def render_markdown(results: list[dict], title: str) -> str:
    if not results:
        return f"# {title}\n\n*No items.*\n"

    results_sorted = sorted(results, key=lambda r: (r["line"], r.get("content_index", 0)))
    parts = [f"# {title}\n"]
    for entry in results_sorted:
        parts.append(render_block_markdown(entry))
    return "\n".join(parts)


def _run_extraction(base_script: str, filepath: str, keys: list[str],
                    matched_path: str, unmatched_path: str) -> bool:
    cmd = [sys.executable, base_script, "--file", filepath]
    for k in keys:
        cmd.extend(["--key", k])
    cmd.extend(["--output-matched", matched_path])
    cmd.extend(["--output-unmatched", unmatched_path])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: base extractor failed for keys {keys}:\n{result.stderr}", file=sys.stderr)
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export Claude session JSONL to structured markdown"
    )
    parser.add_argument("--file", required=True, help="Path to Claude session JSONL file")
    parser.add_argument("--type", action="append", default=None,
                        help=f"Content types to extract (default: {', '.join(DEFAULT_TYPES)})")
    parser.add_argument("--output-dir", default=".", help="Output directory (default: current dir)")

    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1

    types = args.type if args.type else DEFAULT_TYPES
    session_id = get_session_id(args.file)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_script = os.path.normpath(os.path.join(script_dir,
                                  "../../jsonl-content-extractor/scripts/extract.py"))

    if not os.path.isfile(base_script):
        print(f"Error: base extractor not found at {base_script}", file=sys.stderr)
        return 1

    all_matched: list[dict] = []
    all_unmatched: list[dict] = []
    matched_lines: set[int] = set()
    type_values = ",".join(types)

    for path in EXTRACTION_PATHS:
        keys = [k % type_values if "%s" in k else k for k in path["keys"]]

        with (tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as mf,
              tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as uf):
            matched_path = mf.name
            unmatched_path = uf.name

        try:
            if not _run_extraction(base_script, args.file, keys, matched_path, unmatched_path):
                return 1

            with open(matched_path, "r", encoding="utf-8") as f:
                matched = json.load(f)
            with open(unmatched_path, "r", encoding="utf-8") as f:
                unmatched = json.load(f)

            for item in matched:
                item["_source"] = path["label"]
                matched_lines.add(item["line"])
            for item in unmatched:
                item["_source"] = path["label"]

            all_matched.extend(matched)
            all_unmatched.extend(unmatched)

        finally:
            for p in [matched_path, unmatched_path]:
                if os.path.exists(p):
                    os.unlink(p)

    all_matched = [e for e in all_matched if not is_empty_text(e)
                   and not (e.get("_source") == "user_text" and not isinstance(e.get("value"), str))]
    surviving_lines = {e["line"] for e in all_matched}
    all_unmatched = [e for e in all_unmatched if e["line"] not in surviving_lines]
    with open(args.file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if i not in surviving_lines:
                data = json.loads(line)
                all_unmatched.append({
                    "line": i,
                    "content_index": 0,
                    "matched": False,
                    "value": data.get("type", "unknown"),
                    "block": {},
                    "_source": "unmatched",
                    "line_data": data,
                })

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    extracted_path = os.path.join(output_dir, f"{session_id}-extracted.md")
    other_path = os.path.join(output_dir, f"{session_id}-other.md")

    type_label = ", ".join(types)
    extracted_md = render_markdown(all_matched, f"Claude Session Export — {type_label}")
    other_md = render_markdown(all_unmatched, f"Other Content — not matching: {type_label}")

    with open(extracted_path, "w", encoding="utf-8") as f:
        f.write(extracted_md)
    with open(other_path, "w", encoding="utf-8") as f:
        f.write(other_md)

    print(f"Extracted: {len(all_matched)} items → {extracted_path}", file=sys.stderr)
    print(f"Other:    {len(all_unmatched)} items → {other_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
