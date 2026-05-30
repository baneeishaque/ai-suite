---
name: shellcheck-fixer
version: 1.0.0
description: Repair shell scripts to satisfy ShellCheck — refactor over suppress, prefer structural fixes (quoting, arrays, native bash string ops, split declaration/assignment) over `# shellcheck disable=` pragmas, with mandatory pre/post `shellcheck` verification and educational reporting per fix.
---

# Shellcheck Fixer Skill

> **Skill ID:** `shellcheck-fixer`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Industrial protocol for fixing ShellCheck (`SCxxxx`) findings in shell
scripts. The default disposition is **refactor**, not **suppress** —
`# shellcheck disable=SCxxxx` is reserved for cases where the safe fix
would introduce unacceptable complexity or behavioural risk, and even
then must be justified in an inline comment.

This skill operationalizes the (now-decommissioned)
`shellcheck-fixer-rules.md` rule file. It is delegated to whenever an
agent is asked to repair, harden, or lint shell scripts against
ShellCheck.

## Source Rules

| Rule File | Coverage |
|---|---|
| `shellcheck-fixer-rules.md` (decommissioned in this commit) | 100% — Core principles, Diagnosis, Fix strategies (SC2086 / SC2001 / SC2155), Verification, Tooling, Interaction style |

## Prerequisites

