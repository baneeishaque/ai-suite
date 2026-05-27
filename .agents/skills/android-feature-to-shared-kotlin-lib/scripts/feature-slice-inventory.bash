#!/usr/bin/env bash
# feature-slice-inventory.bash
# Given a feature name fragment and an Android source root, list the likely
# vertical-slice files (Activity, layout XML, ApiWrapper / API methods,
# string resources) that constitute the feature.
#
# Usage:
#   ./feature-slice-inventory.bash --feature <name> --root <android-src-root>
#
# Exit code 0 if at least one file matches; 1 otherwise.

set -uo pipefail

FEATURE=""
ROOT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --feature) FEATURE="$2"; shift 2;;
        --root)    ROOT="$2"; shift 2;;
        -h|--help) sed -n '2,12p' "$0"; exit 0;;
        *) echo "Unknown arg: $1" >&2; exit 2;;
    esac
done

if [[ -z "$FEATURE" || -z "$ROOT" ]]; then
    echo "Usage: $0 --feature <name> --root <android-src-root>" >&2
    exit 2
fi

if [[ ! -d "$ROOT" ]]; then
    echo "Root not a directory: $ROOT" >&2
    exit 2
fi

# Normalise feature variants: PascalCase, snake_case, camelCase, kebab-case
FEAT_LOWER=$(echo "$FEATURE" | tr '[:upper:]_-' '[:lower:]  ' | tr -d ' ')
FEAT_PASCAL=$(echo "$FEATURE" | awk -F'[_ -]' '{out=""; for(i=1;i<=NF;i++) out=out toupper(substr($i,1,1)) substr($i,2); print out}')
FEAT_SNAKE=$(echo "$FEATURE" | sed -E 's/([A-Z])/_\L\1/g; s/^_//; s/[ -]/_/g')

echo "Feature variants:"
echo "  lower:  $FEAT_LOWER"
echo "  pascal: $FEAT_PASCAL"
echo "  snake:  $FEAT_SNAKE"
echo

echo "=== Activities & Kotlin/Java source ==="
find "$ROOT" \( -name "*.java" -o -name "*.kt" \) 2>/dev/null \
    | grep -iE "$FEAT_LOWER|$FEAT_PASCAL|$FEAT_SNAKE" || echo "(none)"
echo

echo "=== Layout XML ==="
find "$ROOT" -path "*/res/layout/*.xml" 2>/dev/null \
    | grep -iE "$FEAT_LOWER|$FEAT_SNAKE" || echo "(none)"
echo

echo "=== ApiWrapper / Api method references ==="
grep -rln --include="*.java" --include="*.kt" -iE "$FEAT_LOWER|$FEAT_PASCAL" "$ROOT" 2>/dev/null \
    | xargs -I{} sh -c 'grep -l -iE "ApiWrapper|@POST|@GET|interface Api" "$1" 2>/dev/null' _ {} \
    | sort -u || echo "(none)"
echo

echo "=== String resources ==="
find "$ROOT" -path "*/res/values*/strings.xml" 2>/dev/null \
    | xargs grep -l -iE "$FEAT_LOWER|$FEAT_SNAKE" 2>/dev/null || echo "(none)"
