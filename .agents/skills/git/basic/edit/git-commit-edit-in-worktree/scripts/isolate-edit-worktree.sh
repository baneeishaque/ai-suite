# !/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: $0 --repo <path> --worktree-path <path> --branch <name> --base-ref <ref> --target-sha <sha> --sequence-editor <path> [--action drop|edit]"
    exit 2
}

REPO=""
WORKTREE=""
BRANCH=""
BASE_REF=""
TARGET_SHA=""
SEQ_EDITOR=""
ACTION="drop"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo) REPO="$2"; shift 2 ;;
        --worktree-path) WORKTREE="$2"; shift 2 ;;
        --branch) BRANCH="$2"; shift 2 ;;
        --base-ref) BASE_REF="$2"; shift 2 ;;
        --target-sha) TARGET_SHA="$2"; shift 2 ;;
        --sequence-editor) SEQ_EDITOR="$2"; shift 2 ;;
        --action) ACTION="$2"; shift 2 ;;
        *) usage ;;
    esac
done

if [[ -z "$REPO" || -z "$WORKTREE" || -z "$BRANCH" || -z "$BASE_REF" || -z "$TARGET_SHA" || -z "$SEQ_EDITOR" ]]; then
    usage
fi

if [[ ! -f "$SEQ_EDITOR" ]]; then
    echo "isolate-edit-worktree: sequence editor not found: $SEQ_EDITOR" >&2
    exit 1
fi

export GIT_PAGER=cat

git -C "$REPO" worktree add -b "$BRANCH" "$WORKTREE" HEAD

if [[ "$ACTION" == "drop" ]]; then
    SEQ_ARGS="$TARGET_SHA"
else
    SEQ_ARGS="$TARGET_SHA --edit $TARGET_SHA"
fi

(
    cd "$WORKTREE"
    GIT_SEQUENCE_EDITOR="python3 $SEQ_EDITOR $SEQ_ARGS" \
    GIT_EDITOR=true PAGER=cat git rebase -i "$BASE_REF"
    echo "isolate-edit-worktree: new tip: $(git rev-parse HEAD)"
)
