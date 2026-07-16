---
name: agents-md-recovery-from-session
description: Apply extracted git diff from opencode session export to restore AGENTS.md; uses opencode-session-diff-extractor to get diff → apply → verify alphabetical order and fix markdownlint.
category: Meta-Automation
---

# AGENTS.md Recovery from Session Skill (v1)

## Composition Rationale

This skill is a **composer** over the base primitive
`opencode-session-diff-extractor`. The base skill extracts git diff
blocks from session exports generically. This composer applies that
extraction specifically to AGENTS.md recovery:

1. Extract diff from session file targeting `AGENTS.md`
2. Apply the diff to current AGENTS.md
3. Verify alphabetical order of skills table
4. Fix markdownlint errors

The composer's value-add: domain-specific recovery protocol with
verification steps that the generic extraction primitive doesn't know
about.

---

## Prerequisites

- AGENTS.md exists at `AGENTS.md` in repository root
- Session export file with lost diff available
- Git repository with clean working tree or non-critical changes acceptable

## Operational Procedure

### Step 1: Extract AGENTS.md Diff

Use `opencode-session-diff-extractor` to extract only the diff
affecting `AGENTS.md`:

```bash
python3 .agents/skills/opencode-session-diff-extractor/scripts/extract-session-diff.py \
  --session /path/to/session.md \
  --file-pattern AGENTS.md
```

**Expected output:** Unified diff starting with `diff --git a/AGENTS.md`.

**Error cases:**

- Exit code 1: No AGENTS.md diff found in session
- Exit code 2: Parse error reading session file
- Exit code 3: AGENTS.md file doesn't exist

### Step 2: Apply Diff to AGENTS.md

Apply the extracted diff to the working AGENTS.md:

```bash
git apply --3way .agents/skills/opencode-session-diff-extractor/scripts/extracted-diff.patch
```

**Verification:**

```bash
git diff --stat
```

Ensure the output shows changes only to `AGENTS.md` (no unexpected file
modifications).

**If conflict arises:**

```bash
git status  # Check 3-way merge conflict markers
# Manually resolve if needed, preserving intent of the diff
git add -A
```

### Step 3: Verify Skills Table Order

Inspect the skills table to ensure alphabetical ordering after the diff
was applied:

```bash
grep -A 200 "^## Skills$" AGENTS.md | head -n +7 | sed -n '1,200p' | sort --check
```

**Expected:** No output (sort succeeds silently).

**If ordering broken:**

- Re-read the diff to understand the intended insertion position
- Use `text-lines-sort-by-length` skill to sort the skills table
- Alternatively, edit manually to place rows in correct alphabetical
  position

### Step 4: Fix Markdownlint Errors

Check for markdownlint violations:

```bash
markdownlint --fix AGENTS.md
```

**Common errors from normal diff operations:**

- Missing trailing pipes in table columns (`| Key | Value |\` becomes
  `| Key || Value |`)
- Line length violations (>120 chars)

**Error codes:**

- Exit code 0: No issues or auto-fixed
- Exit code 1: Issues found but not auto-fixable

If manual fixes needed, read the `AGENTS.md` and edit specific lines.

### Step 5: Verify Changed Skills Exist

Confirm all rows added in the diff have corresponding
`.agents/skills/` directories and files:

```bash
git diff --name-only .agents/skills/
```

Review each new directory/file listed in the output, ensure SKILL.md and
AGENTS.md exist.

### Step 6: Final Verification

1. **Syntax check AGENTS.md:**

   ```bash
   markdownlint --strict AGENTS.md
   ```

2. **Validate git patch applies cleanly:**

   ```bash
   git apply --check .agents/skills/opencode-session-diff-extractor/scripts/extracted-diff.patch
   ```

3. **Confirm working tree status:**

   ```bash
   git status
   ```

**Success:** Only AGENTS.md appears as modified.

### Step 7: Commit Changes

```bash
git add AGENTS.md
git add .agents/skills/opencode-session-diff-extractor/scripts/extracted-diff.patch
git commit -m "$(cat <<'EOF'
agents-md-recovery: restore AGENTS.md from session export

Extracted diff from session export after accidental git checkout
HEAD -- AGENTS.md. Restored lost skills table entries.

Applied extracted diff, verified alphabetical order, fixed markdownlint.
EOF
)"
```

**Optional:** Push to remote to prevent future loss (if repo is cloned
for backup).

## CLI Interface

This skill can be invoked as a standalone CLI for scripts:

```bash
scripts/recover-agents-md.py --session /path/to/session.md [--commit] [--dry-run]
```

| Flag | Description |
|------|-------------|
| `--session` | Path to opencode session export (.md) |
| `--commit` | Automatically commit changes after successful recovery |
| `--dry-run` | Print extraction and apply steps without executing |
| `--branch <name>` | Create a new branch before recovery (default: `agents-md-recovery-$(date +%s)`) |

**Example:**

```bash
scripts/recover-agents-md.py \
  --session /path/to/session.md \
  --branch agents-md-recovery-2026-06-29 \
  --commit
```

## Composition by Lower-Level Skills

| Primitive | Composition Mechanism |
|-----------|----------------------|
| `opencode-session-diff-extractor` | Extracts `diff --git a/AGENTS.md` block from session file; emits to stdout/file |
| `text-lines-sort-by-length` | Optional step if skills table ordering is broken after diff |

## Error Handling

| Failure Mode | Detection | Recovery |
|--------------|-----------|----------|
| No AGENTS.md diff found in session | Exit code 1 from extractor | Verify session file, check for typo |
| AGENTS.md doesn't exist | Exit code 3 from extractor | Create AGENTS.md from git history or base template |
| Merge conflicts after git apply | `git status` shows conflict markers | Manually resolve, preserving diff intent |
| Skills table out of alphabetical order | Sort check returns error | Use `text-lines-sort-by-length` or manual edit |
| Markdownlint auto-fix fails | Exit code 1 from markdownlint | Inspect line-by-line using `markdownlint --output RADON` |

## Related Skills

- [`opencode-session-diff-extractor`](../opencode-session-diff-extractor/SKILL.md) —
  Base primitive for extracting git diffs from session exports
- [`skill-library-domain-grouping`](../general/skill-library-domain-grouping/SKILL.md) —
  Domain taxonomy and placement rules for skills
- [`text-lines-sort-by-length`](../text-lines-sort-by-length/SKILL.md) —
  Optional helper for reordering skills table if alphabetical order
  is broken after diff application

## Source Rules

- Generated: 2026-06-29 from session `ses_0ef9d288dffe17xKEI2evfdzOI`
- Context: AGENTS.md recovery after `git checkout HEAD -- AGENTS.md`
  in oleovista-acers repo
- Base skill origin:
  [`opencode-session-diff-extractor`](../opencode-session-diff-extractor/SKILL.md)
