#!/usr/bin/env bash
#
# resolve-vscode-setting.bash
# ---------------------------
# Resolve the JSON Schema (enum values, default, description, per-value
# enumDescriptions) for any VS Code (or VS Code-family Electron app) setting
# by inspecting the app bundle directly — independent of online docs which
# frequently lag behind Insiders / forks (AntiGravity, Cursor, Codium,
# Windsurf, etc.).
#
# Usage:
#   resolve-vscode-setting.bash <setting.key> [--app <bundle-path>]
#
#   <setting.key>     dotted VS Code setting id, e.g. workbench.editor.useModal
#   --app <path>      path to the *.app bundle (macOS) or the resources/app
#                     directory (Linux/Windows). If omitted, auto-discovers
#                     in this order:
#                       1. /Applications/Visual Studio Code - Insiders.app
#                       2. /Applications/Visual Studio Code.app
#                       3. /Applications/Antigravity.app
#                       4. /Applications/Cursor.app
#                       5. /usr/share/code-insiders/resources/app
#                       6. /usr/share/code/resources/app
#
# Exit codes:
#   0  schema found and printed
#   1  setting key not found in bundle
#   2  bundle layout unrecognized / NLS file missing
#   3  bad arguments
#
# Output: a small markdown table to stdout:
#   - Default value (and any window-override defaults)
#   - One row per enum value (when applicable) with its enumDescription
#   - Top-level description
#
# Notes:
#   - The bundle's workbench.desktop.main.js is minified but readable;
#     setting registrations are emitted as object literals keyed by
#     "<setting.key>":{...} with NLS strings replaced by d(<id>,null)
#     placeholders that resolve against out/nls.messages.json (a flat array
#     indexed by the numeric id).
#   - When a setting is contributed by an EXTENSION (not core), it will not
#     appear in workbench.desktop.main.js. In that case, search each
#     extension's package.json contributes.configuration block instead.
#
# Bash extension justification: target is macOS/Linux app-bundle inspection
# requiring grep + python3 JSON parsing; PowerShell would add no portability
# value here since the bundle paths and JS minification format are inherently
# POSIX-shaped. Windows variant: document path swap in SKILL.md, not script.

set -euo pipefail

usage() {
    cat >&2 <<USAGE
Usage: $(basename "$0") <setting.key> [--app <bundle-path>]
USAGE
    exit 3
}

