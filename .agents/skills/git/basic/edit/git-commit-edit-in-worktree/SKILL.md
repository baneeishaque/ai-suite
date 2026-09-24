---
name: git-commit-edit-in-worktree
description: >-
  Composer — edit ANY commit (drop, amend, reword, edit) without touching
  the current working tree: worktree add a scratch branch, script the rebase
  todo (GIT_SEQUENCE_EDITOR), rebase inside the isolated worktree, amend /
  drop / reword, complete the rebase, git diff-tree parity vs the backup
  branch, then fast-forward the real branch with git reset --soft on the main
  worktree, push --force-with-lease, and clean up the worktree + backup.
category: Git & Repository Management
---

# Git Commit Edit In Worktree (v1)

> **Name:** git-commit-edit-in-worktree<br>
> **Description:** Composer — edit any commit (drop / amend / reword / edit)
> in an isolated `git worktree`, never touching the current working tree<br>
> **Category:** Git & Repository Management

## Composition Rationale

This skill is a composer. It does NOT re-implement the rebase-todo rewrite,
nor does it re-implement submodule commit discovery. It orchestrates two
base skills:

1. [`git-rebase-drop-noninteractive`](../git-rebase-drop-noninteractive/SKILL.md) —
   invoked as the `GIT_SEQUENCE_EDITOR`. Its `scripts/write-drop-todo.py`
   receives the target SHA list (via `--action drop` / `--action edit` /
   `--action reword` remap) and rewrites the todo non-interactively.
2. [`git-submodule-history-classification`](../../../../git/submodule/repair/
   git-submodule-history-classification/SKILL.md) —
   optional scoping input: its `scripts/classify-submodule-commits.py`
   locates the INTRO commit when the target is a submodule path, and its
   post-rebase zero-commits result is the verification evidence.

The composer's domain-specific value-add: the isolated-worktree lifecycle
(baseline capture → plan → backup → isolate → rebase → tree parity →
fast-forward → cleanup) with a dirty-main-worktree-preservation contract that
neither base provides. The core constraint: the current working tree MUST NOT
be touched — proven by byte/index-level baseline comparison, not a status
string (see Gate 1 and Gate 8).

Bidirectional discoverability: both bases list this composer in their
`## Composition by Higher-Level Skills` tables.

## Related Skills

- [`git-commit-edit`](../../../../git-commit-edit/SKILL.md) — in-place
  single-commit interactive editing; this composer is its worktree-isolated,
  dirty-tree-safe counterpart.
- [`git-pre-execution-safety-stash`](../../../../git-pre-execution-safety-stash/SKILL.md) —
  the canonical apply-not-pop safety stash used at Gate 3 when additional
  working-tree protection is required.

## Environment & Dependencies

| Requirement | Version | Notes |
| ----------- | ------- | ----- |
| Python | 3.12+ | For `scripts/plan-commit-edit.py` — stdlib only |
| Bash | 3.2+ (macOS) | For `scripts/isolate-edit-worktree.sh` — `set -euo pipefail` |
| Git | 2.x | `worktree`, `rebase -i`, `reset --soft` |

## Scripts

### `scripts/plan-commit-edit.py` — deterministic discovery half

| Argument | Required | Description |
| -------- | -------- | ----------- |
| `--repo <path>` | no | Repo root (default `.`). |
| `<target-sha>` | yes | Full or abbreviated commit SHA to edit. |
| `--action <drop\|edit\|reword>` | no | Todo action (default `drop`). |
| `--purpose <name>` | no | Purpose token for branch/worktree naming. |
| `--json` | no | Emit the plan as JSON. |

Emits: `repo`, `target_sha` (fully resolved), `action`, `base_ref`
(`<target>^`), `branch_name` (`rebase-<purpose>`), `backup_branch`
(`backup/pre-edit-<purpose>`), `worktree_path` (`<repo>/scratch/rebase-<purpose>`),
`sequence_editor` (absolute path to the sibling base's
`write-drop-todo.py` — resolved relative to this script's own location, so
invocation works regardless of `cwd`), and `sequence_args`. Exits `1` if the
base script is missing or the SHA does not resolve.

### `scripts/isolate-edit-worktree.sh` — CRUD orchestration

```text
--repo <path> --worktree-path <path> --branch <name> --base-ref <ref> --target-sha <sha> --sequence-editor <path> [--action drop|edit]
```

Note: for long drop lists with multiple SHAs, `--target-sha` accepts multiple
space-separated SHAs (pass the full list as one quoted argument).

Performs: `git worktree add -b <branch> <worktree-path> HEAD`, then inside
the worktree runs the scripted rebase (`GIT_SEQUENCE_EDITOR` + `GIT_EDITOR=true`),
then prints the new tip. Conflict resolution and cleanup are prose gates
below, not script steps.

## Protocol

