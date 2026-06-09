#!/usr/bin/env python3
"""Jira Work Item Hierarchy Report.

Given a JQL query, fetches all matching work items with their full metadata,
builds a parent-child hierarchy tree, and outputs a markdown report with
clickable links and typed tables.

Usage:
    python3 jira-hierarchy-report.py \\
        --jql 'summary ~ "system memory"' \\
        --output docs/jira-work-items.md
"""

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def run_acli(*args: str) -> dict | list:
    """Run an acli command and return parsed JSON output."""
    cmd = ["acli", "jira", "workitem"] + list(args) + ["--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def search_items(jql: str) -> list[dict]:
    """Search for work items matching the JQL query."""
    raw = run_acli("search", "--jql", jql)
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and "issues" in raw:
        return raw["issues"]
    return [raw]


def fetch_item(key: str) -> dict:
    """Fetch full metadata for a single work item."""
    return run_acli("view", key, "--fields", "*all")


def extract_type_name(fields: dict) -> str:
    """Extract the issue type name from fields."""
    it = fields.get("issuetype", {})
    if isinstance(it, dict):
        return it.get("name", "Unknown")
    return str(it)


def extract_status_name(fields: dict) -> str:
    """Extract the status name from fields."""
    st = fields.get("status", {})
    if isinstance(st, dict):
        return st.get("name", "Unknown")
    return str(st)


def is_testing_subtask(fields: dict) -> bool:
    """Check if a subtask is a testing/QA subtask (not dev responsibility)."""
    summary = fields.get("summary", "")
    name = summary.lower()
    return "test" in name or "qa" in name


def build_report_data(jql: str, base_url: str) -> dict:
    """Search Jira and build all data needed for the report.

    Returns a dict with keys:
      - jql: the original query
      - base_url
      - items: list of all items with full metadata (including subtask expansion)
      - epic: the epic item if one was found
    """
    # Step 1: Search
    results = search_items(jql)
    if not results:
        return {"jql": jql, "base_url": base_url, "items": [], "epic": None}

    # Step 2: Fetch full metadata for each result
    items_by_key: dict[str, dict] = {}
    for item in results:
        key = item["key"]
        try:
            items_by_key[key] = fetch_item(key)
        except subprocess.CalledProcessError:
            items_by_key[key] = item

    # Step 3: Identify epic
    epic = None
    for key, item in items_by_key.items():
        if extract_type_name(item["fields"]).lower() == "epic":
            epic = item

    # Step 4: Collect all subtask data (from parent's subtasks field)
    for key, item in list(items_by_key.items()):
        for st in item["fields"].get("subtasks", []):
            skey = st["key"]
            if skey not in items_by_key and st.get("fields"):
                items_by_key[skey] = {"key": skey, "fields": st["fields"]}

    return {
        "jql": jql,
        "base_url": base_url,
        "items": list(items_by_key.values()),
        "epic": epic,
    }


def format_hierarchy_tree(data: dict) -> str:
    """Build the visual hierarchy tree with clickable links."""
    items_by_key = {it["key"]: it for it in data["items"]}
    base = data["base_url"]
    lines = []
    lines.append("<pre>")

    epic = data.get("epic")

    # Collect all subtask keys so they only appear nested, not at top level
    all_subtask_keys: set[str] = set()
    for item in data["items"]:
        for st in item["fields"].get("subtasks", []):
            all_subtask_keys.add(st["key"])

    if epic:
        ekey = epic["key"]
        efields = epic["fields"]
        lines.append(
            f'<a href="{base}/{ekey}"><b>{ekey}</b></a>'
            f'  Epic \u00b7 {efields.get("summary", "")}'
            f' \u00b7 {extract_status_name(efields)}'
        )
        lines.append("\u2502")
        # Only non-subtask items appear directly under the epic
        top_level = sorted(
            [
                it
                for it in data["items"]
                if it["key"] != ekey and it["key"] not in all_subtask_keys
            ],
            key=lambda x: x["key"],
        )
    else:
        # Without an epic, show only items that are NOT subtasks of other items
        top_level = sorted(
            [
                it
                for it in data["items"]
                if it["key"] not in all_subtask_keys
            ],
            key=lambda x: x["key"],
        )

    def get_subtasks(item: dict) -> list[dict]:
        """Get subtasks of an item that are in our dataset."""
        sts = []
        for st in item["fields"].get("subtasks", []):
            skey = st["key"]
            if skey in items_by_key:
                sts.append(items_by_key[skey])
            elif st.get("fields"):
                sts.append({"key": skey, "fields": st["fields"]})
        return sorted(sts, key=lambda x: x["key"])

    last_idx = len(top_level) - 1
    for i, item in enumerate(top_level):
        ikey = item["key"]
        ifields = item["fields"]
        itype = extract_type_name(ifields)
        prefix = "\u2514\u2500\u2500" if i == last_idx else "\u251c\u2500\u2500"
        lines.append(
            f'{prefix} <a href="{base}/{ikey}"><b>{ikey}</b></a>'
            f'  {itype} \u00b7 {ifields.get("summary", "")}'
            f' \u00b7 {extract_status_name(ifields)}'
        )

        subtasks = get_subtasks(item)
        if subtasks:
            st_indent = "    " if i == last_idx else "\u2502   "
            for j, st in enumerate(subtasks):
                skey = st["key"]
                sfields = st["fields"]
                st_status = extract_status_name(sfields)
                st_summary = sfields.get("summary", "")
                st_prefix_conn = "\u2514\u2500\u2500" if j == len(subtasks) - 1 else "\u251c\u2500\u2500"
                lines.append(
                    f'{st_indent}{st_prefix_conn} <a href="{base}/{skey}"><b>{skey}</b></a>'
                    f'  Subtask \u00b7 {st_summary} \u00b7 {st_status}'
                )

    lines.append("</pre>")
    return "\n".join(lines)


def format_markdown_report(data: dict) -> str:
    """Produce the complete markdown report."""
    lines = []
    lines.append("# Jira Work Item Hierarchy Report")
    lines.append("")
    lines.append(f"**Source JQL:** `{data['jql']}`")
    lines.append(f"**Base URL:** {data['base_url']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Hierarchy")
    lines.append("")
    lines.append(format_hierarchy_tree(data))
    lines.append("")
    lines.append("---")
    lines.append("")

    # Group by type
    base = data["base_url"]
    grouped = defaultdict(list)
    for item in data["items"]:
        t = extract_type_name(item["fields"])
        grouped[t].append(item)

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Type | Count | Keys |")
    lines.append("|------|-------|------|")
    for t in ["Epic", "Story", "Task", "Subtask"]:
        if t in grouped:
            keys = sorted(grouped[t], key=lambda x: x["key"])
            links = ", ".join(
                f"[{it['key']}]({base}/{it['key']})" for it in keys
            )
            lines.append(f"| {t} | {len(keys)} | {links} |")
    lines.append("")

    # Per-type detail tables
    for t in ["Story", "Task"]:
        if t not in grouped:
            continue
        items = sorted(grouped[t], key=lambda x: x["key"])
        lines.append(f"### {t}s ({len(items)})")
        lines.append("")
        lines.append("| Key | Summary | Status |")
        lines.append("|-----|---------|--------|")
        for item in items:
            fields = item["fields"]
            lines.append(
                f"| [{item['key']}]({base}/{item['key']})"
                f" | {fields.get('summary', '')}"
                f" | {extract_status_name(fields)} |"
            )
        lines.append("")

    # Subtask tables - split dev vs testing
    if "Subtask" in grouped:
        subtasks = sorted(grouped["Subtask"], key=lambda x: x["key"])
        dev = [s for s in subtasks if not is_testing_subtask(s["fields"])]
        testing = [s for s in subtasks if is_testing_subtask(s["fields"])]

        if dev:
            lines.append(f"### Dev Subtasks ({len(dev)})")
            lines.append("")
            lines.append("| Key | Summary | Status |")
            lines.append("|-----|---------|--------|")
            for item in dev:
                fields = item["fields"]
                lines.append(
                    f"| [{item['key']}]({base}/{item['key']})"
                    f" | {fields.get('summary', '')}"
                    f" | {extract_status_name(fields)} |"
                )
            lines.append("")

        if testing:
            lines.append("### Testing Subtasks \u2014 not dev responsibility")
            lines.append("")
            lines.append("| Key | Summary | Status |")
            lines.append("|-----|---------|--------|")
            for item in testing:
                fields = item["fields"]
                lines.append(
                    f"| [{item['key']}]({base}/{item['key']})"
                    f" | {fields.get('summary', '')}"
                    f" | {extract_status_name(fields)} |"
                )
            lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Jira work item hierarchy report from a JQL query."
    )
    parser.add_argument(
        "--jql",
        required=True,
        help="JQL query to search for work items (e.g. 'summary ~ \"system memory\"')",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output markdown file path (default: print to stdout)",
    )
    parser.add_argument(
        "--base-url",
        default="https://ompventure.atlassian.net/browse",
        help="Jira base URL for browse links",
    )
    args = parser.parse_args()

    print(f"Searching: {args.jql}", file=sys.stderr)
    try:
        data = build_report_data(args.jql, args.base_url)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)

    if not data["items"]:
        print("No results found.", file=sys.stderr)
        sys.exit(0)

    print(
        f"Found {len(data['items'])} items (including subtasks). Generating report...",
        file=sys.stderr,
    )

    report = format_markdown_report(data)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Report written to {out_path.resolve()}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
