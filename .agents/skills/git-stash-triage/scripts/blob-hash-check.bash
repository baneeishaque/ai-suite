#!/usr/bin/env bash
set -euo pipefail

# --- file-level metadata ------------------------------------------------
# Language: Bash (Tier-2 borderline — pure shell glue: git invocation +
#   string comparison + stdout report. No JSON/regex/structured data.
#   Justification: ssot `scripting-language-selection-rules` Tier-2 §3.4 —
#   the body IS shell glue (≥80% native-binary invocation in sequence).
#   Host may lack `pwsh` in agent contexts; Bash is universally available.)

# .. synopsis ..
#   blob-hash-check.bash --repo <path> --stash-n <N> [--ref-b <ref>]
#
# .. description ..
#   For every file that differs between stash@{N} and ref-b (default HEAD),
#   compare the per-file blob hash and emit a classification line:
#     IDENTICAL        <path>
#     DIFFERENT        <path>
#     not in stash     <path>
#     not in HEAD      <path>
#
#   Exit 0 on success. Exit 1 with a diagnostic on error.
#
# .. example ..
#   bash blob-hash-check.bash --repo /path/to/repo --stash-n 3
#
# .. notes ..
#   This is the executable SSOT for the blob-hash supersession check
#   documented in git-stash-triage SKILL.md §2.2 (Fast Supersession Check).
#   The skill's prose owns interpretation (All IDENTICAL → Bucket A).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  sed -n '/^# .. synopsis ..$/,/^$/p' "$0" | sed '1d;s/^#   //g'
  exit 1
}

# --- parse args ---------------------------------------------------------
repo=""
stash_n=""
ref_b="HEAD"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)    repo="$2";   shift 2 ;;
    --stash-n) stash_n="$2"; shift 2 ;;
    --ref-b)   ref_b="$2";  shift 2 ;;
    -h|--help) usage ;;
    *)         echo "ERROR: unknown argument: $1"; usage ;;
  esac
done

if [[ -z "$repo" || -z "$stash_n" ]]; then
  echo "ERROR: --repo and --stash-n are required" >&2
  usage
fi

if [[ ! -d "$repo/.git" && ! -f "$repo/.git" ]]; then
  echo "ERROR: not a git repository: $repo" >&2
  exit 1
fi

# --- main ---------------------------------------------------------------
stash_ref="stash@{$stash_n}"

# Verify stash exists
if ! git -C "$repo" rev-parse --verify "$stash_ref" &>/dev/null; then
  echo "ERROR: stash reference not found: $stash_ref" >&2
  exit 1
fi

# Verify ref-b exists
if ! git -C "$repo" rev-parse --verify "$ref_b" &>/dev/null; then
  echo "ERROR: ref-b not found: $ref_b" >&2
  exit 1
fi

any_mismatch=0

while IFS= read -r f; do
  [[ -z "$f" ]] && continue

  hash_stash=$(git -C "$repo" rev-parse "$stash_ref":"$f" 2>/dev/null || true)
  hash_ref=$(git -C "$repo" rev-parse "$ref_b":"$f" 2>/dev/null || true)

  if [[ "$hash_stash" == "$hash_ref" ]]; then
    echo "IDENTICAL      $f"
  elif [[ -z "$hash_stash" ]]; then
    echo "not in stash   $f"
  elif [[ -z "$hash_ref" ]]; then
    echo "not in $ref_b  $f"
  else
    echo "DIFFERENT      $f"
    any_mismatch=1
  fi
done < <(git -C "$repo" diff "$stash_ref" "$ref_b" --name-only)

exit $any_mismatch