| Requirement | Minimum |
|---|---|
| `shellcheck` | Any recent release (`brew install shellcheck` on macOS) |
| Shell | Bash 4+ (the target script's interpreter) |
| Optional | Homebrew (`brew`) for installation on macOS — if missing, offer
  to install Homebrew first |

## When to Apply

Apply this skill when:

- The user asks to "fix shellcheck warnings", "lint a bash script", or
  "make this script ShellCheck-clean"
- A CI pipeline reports `SCxxxx` findings against a shell script
- A code review surfaces unquoted expansions, command substitutions in
  declarations, or `sed`-for-string-manipulation anti-patterns

Do NOT apply when:

- The user asks to fix issues found by other linters (`harper`, `pylint`,
  `eslint`) — use the matching linter-specific skill
- The user explicitly asks to **suppress** all warnings — warn that this
  violates §1 and ask for explicit override per
  [git-atomic-commit-construction §14](../git-atomic-commit-construction/SKILL.md#step-14--user-requested-coupling--deviations)

---

## 1. Core Principles

The primary goal is to **fix** ShellCheck issues by refactoring code to
be safer and more robust, rather than simply suppressing warnings.

- **Refactor over Suppress** — Change the code structure (e.g., use
  arrays instead of unquoted strings) to satisfy the linter.
- **Suppress as Last Resort** — Only use `# shellcheck disable=SCxxxx`
  if the fix would introduce unacceptable complexity or risk. The
  disable MUST be scoped to the smallest possible line range and
  followed by an inline comment explaining why.
- **Safety First** — Ensure no behaviour changes occur unless the
  original behaviour was a bug. A "fix" that silently alters output,
  exit code, or argument splitting must be flagged to the user before
  application.

---

## 2. Operational Protocol

### 2.1 Diagnosis

- **Run ShellCheck**: Always verify the current state first.

  ```bash
  shellcheck <file>
  ```

- **Analyze Error**: Understand *why* each finding is flagged (word
  splitting, globbing, subshell variable scope, etc.) — do not blindly
  pattern-match the SC code.
- **Check Context**: Look for surrounding code that might be affected
  by a fix (callers that rely on word-splitting, traps that read the
  variable, etc.).

### 2.2 Fix Strategy Catalogue

The following catalogue is the canonical reference. Extend it as new
`SCxxxx` codes are encountered, but always pair the new entry with a
worked Bad/Fix example.

#### SC2086 — Double-Quote Variables

- **Standard fix**: Quote the variable: `"$VAR"`.
- **Array requirement**: If the variable is meant to expand into
  multiple arguments, **migrate to an array** — do NOT keep the
  unquoted form.

  ```bash
  # Bad
  cmd $ARGS

  # Fix
  read -r -a ARGS_ARRAY <<< "$ARGS"
  cmd "${ARGS_ARRAY[@]}"
  ```

#### SC2001 — `sed` vs Native String Manipulation

Prefer bash native string ops `${VAR//old/new}` over piping to `sed`
for simple replacements (saves a subshell + `sed` process).

```bash
# Bad
new=$(echo "$VAR" | sed 's/old/new/g')

# Fix
new="${VAR//old/new}"
```

#### SC2155 — Masking Return Values

`local val=$(cmd)` swallows `cmd`'s exit code (the `local` builtin
always returns 0). Split the declaration from the assignment so the
assignment's exit status surfaces.

```bash
# Bad
local val=$(cmd)

# Fix
local val
val=$(cmd)
```

### 2.3 Verification

- **Post-Fix Check**: Run `shellcheck <file>` again immediately after
  applying the fix to confirm resolution and that no new findings were
  introduced.
- **Regression Check**: Ensure the script still runs as intended (if
  execution is safe and reproducible). For destructive scripts, dry-run
  the changed code path on a copy or in a container.

---

## 3. Tooling & Environment

### 3.1 System Check (macOS focus)

1. **Check availability**: `which shellcheck`
2. **Install via Homebrew**: If missing, `brew install shellcheck`.
3. **Install Homebrew**: If `brew` is missing, offer to install
   Homebrew first (delegate to `system-wide-tool-management` skill when
   available).

### 3.2 CI/CD Integration

Work seamlessly with existing CI pipelines that enforce linting. When
fixing for CI, run the same `shellcheck` invocation locally as the CI
job (read `.github/workflows/*.yml` or equivalent for the exact flags)
to avoid local-pass / CI-fail divergence.

---

## 4. Interaction Style

- **Concise** — State the error code (`SCxxxx`) and the fix method in
  one line per finding.
- **Educational** — Briefly explain *why* the original code was unsafe
  (e.g., "Unquoted expansion allows accidental globbing and word
  splitting on whitespace in `$VAR`").
- **Report format** — When reporting back to the user, group fixes by
  file and list `<file>:<line> SCxxxx — <one-line description> → <fix
  applied>`.

---

## Prohibited Behaviours

The agent is **BLOCKED** from:

- Suppressing a finding (`# shellcheck disable=...`) without first
  attempting a refactor fix and documenting why the refactor was
  rejected.
- Applying a fix that silently changes script behaviour (e.g.,
  quoting a variable that callers were relying on to word-split)
  without user confirmation.
- Skipping the post-fix `shellcheck` re-run.
- Bulk-disabling findings at the file scope (`# shellcheck
  disable=SCxxxx` at the top of the file) as a substitute for fixing.

## Related Skills

- [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
  — for committing the fixes as a focused `fix(shellcheck): …` commit
  (or `style(shellcheck): …` when the change is purely cosmetic).
- [`system-wide-tool-management`](../system-wide-tool-management/SKILL.md)
  — for installing `shellcheck` and Homebrew when missing.
- [`harper-linting-suppression`](../harper-linting-suppression/SKILL.md)
  — analogous pattern for the Harper prose linter (suppression
  discipline).

## Common Pitfalls

| Pitfall | Solution |
|---|---|
| Quoted `$ARGS` and the command now sees one big string | Migrate to an array (`read -r -a ARGS_ARRAY <<< "$ARGS"`) and expand `"${ARGS_ARRAY[@]}"` |
| `local val=$(cmd)` "fixed" by quoting only — exit code still masked | Must split declaration and assignment (`local val; val=$(cmd)`) |
| Replaced `sed 's/old/new/g'` with `${VAR/old/new}` (single replacement) | Use the double-slash form `${VAR//old/new}` for global replacement |
| File-level `# shellcheck disable=` left in place "for now" | Replace with per-line scoped suppression and an inline justification, or refactor properly |
| Local `shellcheck` passes, CI fails | Read the CI workflow for the exact `shellcheck` flags (`-x`, `--shell=bash`, `--severity=…`) and reproduce locally |
