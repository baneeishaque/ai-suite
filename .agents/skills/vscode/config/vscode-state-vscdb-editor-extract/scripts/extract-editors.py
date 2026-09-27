#!/usr/bin/env python3
"""Extract open VS Code editor tabs + pinned annotation from a state.vscdb.

Reads the 'memento/workbench.parts.editor' key from a VS Code Code-family
state.vscdb SQLite database (VS Code / Code - Insiders / VSCodium / Cursor),
parses the 'editorpart.state.serializedGrid' tree, walks it to every leaf
editor-group, and emits the editors in display (tab-bar) order with pinned
annotation derived from the group-level 'sticky' count.

Default text output ('--mode all') lists EVERY tab — file, webview
(markdown previews, custom editors) and terminal — in tab-bar order with a
'[type]' tag, '#' group markers, and a '[pinned]' suffix. '--mode files'
emits the file-only projection (one absolute fsPath per line) for callers
that want just source files.

Key findings from session 02f0d4351ffeTl1vcyqbPXZqvW:
  - The 'editors[]' array on each leaf node is in display order (pinned first).
  - 'sticky: N' at the group level = number of pinned (sticky) editors.
    Editors at index < N are pinned. The per-editor 'pinned' flag is NOT
    serialized — 'sticky' count is the only signal.
  - 'mru: [...]' is a separate ordering axis (most-recently-used), NOT the
    tab-bar order.
  - 'memento/workbench.editors.files.textFileEditor' (view-state memento) is
    NOT a reliable source — it includes historically-closed editors.

Key findings from session 00dd58393ffertAuAtxH2qg1EU:
  - Webview tabs (workbench.editors.webviewEditor) carry their backing source
    file inside value['state'] — a JSON-encoded string whose parsed object has
    a 'resource' key (URI dict with 'path'/'fsPath', or a 'file://' string).
    Top-level 'resourceJSON'/'resource' are absent for webview entries.
  - The file-only projection silently dropped webview + terminal tabs, so it
    never matched the on-screen tab bar; '--mode all' is the faithful view.

Tier 1 (Python 3.12+, stdlib only) per scripting-language-selection-rules §2.1.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from typing import Any


FILE_EDITOR_INPUT_ID = "workbench.editors.files.fileEditorInput"
TERMINAL_EDITOR_ID = "workbench.editors.terminal"
WEBVIEW_EDITOR_ID = "workbench.editors.webviewEditor"
DEFAULT_KEY = "memento/workbench.parts.editor"


def read_memento_value(db_path: str, key: str) -> str | None:
    """Read a single key from the VS Code state.vscdb ItemTable.

    Returns the raw string value, or None if the key does not exist.
    Exits with code 2 on SQLite error.
    """
    if not os.path.isfile(db_path):
        sys.stderr.write(f"ERROR: database not found: {db_path}\n")
        sys.exit(2)
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        sys.stderr.write(f"ERROR: cannot open database {db_path}: {exc}\n")
        sys.exit(2)
    try:
        row = conn.execute(
            "SELECT value FROM ItemTable WHERE key = ?", (key,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    return row[0]


def walk_grid(node: Any, leaves: list[dict]) -> None:
    """Recursively walk the serializedGrid tree.

    VS Code's serializedGrid is a nested tree of branch/leaf nodes:
      - {'type': 'branch', 'data': [<child-node>, ...]}
      - {'type': 'leaf',   'data': {'id': <int>, 'editors': [...],
                                   'sticky': <int>, 'mru': [...], 'size': <int>}}

    Appends every leaf-group dict to *leaves*.
    """
    if not isinstance(node, dict):
        return
    data = node.get("data")
    if node.get("type") == "leaf" and isinstance(data, dict):
        leaves.append(data)
    elif isinstance(data, list):
        for child in data:
            walk_grid(child, leaves)
    elif isinstance(data, dict):
        for val in data.values():
            if isinstance(val, dict):
                walk_grid(val, leaves)


def extract_fs_path(value_json: str) -> str | None:
    """Parse a fileEditorInput 'value' string and return the absolute fsPath.

    The value JSON may use 'resourceJSON' (newer VS Code) or 'resource'
    (older forms). Both contain a 'path' field.
    """
    try:
        obj = json.loads(value_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(obj, dict):
        return None
    # Newer Code versions use resourceJSON
    res = obj.get("resourceJSON")
    if isinstance(res, dict) and res.get("path"):
        return res["path"]
    # Older / alternate forms use 'resource'
    res = obj.get("resource")
    if isinstance(res, dict) and res.get("path"):
        return res["path"]
    # Some forms store the path directly under 'path'
    if isinstance(obj.get("path"), str):
        return obj["path"]
    return None


def extract_webview_source_path(value_json: str) -> str | None:
    """Return the backing source file path of a webviewEditor 'value'.

    Webview entries (markdown previews, custom editors) have no top-level
    'resourceJSON'/'resource'; their backing resource lives inside the 'state'
    field — a JSON-encoded string whose parsed object carries a 'resource' key
    shaped as a URI dict ('path'/'fsPath', optionally 'scheme') or a 'file://'
    URI string. Falls back to top-level 'resourceJSON'/'resource'/'path' for
    older or alternate shapes.
    """
    try:
        obj = json.loads(value_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(obj, dict):
        return None
    state = obj.get("state")
    if isinstance(state, str):
        try:
            state = json.loads(state)
        except (json.JSONDecodeError, TypeError):
            state = None
    res = state.get("resource") if isinstance(state, dict) else None
    if isinstance(res, dict):
        fs = res.get("fsPath")
        if isinstance(fs, str) and fs:
            return fs
        p = res.get("path")
        if isinstance(p, str) and p:
            return p
    elif isinstance(res, str) and res:
        return _strip_file_uri(res)
    # Fallbacks for older / alternate shapes
    for key in ("resourceJSON", "resource"):
        top = obj.get(key)
        if isinstance(top, dict) and top.get("path"):
            return top["path"]
    if isinstance(obj.get("path"), str):
        return obj["path"]
    return None


def _strip_file_uri(value: str) -> str:
    """Strip a 'file://' prefix from a URI string, returning the path part."""
    if value.startswith("file://"):
        return value[len("file://"):]
    return value


def parse_editor_entry(editor: dict) -> dict:
    """Flatten a single editor entry into a normalized record.

    Every editor is classified by 'type' (file / webview / terminal / other)
    and given a display 'label'. File editors expose 'fs_path'; webview
    editors expose 'source_path' (the markdown/custom-editor backing file).
    """
    editor_id = editor.get("id", "")
    raw_value = editor.get("value", "")
    record: dict[str, Any] = {
        "editor_id": editor_id,
        "type": "other",
        "title": None,
        "fs_path": None,
        "source_path": None,
        "label": editor_id,
    }
    if raw_value:
        try:
            parsed = json.loads(raw_value)
        except (json.JSONDecodeError, TypeError):
            parsed = {}
        if isinstance(parsed, dict):
            if "title" in parsed:
                record["title"] = parsed["title"]
                record["label"] = parsed["title"]
            if editor_id == FILE_EDITOR_INPUT_ID:
                record["type"] = "file"
                record["fs_path"] = extract_fs_path(raw_value)
                if record["fs_path"] is not None:
                    record["label"] = record["fs_path"]
            elif editor_id == WEBVIEW_EDITOR_ID:
                record["type"] = "webview"
                record["source_path"] = extract_webview_source_path(raw_value)
                if record["source_path"] is not None:
                    record["label"] = record["source_path"]
            elif editor_id == TERMINAL_EDITOR_ID:
                record["type"] = "terminal"
                record["title"] = parsed.get("title", record.get("title"))
                if record["title"]:
                    record["label"] = record["title"]
    return record


def extract_editors(db_path: str, key: str = DEFAULT_KEY) -> dict:
    """Extract all open editors from a state.vscdb.

    Returns a dict with 'groups', 'total_editors', 'total_file_editors',
    and 'key_found' boolean.
    """
    raw = read_memento_value(db_path, key)
    if raw is None:
        return {
            "db_path": os.path.abspath(db_path),
            "memento_key": key,
            "key_found": False,
            "groups": [],
            "total_editors": 0,
            "total_file_editors": 0,
            "error": f"key '{key}' not found in {os.path.basename(db_path)}",
        }
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {
            "db_path": os.path.abspath(db_path),
            "memento_key": key,
            "key_found": True,
            "groups": [],
            "total_editors": 0,
            "total_file_editors": 0,
            "error": f"value is not valid JSON: {exc}",
        }

    # Navigate to the serializedGrid root.
    # The memento value has shape: {"editorpart.state": {"serializedGrid": {"root": {...}}}}
    ep = data.get("editorpart.state", {})
    grid = ep.get("serializedGrid", {}) if isinstance(ep, dict) else {}
    root = grid.get("root", {})

    leaves: list[dict] = []
    walk_grid(root, leaves)

    groups: list[dict] = []
    total = 0
    total_files = 0
    for grp in leaves:
        group_id = grp.get("id")
        sticky = grp.get("sticky", 0)
        mru = grp.get("mru", [])
        size = grp.get("size", 0)
        editors_raw = grp.get("editors", [])
        editors_out = []
        for idx, ed in enumerate(editors_raw):
            rec = parse_editor_entry(ed) if isinstance(ed, dict) else {
                "editor_id": "", "type": "other", "title": None,
                "fs_path": None, "source_path": None, "label": "",
            }
            rec["index"] = idx
            rec["pinned"] = idx < sticky
            rec["group_id"] = group_id
            rec["group_sticky"] = sticky
            editors_out.append(rec)
            total += 1
            if rec["fs_path"] is not None:
                total_files += 1
        groups.append({
            "group_id": group_id,
            "sticky": sticky,
            "size": size,
            "mru": mru,
            "editors": editors_out,
        })

    return {
        "db_path": os.path.abspath(db_path),
        "memento_key": key,
        "key_found": True,
        "groups": groups,
        "total_editors": total,
        "total_file_editors": total_files,
    }


def render_all(result: dict) -> str:
    """Render every tab in tab-bar order with [type] tags and # group markers.

    Each line is '[<type>      ] <label>[ [pinned]]', where <label> is the
    fs_path (file), the source path or title (webview), the title (terminal),
    or the editor_id (other). A '# group <id>' line precedes each leaf group
    with at least one editor, mirroring the on-screen split-view layout.
    """
    lines = []
    for grp in result.get("groups", []):
        editors = grp["editors"]
        if not editors:
            continue
        lines.append(f"# group {grp['group_id']}")
        for ed in editors:
            tag = " [pinned]" if ed["pinned"] else ""
            lines.append(f"[{ed['type']:<8}] {ed['label']}{tag}")
    return "\n".join(lines) if lines else "(no editors found)"


def render_files(result: dict) -> str:
    """Render the file-only projection: one absolute fsPath per line.

    Preserves the legacy text contract: pinned file editors are annotated
    with '[pinned]'; when no file editors exist, non-file tabs are emitted as
    '#non-file:' markers as a fallback.
    """
    lines = []
    for grp in result.get("groups", []):
        for ed in grp["editors"]:
            if ed["fs_path"] is not None:
                tag = " [pinned]" if ed["pinned"] else ""
                lines.append(f"{ed['fs_path']}{tag}")
    if lines:
        return "\n".join(lines)
    # Fallback: include non-file editors with a marker
    for grp in result.get("groups", []):
        for ed in grp["editors"]:
            if ed["fs_path"] is None:
                tag = " [pinned]" if ed["pinned"] else ""
                label = ed.get("title") or ed.get("label") or ed["editor_id"]
                lines.append(f"#non-file: {label}{tag}")
    return "\n".join(lines) if lines else "(no editors found)"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract open VS Code editor tabs + pinned order from a "
                    "state.vscdb database"
    )
    parser.add_argument(
        "--db", required=True,
        help="Absolute path to a VS Code state.vscdb SQLite file",
    )
    parser.add_argument(
        "--key", default=DEFAULT_KEY,
        help=f"Memento key to read (default: {DEFAULT_KEY})",
    )
    parser.add_argument(
        "--mode", choices=["all", "files"], default="all",
        help="Text output mode: 'all' = every tab (file/webview/terminal) "
             "with [type] tags and # group markers (default); "
             "'files' = file-only projection (one fsPath per line)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Emit machine-readable JSON instead of human text",
    )
    args = parser.parse_args()

    result = extract_editors(args.db, args.key)

    if result.get("error"):
        sys.stderr.write(f"WARNING: {result['error']}\n")

    if args.json:
        # Text annotations go to stderr so stdout is pure JSON
        if result.get("error"):
            sys.stderr.write(f"WARNING: {result['error']}\n")
        print(json.dumps(result, indent=2))
    else:
        renderer = render_all if args.mode == "all" else render_files
        print(renderer(result))


if __name__ == "__main__":
    main()