> **Core constraint:** the current working tree MUST NOT be touched. Gates 1
> and 8 prove this with content-level evidence, not a status string.

1. **Baseline gate** — capture, BEFORE anything:
   - `git status --porcelain` snapshot;
   - index evidence: `git ls-files -s` + `git diff --cached --binary`
     hashed;
   - working-tree evidence: `git diff --binary` hashed;
   - untracked listing: `git ls-files --others --exclude-standard` hashed.
   The entire protocol MUST end with all four byte-identical (Gate 8).
2. **Plan gate** — `python3 <path>/scripts/plan-commit-edit.py <sha>`
   (with `--action` and `--purpose` as needed); show the intended operation
   (drop / edit / reword), the base ref, the scratch worktree path, and the
   todo scrub (target SHAs) to the user.
3. **Safety/backup gate** — `git branch backup/pre-edit-<purpose>` at the
   current HEAD; `git worktree add -b rebase-<purpose>
   <repo>/scratch/rebase-<purpose> HEAD`. Optionally also capture an
   apply-not-pop safety stash per
   [`git-pre-execution-safety-stash`](../../../../git-pre-execution-safety-stash/SKILL.md).
4. **Isolate/rebuild** — inside the worktree, run
   `scripts/isolate-edit-worktree.sh` (which wraps the
   `GIT_SEQUENCE_EDITOR`-scripted `git rebase -i <base-ref>` from
   [`git-rebase-drop-noninteractive`](../git-rebase-drop-noninteractive/SKILL.md)).
5. **Amend/reword/edit gate** — for `edit` stops: amend content and
   `git rebase --continue`; for conflicts: resolve, `git add`, then
   `GIT_EDITOR=true PAGER=cat git rebase --continue`. NEVER `git commit
   --amend` on a conflicted commit before continuing (it folds the staged
   resolution into the WRONG commit — see the base's pitfall table).
6. **Interruption recovery** — `git commit -C <sha>` (recreate the
   interrupted strip), then `GIT_EDITOR=true PAGER=cat git rebase
   --continue`.
7. **Tree-check gate** — `git rev-parse HEAD^{tree}` of the rewritten branch
   tip; verify the tree no longer contains the removed path(s) and that the
   tree delta vs `backup/pre-edit-<purpose>` matches the planned edit
   exactly (`git diff --stat backup/pre-edit-<purpose> HEAD` shows ONLY the
   intended files).
8. **Fast-forward gate on main** — on the main worktree:
   `git reset --soft rebase-<purpose>`; then re-run the Gate-1 baseline
   capture and compare byte-for-byte against the pre-edit evidence: index,
   working-tree diff, untracked listing, and `--porcelain` MUST all match.
   Any mismatch (e.g. the old index resurrecting a removed gitlink as a
   staged addition) is a STOP condition — do not commit or push.
9. **Cleanup gate** (after confirmation) — `git worktree remove
   <worktree-path>`, delete `backup/pre-edit-<purpose>` and
   `rebase-<purpose>` only after the user confirms the rewritten branch is
   verified.

## Composition by Higher-Level Skills

| Composer | Composition Mechanism |
| -------- | --------------------- |
| [`git-submodule-history-removal`](../../../../git/submodule/lifecycle/git-submodule-history-removal/SKILL.md) | Delegates its Isolate/Rebase/Fast-forward gates to this composer's protocol, passing the INTRO (+ optional POINTER-UPDATE) SHA list as the drop targets and consuming the Gate-8 baseline match as its own verification evidence. |

## Prohibited Behaviors

- **Running the rebase in the main worktree** — always the isolated worktree.
- **Proceeding past Gate 8 on any baseline mismatch** — staged resurrection
  of removed gitlinks is the canonical silent-failure mode.
- **`git reset --hard`** — the fast-forward is `reset --soft` by design;
  hard reset destroys user work.
- **Deleting the backup branch or worktree without user confirmation** —
  cleanup is a separate authorization gate.
- **Pushing** — push (`--force-with-lease`) is owned by the submodule-removal
  composer's push gate, not by this skill.

## Common Pitfalls

| Pitfall | Solution |
| ------- | -------- |
| `fatal: '<branch>' is already used by worktree at ...` | The branch name is taken — pick a fresh `--purpose` token. |
| Old index shows removed submodule as staged addition after `reset --soft` | Expected on the OLD base; resolve by migrating the dirty worktree onto the new base deliberately (preservation branch / index-preserving stash), never by committing the staged addition. |
| Rebase stops on `.gitmodules` conflict | Resolve, `git add .gitmodules`, `GIT_EDITOR=true git rebase --continue`. |
| `git commit --amend` mid-rebase after conflict resolution | Forbidden — it rewrites the previously-applied commit. Use `git rebase --continue`. |

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Traceability

See [TRACEABILITY.md](TRACEABILITY.md).
