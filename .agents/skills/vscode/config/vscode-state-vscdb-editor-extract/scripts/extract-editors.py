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
emits the file-only projection for callers that want just source files:
local 'file'-scheme resources as absolute fsPaths, and non-file schemes
(e.g. 'gist://') as '#non-file:' URI markers rather than misrepresenting
their URI path as a local absolute path.

Key findings:
  - The 'editors[]' array on each leaf node is in display order (pinned first).
  - 'sticky: N' at the group level = the INCLUSIVE array index of the LAST
    pinned (sticky) editor — i.e. editors at index <= N are pinned. It is NOT a
    count, and it is ABSENT (undefined) when the group has no pinned editors.
    Verified against VS Code's EditorGroupModel: `isSticky(index)` returns
    `index <= this.sticky`, the field is initialized to -1, and `serialize()`
    emits `sticky: r >= 0 ? r : undefined`. The per-editor 'pinned' flag is NOT
    serialized — 'sticky' is the only signal.
  - 'mru: [...]' is a separate ordering axis (most-recently-used), NOT the
    tab-bar order.
  - 'memento/workbench.editors.files.textFileEditor' (view-state memento) is
    NOT a reliable source — it includes historically-closed editors.

Additional findings (webview/terminal support):
  - Webview tabs (workbench.editors.webviewEditor) carry their backing source
    file inside value['state'] — a JSON-encoded string whose parsed object has
    a 'resource' key (URI dict with 'path'/'fsPath', or a 'file://' string).
    Top-level 'resourceJSON'/'resource' are absent for webview entries.
  - The file-only projection silently dropped webview + terminal tabs, so it
    never matched the on-screen tab bar; '--mode all' is the faithful view.

Additional findings (non-file URI schemes):
  - A 'fileEditorInput' resource is not necessarily a local file. Virtual
    documents opened through extensions carry a non-'file' scheme (e.g.
    'gist://<gist-id>/<name>' from a Gist extension) in the same
    'resourceJSON' shape. Their 'path' field is a URI path, NOT an absolute
    filesystem path, and 'external' carries the complete locator.
  - File records therefore expose 'scheme'/'external'/'authority'/'uri'
    (additive fields); text output uses 'external' for non-'file' schemes so
    a namespace path is never presented as a local absolute path.

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


def extract_resource_info(value_json: str) -> dict[str, Any] | None:
    """Parse a fileEditorInput 'value' string and return its resource dict.

    The value JSON may use 'resourceJSON' (newer VS Code) or 'resource'
    (older forms). Both describe a URI with 'path', an optional 'fsPath',
    and — for virtual documents — a non-'file' 'scheme' plus 'authority' and
    a complete 'external' locator.
    """
    try:
        obj = json.loads(value_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(obj, dict):
        return None
    # Newer Code versions use resourceJSON; older forms use 'resource'.
    for key in ("resourceJSON", "resource"):
        res = obj.get(key)
        if isinstance(res, dict) and (res.get("path") or res.get("fsPath")):
            return res
    # Some forms store the path directly under 'path'.
    if isinstance(obj.get("path"), str):
        return {"path": obj["path"]}
    return None


def extract_fs_path(value_json: str) -> str | None:
    """Parse a fileEditorInput 'value' string and return its path field.

    For a local resource this is the absolute fsPath. For a virtual document
    (non-'file' scheme) it is the URI path, so callers MUST inspect 'scheme'
    before treating it as a filesystem location.
    """
    res = extract_resource_info(value_json)
    if res is None:
        return None
    path = res.get("path")
    if isinstance(path, str) and path:
        return path
    fs_path = res.get("fsPath")
    return fs_path if isinstance(fs_path, str) and fs_path else None


def _build_uri(info: dict[str, Any]) -> str | None:
    """Return the complete locator for a resource dict.

    Prefers the serialized 'external' URI (e.g. 'gist://<id>/<name>' or
    'file:///abs/path'); otherwise reconstructs a non-'file' URI from its
    scheme/authority/path, or a 'file://' URI from the path for local
    resources.
    """
    external = info.get("external")
    if isinstance(external, str) and external:
        return external
    path = info.get("path")
    if not isinstance(path, str) or not path:
        fs_path = info.get("fsPath")
        path = fs_path if isinstance(fs_path, str) and fs_path else None
    scheme = info.get("scheme")
    if not isinstance(scheme, str) or not scheme or scheme == "file":
        return f"file://{path}" if path else None
    authority = info.get("authority")
    authority = authority if isinstance(authority, str) else ""
    if not path:
        return None
    return f"{scheme}://{authority}{path}" if authority else f"{scheme}:{path}"


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
    and given a display 'label'. File editors expose 'fs_path' plus the URI
    fields 'scheme' / 'external' / 'authority' / 'uri'; webview editors expose
    'source_path' (the markdown/custom-editor backing file).
    """
    editor_id = editor.get("id", "")
    raw_value = editor.get("value", "")
    record: dict[str, Any] = {
        "editor_id": editor_id,
        "type": "other",
        "title": None,
        "fs_path": None,
        "source_path": None,
        "scheme": None,
        "external": None,
        "authority": None,
        "uri": None,
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
                info = extract_resource_info(raw_value)
                record["fs_path"] = extract_fs_path(raw_value)
                if info is not None:
                    scheme = info.get("scheme")
                    record["scheme"] = (
                        scheme if isinstance(scheme, str) and scheme else "file"
                    )
                    external = info.get("external")
                    record["external"] = (
                        external if isinstance(external, str) and external else None
                    )
                    authority = info.get("authority")
                    record["authority"] = (
                        authority if isinstance(authority, str) and authority else None
                    )
                    record["uri"] = _build_uri(info)
                if record["fs_path"] is not None:
                    if record["scheme"] not in (None, "file"):
                        record["label"] = record["uri"] or record["fs_path"]
                    else:
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
        # 'sticky' is the INCLUSIVE index of the last pinned editor, or absent
        # when nothing is pinned. Default -1 (no pinned) so `idx <= sticky` is
        # always False for a pinned-free group.
        sticky = grp.get("sticky", -1)
        mru = grp.get("mru", [])
        size = grp.get("size", 0)
        editors_raw = grp.get("editors", [])
        editors_out = []
        for idx, ed in enumerate(editors_raw):
            rec = parse_editor_entry(ed) if isinstance(ed, dict) else {
                "editor_id": "", "type": "other", "title": None,
                "fs_path": None, "source_path": None, "scheme": None,
                "external": None, "authority": None, "uri": None, "label": "",
            }
            rec["index"] = idx
            # Sticky is the last-pinned index (inclusive): pinned iff idx <= sticky.
            rec["pinned"] = idx <= sticky
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
    """Render the file-only projection.

    Local 'file'-scheme resources are emitted as one absolute fsPath per line.
    File-editor resources with a non-'file' scheme (e.g. 'gist://') are emitted
    as '#non-file:' URI markers so their URI path is never mistaken for a local
    absolute path. Pinned file rows are annotated with '[pinned]'. When no file
    editors exist at all, non-file tabs are emitted as '#non-file:' markers as
    a fallback.
    """
    lines = []
    for grp in result.get("groups", []):
        for ed in grp["editors"]:
            if ed["fs_path"] is None:
                continue
            tag = " [pinned]" if ed["pinned"] else ""
            scheme = ed.get("scheme") or "file"
            if scheme == "file":
                lines.append(f"{ed['fs_path']}{tag}")
            else:
                locator = ed.get("uri") or ed["fs_path"]
                lines.append(f"#non-file: {locator}{tag}")
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
