#!/usr/bin/env python3
"""Jira Work Item Hierarchy Report.

Given a JQL query, fetches all matching work items with their full metadata,
builds a parent-child hierarchy tree, and outputs a markdown report with
clickable links and typed tables.

Usage:
    python3 jira-hierarchy-report.py \\
        --jql 'summary ~ "system memory"' \\
        --output docs/jira-work-items.md

    # surface a custom field as an extra column (repeatable)
    python3 jira-hierarchy-report.py \\
        --jql '"Release Status" = "Ready for release"' \\
        --extra-field customfield_10252:Release Status

IMPORTANT — always pass the JQL as ONE argv element (as this script does via
subprocess arg lists). Interpolating it into a shell string mangles the nested
quotes and yields misleading parser errors. See jira-acli-operations SKILL.md
"JQL and --fields Pitfalls".
"""

import argparse
import html
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# acli's own --limit ceiling for a single search call.
SEARCH_LIMIT = 1000

# Issue types are reported in this order; any type not listed is appended
# alphabetically afterwards so NO type is ever silently dropped.
TYPE_ORDER = ["Epic", "Story", "Task", "Bug", "Improvement", "Subtask"]

IRREGULAR_PLURALS = {"Story": "Stories", "Bug": "Bugs", "Epic": "Epics"}

# Middle dot separator between tree fields (hoisted: f-string expressions may
# not contain backslash escapes).
SEP = " \u00b7 "


def run_acli(*args: str) -> dict | list:
    """Run an acli command and return parsed JSON output.

    Passes argv as a list (never a shell string) so JQL quoting survives.
    Tolerates a human-readable preamble line before the JSON payload, which
    some acli builds emit even under --json.
    """
    cmd = ["acli", "jira", "workitem"] + list(args) + ["--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    out = result.stdout.strip()
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        start = min((i for i in (out.find("["), out.find("{")) if i != -1),
                    default=-1)
        if start == -1:
            raise
        return json.loads(out[start:])


def search_items(jql: str, limit: int = SEARCH_LIMIT) -> list[dict]:
    """Search for work items matching the JQL query."""
    raw = run_acli("search", "--jql", jql, "--limit", str(limit))
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict) and "issues" in raw:
        items = raw["issues"]
    else:
        items = [raw]
    if len(items) >= limit:
        print(
            f"WARNING: search returned {len(items)} items, equal to --limit "
            f"{limit}. Results are probably TRUNCATED; narrow the JQL or raise "
            f"--limit.",
            file=sys.stderr,
        )
    return items


def fetch_item(key: str) -> dict:
    """Fetch full metadata for a single work item.

    '*all' is mandatory: `search` never returns custom fields, and --fields
    with a space-containing name is rejected (acli strips the space).
    """
    return run_acli("view", key, "--fields", "*all")


def extract_type_name(fields: dict) -> str:
    """Extract the issue type name from fields."""
    it = fields.get("issuetype") or {}
    if isinstance(it, dict):
        return it.get("name", "Unknown")
    return str(it)


def extract_status_name(fields: dict) -> str:
    """Extract the status name from fields."""
    st = fields.get("status") or {}
    if isinstance(st, dict):
        return st.get("name", "Unknown")
    return str(st)


def extract_parent_key(fields: dict) -> str | None:
    """Extract the parent key, if any."""
    p = fields.get("parent") or {}
    if isinstance(p, dict):
        return p.get("key")
    return None


def extract_custom_value(fields: dict, field_id: str) -> str:
    """Render a custom field value as a short string."""
    v = fields.get(field_id)
    if v is None:
        return ""
    if isinstance(v, dict):
        return str(v.get("value") or v.get("name") or v.get("displayName") or "")
    if isinstance(v, list):
        return ", ".join(
            str(x.get("value") or x.get("name") or x) if isinstance(x, dict) else str(x)
            for x in v
        )
    return str(v)


def is_testing_subtask(fields: dict) -> bool:
    """Check if a subtask is a testing/QA subtask (not dev responsibility)."""
    name = fields.get("summary", "").lower()
    return "test" in name or "qa" in name


def clean(text: str) -> str:
    """Collapse whitespace so a value is safe on one line."""
    return re.sub(r"\s+", " ", str(text or "")).strip()


def cell(text: str) -> str:
    """Escape a value for use inside a markdown table cell.

    An unescaped pipe or an embedded newline silently breaks the whole row.
    """
    return clean(text).replace("|", "\\|")


def pre(text: str) -> str:
    """Escape a value for use inside the <pre> hierarchy block.

    Summaries containing < or > would otherwise be swallowed as HTML tags.
    """
    return html.escape(clean(text), quote=False)