[ $# -ge 1 ] || usage
KEY="$1"; shift || true
APP=""
while [ $# -gt 0 ]; do
    case "$1" in
        --app) APP="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "unknown arg: $1" >&2; usage ;;
    esac
done

# Auto-discover the bundle if not provided.
if [ -z "$APP" ]; then
    for candidate in \
        "/Applications/Visual Studio Code - Insiders.app" \
        "/Applications/Visual Studio Code.app" \
        "/Applications/Antigravity.app" \
        "/Applications/Cursor.app" \
        "/usr/share/code-insiders/resources/app" \
        "/usr/share/code/resources/app"; do
        if [ -e "$candidate" ]; then APP="$candidate"; break; fi
    done
fi

if [ -z "$APP" ] || [ ! -e "$APP" ]; then
    echo "ERROR: could not locate a VS Code-family app bundle; pass --app <path>" >&2
    exit 2
fi

# Normalize APP -> resources/app directory.
if [ -d "$APP/Contents/Resources/app" ]; then
    APP_DIR="$APP/Contents/Resources/app"
elif [ -d "$APP/resources/app" ]; then
    APP_DIR="$APP/resources/app"
elif [ -d "$APP/out" ]; then
    APP_DIR="$APP"
else
    echo "ERROR: unrecognized bundle layout under: $APP" >&2
    exit 2
fi

BUNDLE_JS="$APP_DIR/out/vs/workbench/workbench.desktop.main.js"
NLS_JSON="$APP_DIR/out/nls.messages.json"

[ -f "$BUNDLE_JS" ] || { echo "ERROR: workbench bundle JS not found: $BUNDLE_JS" >&2; exit 2; }
[ -f "$NLS_JSON" ]  || { echo "ERROR: nls.messages.json not found: $NLS_JSON"   >&2; exit 2; }

# Extract the schema object for KEY from the minified bundle.
# The pattern emitted by VS Code's settings registry is:
#   "<key>":{type:...,enum:[...],default:...,description:d(N,null),...}
# We capture the brace-balanced literal that follows the key.
TMP_HIT="$(mktemp)"
trap 'rm -f "$TMP_HIT"' EXIT

# Use python for brace-balanced extraction (regex alone is unsafe for nested objects).
python3 - "$KEY" "$BUNDLE_JS" "$NLS_JSON" <<'ZZZ_PY_END_ZZZ'
import json, re, sys
key, bundle, nls_path = sys.argv[1], sys.argv[2], sys.argv[3]

src = open(bundle, "r", encoding="utf-8", errors="replace").read()
needle = f'"{key}":{{'
idx = src.find(needle)
if idx < 0:
    print(f"ERROR: setting '{key}' not found in {bundle}", file=sys.stderr)
    print("HINT: settings contributed by extensions live in each extension's",
          "package.json contributes.configuration, NOT in workbench.desktop.main.js.",
          file=sys.stderr)
    sys.exit(1)

# Walk braces to find the balanced object literal.
start = idx + len(needle) - 1   # position of the opening "{"
depth = 0
in_str = False
str_ch = ""
escape = False
end = None
for i in range(start, len(src)):
    c = src[i]
    if in_str:
        if escape: escape = False
        elif c == "\\": escape = True
        elif c == str_ch: in_str = False
    else:
        if c in ("'", '"', "`"):
            in_str = True; str_ch = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
if end is None:
    print(f"ERROR: brace-balance failed for '{key}'", file=sys.stderr)
    sys.exit(2)

literal = src[start:end]

# Resolve every d(<n>,null) NLS placeholder via nls.messages.json.
nls = json.load(open(nls_path, "r", encoding="utf-8"))

def resolve_nls(n: int) -> str:
    if 0 <= n < len(nls):
        return nls[n]
    return f"<unresolved nls id {n}>"

# Field extractors operating on the raw JS literal (good enough — fields are
# emitted in a stable shape by the registry).
def find_enum(lit):
    m = re.search(r'\benum:\[([^\]]*)\]', lit)
    if not m: return None
    raw = m.group(1)
    # Items are quoted strings or numeric/boolean literals.
    items = re.findall(r'"([^"]*)"|([\-\d\.]+|true|false|null)', raw)
    return [a if a else b for a, b in items]

def find_enum_descs(lit):
    m = re.search(r'\benumDescriptions:\[([^\]]*)\]', lit)
    if not m: return None
    return [int(x) for x in re.findall(r'd\((\d+),', m.group(1))]

def find_description(lit):
    m = re.search(r'\bdescription:d\((\d+),', lit)
    if not m: return None
    return resolve_nls(int(m.group(1)))

def find_markdown_description(lit):
    m = re.search(r'\bmarkdownDescription:d\((\d+),', lit)
    if not m: return None
    return resolve_nls(int(m.group(1)))

def find_default(lit):
    m = re.search(r'\bdefault:("(?:[^"\\]|\\.)*"|[\-\d\.]+|true|false|null|\{[^}]*\}|\[[^\]]*\])', lit)
    return m.group(1) if m else None

def find_type(lit):
    m = re.search(r'\btype:("(?:[^"\\]|\\.)*"|\[[^\]]*\])', lit)
    return m.group(1) if m else None

def find_override_defaults(lit):
    # e.g.  agentsWindow:{default:"all"}
    out = []
    for m in re.finditer(r'(\w+Window):\{default:("[^"]+"|[\-\d\.]+|true|false|null)\}', lit):
        out.append((m.group(1), m.group(2)))
    return out

enum  = find_enum(literal)
descs = find_enum_descs(literal)
desc  = find_description(literal) or find_markdown_description(literal)
deft  = find_default(literal)
typ   = find_type(literal)
overs = find_override_defaults(literal)

# Render.
print(f"# `{key}`")
print()
if desc:
    print(desc)
    print()
print("| Property | Value |")
print("| :--- | :--- |")
if typ:  print(f"| type | `{typ}` |")
if deft: print(f"| default | `{deft}` |")
for name, val in overs:
    print(f"| default ({name}) | `{val}` |")
print()

if enum:
    print("| Enum value | Description |")
    print("| :--- | :--- |")
    for i, v in enumerate(enum):
        d = ""
        if descs and i < len(descs):
            d = resolve_nls(descs[i])
        print(f"| `\"{v}\"` | {d} |")
    print()

print("---")
print(f"_Resolved from: {bundle}_")
ZZZ_PY_END_ZZZ
