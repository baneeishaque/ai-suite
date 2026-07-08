---
name: git-apply-patch-cleanup
description: Domain-agnostic base primitive for applying a git patch file with verification and optional source cleanup.
category: Git-Operations
---

# git-apply-patch-cleanup

Domain-agnostic base primitive for applying a git patch file with
verification and optional source cleanup. This skill encapsulates the
workflow: validate patch → optionally preview → apply → optionally
delete source.

**Skill ID:** `git-apply-patch-cleanup` (lint-conformant single-segment
name per [ai-rule-standardization-rules.md §2 Skill-Name Precision
Mandate](../../../ai-agent-rules/ai-rule-standardization-rules.md))

---

## Composition Rationale

This skill is a **base skill** (domain-agnostic primitive). It owns ONLY the generic workflow:

1. Verify `git` available and inside a git repo
2. `git apply --check` to validate patch applies cleanly
3. Optional: `git apply --stat` / `--dry-run` for preview
4. `git apply` to actually apply
5. Optional: `rm -f <patch-file>` cleanup

Multiple composer skills can pipe their domain-specific patch discovery
into this base skill via its public CLI contract (`scripts/apply-patch`).
Inlining this primitive into each composer would split the SSOT and
silently diverge bug fixes.

**Known composers** (listed for bidirectional discoverability per
[skill-factory §5.2.1](../skill-factory/SKILL.md)):

| Composer | Composition Mechanism |
|---|---|
| `acers-patch-import` (planned) | Shells out to `scripts/apply-patch <patch> --cleanup` after staging patch from ACERS staging bucket |
| `staging-patch-apply` (planned) | Composes this base after fetching patch from staging environment |

---

## Environment & Dependencies

**Required tools** (verified at runtime):

| Tool | Minimum Version | Verification Command |
|------|-----------------|---------------------|
| `git` | 2.20+ | `git --version` |
| `bash` | 4.0+ | `bash --version` |

**Runtime preflight** (executed by `scripts/apply-patch`):

```bash
# 1. git available
command -v git >/dev/null || { echo "git not found"; exit 1; }

# 2. Inside git repo
git rev-parse --git-dir >/dev/null 2>&1 || { echo "Not in git repo"; exit 1; }
```

---

## Operational Procedure

### CLI Contract

```bash
scripts/apply-patch <patch-file> [--cleanup] [--dry-run] [--stat] [--check-only] [--verbose] [--help]
```

| Flag | Description |
|------|-------------|
| `--cleanup` | Delete `<patch-file>` after successful apply |
| `--dry-run` | Run `git apply --check` only; no working tree modification |
| `--stat` | Run `git apply --stat` and print summary; implies `--dry-run` |
| `--check-only` | Alias for `--dry-run` |
| `--verbose` | Print each `git` command before execution |
| `--help` | Show usage (from `scripts/apply-patch.usage.template`) |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (applied, or dry-run/check passed) |
| 1 | Usage error / missing dependency / not in git repo |
| 2 | Patch file not found or unreadable |
| 3 | `git apply --check` failed (patch does not apply cleanly) |
| 4 | `git apply` failed during actual application |
| 5 | Cleanup failed (patch applied but `rm` failed) |

### Step-by-Step Flow

1. **Parse arguments** — exactly one positional `<patch-file>` required
2. **Verify environment** — `git` in PATH, inside git repo (`git rev-parse --git-dir`)
3. **Validate patch file** — exists, readable, non-empty
4. **Check apply cleanliness** — `git apply --check <patch-file>` (exit 3 on failure)
5. **Dry-run / stat mode** — if `--stat` or `--dry-run`: `git apply --stat` and exit 0
6. **Apply patch** — `git apply <patch-file>` (exit 4 on failure)
7. **List applied files** — `git diff --name-only HEAD` printed to stdout
8. **Optional cleanup** — if `--cleanup`: `rm -f <patch-file>` (exit 5 on failure)

---

## Scripts

| Script | Tier | Purpose |
|--------|------|---------|
| [`scripts/apply-patch`](scripts/apply-patch) | 2 (Bash) | Main executable implementing the CLI contract above |
| [`scripts/apply-patch.usage.template`](scripts/apply-patch.usage.template) | — | Usage template read at runtime by `apply-patch` |

**Language selection rationale:** Tier 2 (Bash) per [Scripting Language
Selection Rules §3.2](../../../ai-agent-rules/scripting-language-selection-rules.md)
— script body IS shell glue (100% native binary invocation: `git`, `rm`,
`cat`). Python would add unnecessary process overhead.

**Portable anchored paths:** Script resolves its own directory via
`SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` to load
the usage template, so invocation works from any `cwd`.

---

## Verification

### Manual Smoke Test

```bash
# 1. Create a test repo
cd /tmp && mkdir test-patch && cd test-patch && git init -q

# 2. Create a file and commit
echo "original" > file.txt && git add file.txt && git commit -q -m "init"

# 3. Create a patch that adds a line
cat > /tmp/test.patch <<'EOF'
diff --git a/file.txt b/file.txt
index 9daeafb..4f9c8b7 100644
--- a/file.txt
+++ b/file.txt
@@ -1 +1,2 @@
 original
+added line
EOF

# 4. Dry-run stat
bash /path/to/git-apply-patch-cleanup/scripts/apply-patch /tmp/test.patch --stat
# Expected: prints stat summary, exits 0

# 5. Apply with cleanup
bash /path/to/git-apply-patch-cleanup/scripts/apply-patch /tmp/test.patch --cleanup
# Expected: prints "file.txt", exits 0, patch file deleted

# 6. Verify applied
cat file.txt
# Expected: two lines "original" + "added line"
```

### Automated Verification (Skill Factory §3)

- [ ] **Redaction & Portability Audit** — Run `redaction-portability` skill on `SKILL.md`, `AGENTS.md`, scripts
- [ ] **Markdown Lint** — `markdownlint-cli2 --fix SKILL.md AGENTS.md` then `markdownlint-cli2 SKILL.md AGENTS.md`
- [ ] **Cross-Reference Audit** — `python3 .agents/skills/general/skill-cross-reference-audit/scripts/audit-cross-refs.py`
- [ ] **Invocation Audit** — `python3 .agents/skills/skill-factory/scripts/verify-doc-invocations.py SKILL.md`
- [ ] **Bridge Audit** — Confirm `AGENTS.md` exists, no frontmatter, 5 sections, 40-120 lines
- [ ] **Registration Audit** — Row inserted alphabetically in root `AGENTS.md`
- [ ] **Script Smoke Test** — Run from repo root and `/tmp` with test patch (see above)

---

## Traceability

**Source conversation:** Session where patch
`/Users/dk/lab-data/oleovista-acers/oleovista-acers-03-51-16.patch` was
applied to generate `session-ses_0f0e.md` and then deleted. See
`docs/conversations/2026-06-29-git-apply-patch-cleanup.md` (sanitized
via `redaction-portability`).

---

## Related Skills

- **Adjacent:** `git-atomic-commit-construction`, `git-submodule-selective-init-no-lfs`

---

## Change History

| Timestamp | Summary | Rationale |
|-----------|---------|-----------|
| [2026-06-29 04:45] | Initial v1 creation | Extracted from completed session workflow |