def plural(type_name: str, count: int) -> str:
    """Pluralise an issue type name for a section heading."""
    if count == 1:
        return type_name
    if type_name in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[type_name]
    if type_name.endswith(("s", "x", "z", "ch", "sh")):
        return type_name + "es"
    if type_name.endswith("y") and type_name[-2:-1] not in "aeiou":
        return type_name[:-1] + "ies"
    return type_name + "s"


def sort_key(key: str):
    """Sort issue keys naturally: AES-9 before AES-10."""
    m = re.match(r"^([A-Za-z]+)-(\d+)$", key or "")
    return (m.group(1), int(m.group(2))) if m else (key or "", 0)


def build_report_data(jql: str, base_url: str, limit: int = SEARCH_LIMIT) -> dict:
    """Search Jira and build all data needed for the report.

    Returns a dict with keys:
      - jql, base_url
      - items: list of all items with full metadata (including subtask expansion)
      - epics: every Epic found (not just the last one)
      - children: {parent_key: [child_key, ...]} restricted to in-set items
      - roots: keys with no in-set parent
    """
    results = search_items(jql, limit)
    if not results:
        return {"jql": jql, "base_url": base_url, "items": [],
                "epics": [], "children": {}, "roots": []}

    # Fetch full metadata for each result.
    items_by_key: dict[str, dict] = {}
    for item in results:
        key = item["key"]
        try:
            items_by_key[key] = fetch_item(key)
        except subprocess.CalledProcessError:
            items_by_key[key] = item

    # Pull in subtask stubs that the search itself did not return.
    for item in list(items_by_key.values()):
        for st in item.get("fields", {}).get("subtasks") or []:
            skey = st.get("key")
            if skey and skey not in items_by_key and st.get("fields"):
                items_by_key[skey] = {"key": skey, "fields": st["fields"]}

    # Edges: `parent` is authoritative; `subtasks` supplements it, because a
    # Story under an Epic has a parent but is not in anyone's subtasks array.
    children: dict[str, list[str]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    for key, item in items_by_key.items():
        p = extract_parent_key(item.get("fields", {}))
        if p and p in items_by_key and (p, key) not in seen:
            children[p].append(key)
            seen.add((p, key))
    for key, item in items_by_key.items():
        for st in item.get("fields", {}).get("subtasks") or []:
            skey = st.get("key")
            if skey in items_by_key and (key, skey) not in seen:
                children[key].append(skey)
                seen.add((key, skey))
    for p in children:
        children[p].sort(key=sort_key)

    has_parent = {c for kids in children.values() for c in kids}
    roots = sorted((k for k in items_by_key if k not in has_parent), key=sort_key)

    epics = [it for it in items_by_key.values()
             if extract_type_name(it.get("fields", {})).lower() == "epic"]

    return {
        "jql": jql,
        "base_url": base_url,
        "items": list(items_by_key.values()),
        "epics": epics,
        "children": dict(children),
        "roots": roots,
    }


def format_hierarchy_tree(data: dict, extra: list[tuple[str, str]]) -> str:
    """Build the visual hierarchy tree with clickable links, at any depth."""
    items_by_key = {it["key"]: it for it in data["items"]}
    children = data["children"]
    base = data["base_url"]
    lines = ["<pre>"]

    def render(key: str, prefix: str, last: bool, top: bool) -> None:
        item = items_by_key.get(key)
        if item is None:
            return
        fields = item.get("fields", {})
        conn = "" if top else ("\u2514\u2500\u2500 " if last else "\u251c\u2500\u2500 ")
        mark = "\u25c8 " if (extract_type_name(fields) == "Subtask"
                             and is_testing_subtask(fields)) else ""
        bits = [extract_type_name(fields), pre(fields.get("summary", "")),
                extract_status_name(fields)]
        for fid, label in extra:
            val = extract_custom_value(fields, fid)
            if val:
                bits.append(f"{label}: {pre(val)}")
        lines.append(
            f'{prefix}{conn}<a href="{base}/{key}"><b>{key}</b></a>'
            f'  {mark}{SEP.join(bits)}'
        )
        kids = children.get(key, [])
        for i, child in enumerate(kids):
            nxt = prefix if top else prefix + ("    " if last else "\u2502   ")
            render(child, nxt, i == len(kids) - 1, False)

    roots = data["roots"]
    for i, root in enumerate(roots):
        render(root, "", i == len(roots) - 1, False)

    lines.append("</pre>")
    return "\n".join(lines)


def ordered_types(grouped: dict) -> list[str]:
    """Canonical types first, then any remaining types alphabetically."""
    known = [t for t in TYPE_ORDER if t in grouped]
    rest = sorted(t for t in grouped if t not in TYPE_ORDER)
    return known + rest


def detail_rows(items: list[dict], base: str, extra: list[tuple[str, str]],
                with_parent: bool) -> list[str]:
    """Render a detail table for a set of items."""
    head = ["Key", "Summary"]
    if with_parent:
        head.append("Parent")
    head.append("Status")
    head += [label for _, label in extra]
    lines = ["| " + " | ".join(head) + " |",
             "|" + "---|" * len(head)]
    for item in items:
        fields = item["fields"]
        row = [f"[{item['key']}]({base}/{item['key']})",
               cell(fields.get("summary", ""))]
        if with_parent:
            p = extract_parent_key(fields)
            row.append(f"[{p}]({base}/{p})" if p else "\u2014")
        row.append(extract_status_name(fields))
        row += [cell(extract_custom_value(fields, fid)) for fid, _ in extra]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return lines


def format_markdown_report(data: dict, extra: list[tuple[str, str]]) -> str:
    """Produce the complete markdown report."""
    base = data["base_url"]
    lines = ["# Jira Work Item Hierarchy Report", "",
             f"**Source JQL:** `{data['jql']}`",
             f"**Base URL:** {base}",
             f"**Total items:** {len(data['items'])}", "",
             "---", "", "## Hierarchy", "",
             format_hierarchy_tree(data, extra), "",
             "> \u25c8 = Testing subtask (not dev responsibility)", "",
             "---", ""]

    grouped = defaultdict(list)
    for item in data["items"]:
        grouped[extract_type_name(item["fields"])].append(item)
    for t in grouped:
        grouped[t].sort(key=lambda x: sort_key(x["key"]))

    # Summary table - covers EVERY type present, so nothing is dropped.
    lines += ["## Summary", "", "| Type | Count | Keys |", "|------|-------|------|"]
    total = 0
    for t in ordered_types(grouped):
        items = grouped[t]
        total += len(items)
        links = ", ".join(f"[{it['key']}]({base}/{it['key']})" for it in items)
        lines.append(f"| {t} | {len(items)} | {links} |")
    lines += [f"| **Total** | **{total}** | |", ""]

    # Per-type detail tables for every non-subtask type.
    for t in ordered_types(grouped):
        if t == "Subtask":
            continue
        items = grouped[t]
        lines += [f"### {plural(t, len(items))} ({len(items)})", ""]
        lines += detail_rows(items, base, extra, with_parent=False)

    # Subtask tables - split dev vs testing.
    if "Subtask" in grouped:
        subtasks = grouped["Subtask"]
        dev = [s for s in subtasks if not is_testing_subtask(s["fields"])]
        testing = [s for s in subtasks if is_testing_subtask(s["fields"])]

        if dev:
            lines += [f"### Dev Subtasks ({len(dev)})", ""]
            lines += detail_rows(dev, base, extra, with_parent=True)

        if testing:
            lines += [
                f"### Testing Subtasks ({len(testing)}) \u2014 not dev responsibility",
                "",
            ]
            lines += detail_rows(testing, base, extra, with_parent=True)

    return "\n".join(lines)


def parse_extra(values: list[str]) -> list[tuple[str, str]]:
    """Parse --extra-field ID arguments.

    The label is auto-derived from the field ID (e.g. customfield_10252 ->
    "10252") so the value is always a single argv token -- no quoting needed
    even when you would want a spaced label.
    """
    out = []
    for raw in values or []:
        fid = raw.strip()
        if not fid:
            continue
        num = ""
        if fid.startswith("customfield_"):
            num = fid[len("customfield_"):]
        out.append((fid, num or fid))
    return out


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
    parser.add_argument(
        "--limit",
        type=int,
        default=SEARCH_LIMIT,
        help=f"Max items to fetch (default {SEARCH_LIMIT}); warns on truncation",
    )
    parser.add_argument(
        "--extra-field",
        action="append",
        metavar="ID",
        help="Custom field to surface as a column, e.g. customfield_10252 "
             "(label is auto-derived; single token, no quoting needed)",
    )
    args = parser.parse_args()
    extra = parse_extra(args.extra_field)

    print(f"Searching: {args.jql}", file=sys.stderr)
    try:
        data = build_report_data(args.jql, args.base_url, args.limit)
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

    report = format_markdown_report(data, extra)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Report written to {out_path.resolve()}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
