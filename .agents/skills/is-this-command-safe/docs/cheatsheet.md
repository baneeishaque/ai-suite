---
name: Shell Command Safety Cheatsheet
description: Curated allowlist of common inspection-toolkit commands with safety verdicts and destructive-flag warnings.
category: Core Agent Behavior
---

# Shell Command Safety Cheatsheet

Quick-reference allowlist for commands a cautious developer or AI-agent supervisor wants
pre-vetted. Each entry uses the four-tier classification defined in
[`SKILL.md §3`](../SKILL.md#3-safety-classification-four-tiers).

Verdict key: ✅ SAFE · 🟡 SAFE-IF-PIPED · ⚠️ HAS-DESTRUCTIVE-FLAGS · ❌ MUTATES

***

## Simplified Safety Table

| Command / Binary | Verdict | Destructive form(s) | Safe alternative / dry-run |
| :--- | :---: | :--- | :--- |
| `brew leaves` | ✅ | — | n/a |
| `brew list` | ✅ | — | n/a |
| `brew outdated` | ✅ | — | n/a |
| `cat` | ✅ | — | n/a |
| `diff` | ✅ | — | n/a |
| `find` | 🟡 | `-delete` · `-exec rm` · `-exec mv` · `-exec sed -i` | `find … -print` first |
| `git branch -a` | ✅ | — | n/a |
| `git branch -vv` | ✅ | — | n/a |
| `git check-ignore` | ✅ | — | n/a |
| `git diff` | ✅ | — | n/a |
| `git log` | ✅ | — | n/a |
| `git ls-tree` | 🟡 | downstream `xargs` | inspect output alone first |
| `git merge-base` | ✅ | — | n/a |
| `git show` | ✅ | — | n/a |
| `git stash list` | ✅ | — | n/a |
| `git status` | ✅ | — | n/a |
| `grep` | 🟡 | `\| xargs rm` · `\| xargs sed -i` | `grep` alone |
| `head` | ✅ | — | n/a |
| `less` | ✅ | — | n/a |
| `lsof` | ✅ | — | n/a |
| `markdownlint-cli2` | ✅ / ⚠️ | `--fix` (edits files in-place) | omit `--fix` |
| `mdfind` | 🟡 | downstream `xargs` | `mdfind` alone |
| `mdls` | ✅ | — | n/a |
| `mkdir` | ❌ | always mutates | `ls -d <path>` to check existence first |
| `tail` | ✅ | — | n/a |
| `wc` | ✅ | — | n/a |

***

## File Search & Metadata

### `find`

- **Verdict**: 🟡 SAFE-IF-PIPED
- **What it does**: Traverses the filesystem and prints matching paths. By itself it is read-only.
- **Destructive forms**:
  - `find / -name "*.log" -delete` → deletes every match.
  - `find . -name "*.txt" -exec rm {} \;` → runs `rm` on each match.
  - `find . -name "*.js" -exec sed -i 's/foo/bar/g' {} \;` → in-place edit.
- **Safe workflow**: always run without action flags first to preview results, then add `-delete`
  or `-exec` only after confirming the match set.

```bash
# Safe preview
find /path -name "*.log" -print

# Only after confirming — destructive
find /path -name "*.log" -delete
```

### `mdfind`

- **Verdict**: 🟡 SAFE-IF-PIPED
- **What it does**: macOS Spotlight metadata search. Read-only output; safe alone.
- **Destructive form**: `mdfind … | xargs rm` — pipeline inherits downstream destructiveness.
- **Safe workflow**: inspect `mdfind` output alone before piping.

### `mdls`

- **Verdict**: ✅ SAFE
- **What it does**: Lists macOS extended metadata attributes (kMDItem*) of a file. Read-only.

***

## Text Search

### `grep`

- **Verdict**: 🟡 SAFE-IF-PIPED
- **What it does**: Searches file contents for patterns. Does not modify files.
- **Destructive pipeline**:
  - `grep -rl "debug" . | xargs rm` → deletes all files containing "debug".
  - `grep -rl "old" . | xargs sed -i 's/old/new/g'` → in-place mass replace.
- **Safe workflow**: run `grep` alone to confirm the match set, then decide on downstream action.

***

## File Viewing

### `cat`

- **Verdict**: ✅ SAFE — Prints file contents. No mutation possible.

### `head`

- **Verdict**: ✅ SAFE — Prints first N lines. Read-only.

### `tail`

- **Verdict**: ✅ SAFE — Prints last N lines (or follows a growing file). Read-only.

### `less`

- **Verdict**: ✅ SAFE — Paginated viewer. No mutation.

### `wc`

- **Verdict**: ✅ SAFE — Counts lines, words, bytes. Read-only.

***

## Diffing

### `diff`

- **Verdict**: ✅ SAFE — Compares files line-by-line, output only. No files modified.

### `git diff`

- **Verdict**: ✅ SAFE — Shows working-tree or commit-to-commit diffs. Read-only.

***

## Git Read-Only Inspection

All the commands in this section are ✅ SAFE when invoked as documented.
Destructive git commands (`push --force`, `reset --hard`, `clean -fd`, `rebase`) are catalogued
in [`SKILL.md §4`](../SKILL.md#4-destructive-flag-inventory-non-exhaustive-authoritative).

### `git status`

- **Verdict**: ✅ SAFE — Reports staged, unstaged, and untracked changes. Read-only.

### `git log`

- **Verdict**: ✅ SAFE — Enumerates commit history with metadata. Read-only.

### `git ls-tree`

- **Verdict**: 🟡 SAFE-IF-PIPED — Lists tree objects. Output can be piped; classify the full
  pipeline if a downstream command is added.

### `git branch -a` / `git branch -vv`

- **Verdict**: ✅ SAFE — Lists local and remote-tracking branches (with upstream info). Read-only.

### `git merge-base`

- **Verdict**: ✅ SAFE — Finds the best common ancestor between two commits. Read-only.

### `git check-ignore`

- **Verdict**: ✅ SAFE — Tests whether paths would be excluded by `.gitignore` rules. Read-only.

### `git show`

- **Verdict**: ✅ SAFE — Shows commit objects, diffs, tree entries, blobs. Read-only.

### `git stash list`

- **Verdict**: ✅ SAFE — Enumerates the stash stack (`stash@{N}` refs with subjects). Read-only.
- **Contrast**: `git stash push`, `git stash pop`, `git stash apply`, `git stash drop`,
  `git stash clear` all modify the stash stack or working tree and are ❌ MUTATES — NOT covered
  by this row.

***

## System / Process Inspection

### `lsof`

- **Verdict**: ✅ SAFE — Lists open files, sockets, and PIDs. Read-only.
- **Note**: `lsof` may require `sudo` to see processes owned by other users; `sudo` itself does
  not change the safety tier of `lsof`.

***

## Linters & Analysis Tools

### `markdownlint-cli2`

- **Verdict**: ✅ SAFE (without `--fix`) / ⚠️ HAS-DESTRUCTIVE-FLAGS (with `--fix`)
- **Without `--fix`**: linting only — reports rule violations, no files changed.
- **With `--fix`**: modifies Markdown files in-place. Confirm the match set by running without
  `--fix` first.

***

## Filesystem Mutation (for contrast)

### `mkdir`

- **Verdict**: ❌ MUTATES — Creates directories. Always mutates the filesystem.
- **Idempotent but still MUTATES**: `mkdir -p <path>` avoids errors if the path exists, but the
  operation itself is still a mutation — a new directory may be created.
- **Safe check before**: `ls -d <path> 2>/dev/null` to test existence without creating.

***

## Package Management Inspection

### `brew leaves`

- **Verdict**: ✅ SAFE — Lists explicitly installed (leaf) formulae. Read-only.
- **Common flag**: `--installed-on-request` narrows output to user-requested installs (excludes
  packages auto-installed as dependencies).
- **Contrast**: `brew install`, `brew upgrade`, `brew uninstall`, `brew cleanup` are all ❌ MUTATES
  and are NOT covered by this row.

### `brew list`

- **Verdict**: ✅ SAFE — Lists installed packages. Read-only.
- **Common flags**: `--cask` (casks only), `--formula` (formulae only). Both remain read-only.

### `brew outdated`

- **Verdict**: ✅ SAFE — Lists outdated formulae/casks. Read-only.
- **Common flag**: `--greedy` includes casks with `auto_updates` or `version :latest`.
- **Contrast**: `brew upgrade` (with or without `--greedy`) is ❌ MUTATES.

***

## Non-CLI Tokens

### `agy`

- **Not a shell binary.** `agy` refers to the **Google Antigravity** IDE-embedded agentic
  assistant (an AI agent layer on top of VS Code). It is not a command-line tool and has no
  applicable shell safety verdict under this skill. For Antigravity agent behavior, consult the
  [Antigravity Version Checker skill](../../antigravity-version-checker/SKILL.md).

***

## Dangerous Pipeline Catalogue

The following pipeline patterns are always `MUTATES` regardless of the source binary:

| Pattern | Effect |
| :--- | :--- |
| `<any> \| xargs rm` | Deletes files matching the upstream output. |
| `<any> \| xargs sed -i` | In-place edits files matching the upstream output. |
| `<any> > existing-file` | Truncates and overwrites the target file. |
| `<any> \| tee existing-file` | Truncates and overwrites (without `-a`). |
| `<any> \| sh` / `\| bash` | Executes upstream output as shell commands. |
| `$(rm …)` / `` `rm …` `` | Inline mutation inside a larger command. |

***

## Adding New Entries

Follow the Append-Only Protocol in [`SKILL.md §8`](../SKILL.md#8-extending-the-allowlist-append-only-protocol).
Add the new row to [`safety-table.csv`](./safety-table.csv) and a new section here at the correct
alphabetical position within its category.
