#!/usr/bin/env python3
"""
resolve-vscode-setting.py
-------------------------
Resolve the JSON Schema (enum values, default, description, per-value
enumDescriptions, window-override defaults) for any VS Code (or VS
Code-family Electron app) setting by inspecting the installed app bundle
directly — independent of online docs which frequently lag behind Insiders
releases and are silent for forks (AntiGravity, Cursor, Codium, Windsurf).

Tier-1 Python per scripting-language-selection-rules.md §2: cross-platform
parity (macOS / Linux today; Windows discovery deferred per session
decision), no nested-heredoc hazard from a bash wrapper, no shellcheck
overhead, no encoding tax.

Usage:
    resolve-vscode-setting.py <setting.key> [--app <bundle-path>]

    <setting.key>   dotted VS Code setting id, e.g. workbench.editor.useModal
    --app <path>    explicit bundle path; otherwise auto-discovers among:
                      1. /Applications/Visual Studio Code - Insiders.app
                      2. /Applications/Visual Studio Code.app
                      3. /Applications/Antigravity.app
                      4. /Applications/Cursor.app
                      5. /usr/share/code-insiders/resources/app
                      6. /usr/share/code/resources/app

Exit codes:
    0  schema found and printed
    1  setting key not found in bundle
    2  bundle layout unrecognized / NLS file missing
    3  bad arguments

Output: a small markdown report to stdout — type, default, window-override
defaults (e.g. agentsWindow:{default:"all"}), top-level description, and a
per-enum-value description table.

Notes:
- workbench.desktop.main.js is minified but readable; setting registrations
  are emitted as object literals keyed by "<setting.key>":{...} with NLS
  strings replaced by d(<N>,null) placeholders that resolve against
  out/nls.messages.json (a flat array indexed by the numeric id).
- When a setting is contributed by an EXTENSION (not core), it will not
  appear in workbench.desktop.main.js. In that case, search each
  extension's package.json contributes.configuration block instead.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_BUNDLE_CANDIDATES = (
    "/Applications/Visual Studio Code - Insiders.app",
    "/Applications/Visual Studio Code.app",
    "/Applications/Antigravity.app",
    "/Applications/Cursor.app",
    "/usr/share/code-insiders/resources/app",
    "/usr/share/code/resources/app",
)


def discover_bundle(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.exists():
            sys.exit(f"ERROR: --app path does not exist: {p}")
        return p
    for candidate in DEFAULT_BUNDLE_CANDIDATES:
        p = Path(candidate)
        if p.exists():
            return p
    sys.exit(
        "ERROR: could not locate a VS Code-family app bundle; "
        "pass --app <path>"
    )


def resolve_app_dir(bundle: Path) -> Path:
    """Return the directory containing 'out/' inside the bundle."""
    for sub in (Path("Contents/Resources/app"), Path("resources/app"), Path(".")):
        candidate = bundle / sub
        if (candidate / "out").is_dir():
            return candidate
    sys.exit(f"ERROR: unrecognized bundle layout under: {bundle}")


def extract_schema_literal(bundle_js: Path, key: str) -> str:
    """Walk braces to extract the balanced object literal that follows
    '"<key>":{' in the minified bundle. Regex is insufficient because the
    literal contains nested arrays/objects and string literals with
    arbitrary content."""
    src = bundle_js.read_text(encoding="utf-8", errors="replace")
    needle = f'"{key}":{{'
    idx = src.find(needle)
    if idx < 0:
        print(
            f"ERROR: setting '{key}' not found in {bundle_js}",
            file=sys.stderr,
        )
        print(
            "HINT: settings contributed by extensions live in each "
            "extension's package.json contributes.configuration, NOT in "
            "workbench.desktop.main.js.",
            file=sys.stderr,
        )
        sys.exit(1)

    start = idx + len(needle) - 1  # position of opening '{'
    depth = 0
    in_str = False
    str_ch = ""
    escape = False
    end = None
    for i in range(start, len(src)):
        c = src[i]
        if in_str:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == str_ch:
                in_str = False
        else:
            if c in ("'", '"', "`"):
                in_str = True
                str_ch = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
    if end is None:
        sys.exit(f"ERROR: brace-balance failed for '{key}'")
    return src[start:end]


def load_nls(nls_path: Path) -> list[str]:
    return json.loads(nls_path.read_text(encoding="utf-8"))


def resolve_nls(nls: list[str], n: int) -> str:
    if 0 <= n < len(nls):
        return nls[n]
    return f"<unresolved nls id {n}>"


def find_enum(lit: str) -> list[str] | None:
    m = re.search(r"\benum:\[([^\]]*)\]", lit)
    if not m:
        return None
    raw = m.group(1)
    items = re.findall(r'"([^"]*)"|([\-\d\.]+|true|false|null)', raw)
    return [a if a else b for a, b in items]


def find_enum_desc_ids(lit: str) -> list[int] | None:
    m = re.search(r"\benumDescriptions:\[([^\]]*)\]", lit)
    if not m:
        return None
    return [int(x) for x in re.findall(r"d\((\d+),", m.group(1))]


def find_nls_field(lit: str, name: str) -> int | None:
    m = re.search(rf"\b{name}:d\((\d+),", lit)
    return int(m.group(1)) if m else None


def find_scalar(lit: str, name: str) -> str | None:
    pattern = (
        rf'\b{name}:('
        r'"(?:[^"\\]|\\.)*"'
        r"|[\-\d\.]+"
        r"|true|false|null"
        r"|\{[^}]*\}"
        r"|\[[^\]]*\])"
    )
    m = re.search(pattern, lit)
    return m.group(1) if m else None


def find_override_defaults(lit: str) -> list[tuple[str, str]]:
    """Find e.g. agentsWindow:{default:"all"} overrides."""
    out: list[tuple[str, str]] = []
    pattern = (
        r'(\w+Window):\{default:('
        r'"[^"]+"'
        r"|[\-\d\.]+"
        r"|true|false|null)\}"
    )
    for m in re.finditer(pattern, lit):
        out.append((m.group(1), m.group(2)))
    return out


def render(
    key: str,
    bundle_js: Path,
    literal: str,
    nls: list[str],
) -> None:
    enum_values = find_enum(literal)
    enum_desc_ids = find_enum_desc_ids(literal)
    desc_id = find_nls_field(literal, "description") or find_nls_field(
        literal, "markdownDescription"
    )
    description = resolve_nls(nls, desc_id) if desc_id is not None else None
    default = find_scalar(literal, "default")
    type_value = find_scalar(literal, "type")
    overrides = find_override_defaults(literal)

    print(f"# `{key}`")
    print()
    if description:
        print(description)
        print()
    print("| Property | Value |")
    print("| :--- | :--- |")
    if type_value:
        print(f"| type | `{type_value}` |")
    if default:
        print(f"| default | `{default}` |")
    for name, val in overrides:
        print(f"| default ({name}) | `{val}` |")
    print()

    if enum_values:
        print("| Enum value | Description |")
        print("| :--- | :--- |")
        for i, v in enumerate(enum_values):
            d = ""
            if enum_desc_ids and i < len(enum_desc_ids):
                d = resolve_nls(nls, enum_desc_ids[i])
            print(f'| `"{v}"` | {d} |')
        print()

    print("---")
    print(f"_Resolved from: {bundle_js}_")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve the JSON Schema of a VS Code-family setting by "
            "reading the installed app bundle directly."
        )
    )
    parser.add_argument(
        "key",
        help="Dotted VS Code setting id, e.g. workbench.editor.useModal",
    )
    parser.add_argument(
        "--app",
        default=None,
        help=(
            "Path to the *.app bundle (macOS) or resources/app dir (Linux). "
            "If omitted, auto-discovers."
        ),
    )
    args = parser.parse_args()

    bundle = discover_bundle(args.app)
    app_dir = resolve_app_dir(bundle)
    bundle_js = app_dir / "out" / "vs" / "workbench" / "workbench.desktop.main.js"
    nls_json = app_dir / "out" / "nls.messages.json"

    if not bundle_js.is_file():
        sys.exit(f"ERROR: workbench bundle JS not found: {bundle_js}")
    if not nls_json.is_file():
        sys.exit(f"ERROR: nls.messages.json not found: {nls_json}")

    literal = extract_schema_literal(bundle_js, args.key)
    nls = load_nls(nls_json)
    render(args.key, bundle_js, literal, nls)


if __name__ == "__main__":
    main()
