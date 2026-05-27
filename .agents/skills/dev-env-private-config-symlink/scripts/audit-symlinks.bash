#!/usr/bin/env bash
# audit-symlinks.bash
# Walks a directory for symlinks pointing at any path containing a configurable
# private-repo marker (default: configurations-private) and reports per link:
# target absolute path, target-exists?, case-matches?, consumer hit count.
#
# Usage:
#   ./audit-symlinks.bash [--marker configurations-private] [--root .]
#
# Exit code 0 if every link resolves AND every linked file has >=1 consumer;
# exit code 1 if any link is broken or any linked file has zero consumers.

set -uo pipefail

MARKER="configurations-private"
ROOT="."

while [[ $# -gt 0 ]]; do
    case "$1" in
        --marker) MARKER="$2"; shift 2;;
        --root)   ROOT="$2"; shift 2;;
        -h|--help)
            sed -n '2,13p' "$0"
            exit 0;;
        *) echo "Unknown arg: $1" >&2; exit 2;;
    esac
done

EXITCODE=0
echo "Auditing symlinks under $ROOT containing marker '$MARKER'..."
echo

# Collect candidate links via process substitution into an array (set -e safe).
LINKS=()
while IFS= read -r l; do
    tgt=$(readlink "$l" 2>/dev/null || true)
    [[ "$tgt" == *"$MARKER"* ]] && LINKS+=("$l")
done < <(find "$ROOT" -type l 2>/dev/null)

if [[ ${#LINKS[@]} -eq 0 ]]; then
    echo "No symlinks containing marker found."
    exit 0
fi

for link in "${LINKS[@]}"; do
    raw_target=$(readlink "$link" 2>/dev/null || echo "")
    # readlink -f may fail when target doesn't exist; tolerate.
    resolved=$(readlink -f "$link" 2>/dev/null || echo "")
    base=$(basename "$link")

    exists="NO"
    [[ -n "$resolved" && -e "$resolved" ]] && exists="YES"

    case_status="N/A"
    if [[ "$exists" == "YES" && "$raw_target" == /* ]]; then
        real_dir=$(cd "$(dirname "$resolved")" 2>/dev/null && pwd -P || echo "")
        real="$real_dir/$(basename "$resolved")"
        if [[ "$real" == "$raw_target" ]]; then
            case_status="OK"
        else
            case_status="MISMATCH (target: $raw_target, real: $real)"
        fi
    elif [[ "$exists" == "YES" && "$raw_target" != /* ]]; then
        case_status="relative (skipped)"
    fi

    consumers=$(grep -rl --include="*.kt" --include="*.java" --include="*.dart" \
                          --include="*.js" --include="*.ts" --include="*.py" \
                          "$base" "$ROOT" 2>/dev/null | wc -l | tr -d ' ')

    echo "Link:       $link"
    echo "  Target:   $raw_target"
    echo "  Resolved: ${resolved:-<unresolved>}"
    echo "  Exists:   $exists"
    echo "  Case:     $case_status"
    echo "  Consumers: $consumers"
    echo

    [[ "$exists" == "NO" ]] && EXITCODE=1
    [[ "$consumers" == "0" ]] && EXITCODE=1
done

exit $EXITCODE
