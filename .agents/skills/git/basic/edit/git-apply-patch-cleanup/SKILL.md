---
name: git-apply-patch-cleanup
description: >-
  Domain-agnostic base primitive for applying a git patch file with
  verification, optional preview, optional source cleanup, and a patch
  coexistence preflight.
category: Git & Repository Management
---

# Git Apply Patch Cleanup (v1.1)

> **Skill ID:** `git-apply-patch-cleanup`<br>
> **Version:** 1.1.0<br>
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)<br>
> **Layer:** Base (per [skill-factory §2.0 Layering Decision](../../../../skill-factory/SKILL.md))

## Description

Domain-agnostic base primitive for applying a git patch file with
verification and optional source cleanup. This skill encapsulates the
workflow: validate patch → optionally preview → apply → optionally
dispose of the source, plus a coexistence preflight for a candidate
patch that must land on top of an already-applied pre-state patch.

## Composition Rationale

This skill is a **base skill** (domain-agnostic primitive). It owns ONLY the generic workflow:

1. Verify `git` available and inside a git repo
2. `git apply --check` to validate patch applies cleanly
3. Optional: `git apply --stat` / `--dry-run` for preview
4. `git apply` to actually apply
5. Optional: dispose of `<patch-file>` (system trash when available, deletion otherwise)
6. Optional: preflight whether a candidate patch coexists with a pre-state patch

Multiple composer skills can pipe their domain-specific patch discovery
into this base skill via its public CLI contract (`scripts/apply-patch`).
Inlining this primitive into each composer would split the SSOT and
silently diverge bug fixes.

**Known composers** (listed for bidirectional discoverability per
[skill-factory §5.2.1](../../../../skill-factory/SKILL.md)):

| Composer | Composition Mechanism |
| --- | --- |
| `acers-patch-import` (planned) | Shells out to `scripts/apply-patch <patch> --cleanup` after staging patch from ACERS staging bucket |
| `staging-patch-apply` (planned) | Composes this base after fetching patch from staging environment |

---

## Environment & Dependencies

**Required tools** (verified at runtime):

| Tool | Minimum Version | Verification Command |
| --- | --- | --- |
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
| --- | --- |
| `--cleanup` | Dispose of `<patch-file>` after successful apply (system trash when available, deletion otherwise) |
| `--dry-run` | Run `git apply --check` only; no working tree modification |
| `--stat` | Run `git apply --stat` and print summary; implies `--dry-run` |
| `--check-only` | Alias for `--dry-run` |
| `--verbose` | Print each `git` command before execution |
| `--help` | Show usage (from `scripts/apply-patch.usage.template`) |

### Exit Codes

| Code | Meaning |
| --- | --- |
| 0 | Success (applied, or dry-run/check passed) |
| 1 | Usage error / missing dependency / not in git repo |
| 2 | Patch file not found or unreadable |
| 3 | `git apply --check` failed (patch does not apply cleanly) |
| 4 | `git apply` failed during actual application |
| 5 | Cleanup failed (patch applied but disposal failed) |

### Step-by-Step Flow

1. **Parse arguments** — exactly one positional `<patch-file>` required
2. **Verify environment** — `git` in PATH, inside git repo (`git rev-parse --git-dir`)
3. **Validate patch file** — exists, readable, non-empty
4. **Check apply cleanliness** — `git apply --check <patch-file>` (exit 3 on failure)
5. **Dry-run / stat mode** — if `--stat` or `--dry-run`: `git apply --stat` and exit 0
6. **Apply patch** — `git apply <patch-file>` (exit 4 on failure)
7. **List applied files** — `git diff --name-only HEAD` printed to stdout
8. **Optional cleanup** — if `--cleanup`: `trash <patch-file>` when available, else `rm -f` (exit 5 on failure)

---

## Patch Coexistence Preflight

`scripts/apply-patch` answers "does this patch apply?" for a single patch.
`scripts/check-patch-coexistence.py` answers the layered question: **does
candidate patch B coexist with pre-state patch A already applied to
`--base-ref`?** It runs in an isolated worktree under `<repo>/scratch` and
emits a deterministic report.

```bash
python3 scripts/check-patch-coexistence.py \
  --repo <repo> \
  --base-ref <sha> \
  --pre-state-patch <pre.patch> \
  --candidate-patch <candidate.patch> \
  [--json]
```

| Argument | Description |
| -------- | ----------- |
| `--repo` | Repository root (default: current directory) |
| `--base-ref` | Commit both patches are layered on |
| `--pre-state-patch` | Patch A, applied first |
| `--candidate-patch` | Patch B, applied on top of A |
| `--json` | Emit JSON (default: text) |
| `--keep-worktree` | Keep the isolated worktree for inspection |

**Protocol:** apply A plain; apply B plain; if B fails, stage A (`git add
-A`) and retry B with `--3way`. The script then classifies every file
touched by B across four dimensions:

| Dimension | Meaning |
| --------- | ------- |
| `line` | Plain-apply result for the file (`clean`, `conflict`, `failed`). |
| `content` | Whether the file contains conflict markers after the three-way retry. |
| `knowledge` | Whether both patches touch the same document category (changelog, traceability, skill doc, code). |
| `structure` | Whether both patches touch the same file. |

**Exit codes:** `0` B coexists (plain or conflict-free three-way); `1` B
does not coexist (conflict markers or a hard failure); `2` usage, I/O, or
git error.

The script reports the dimensions; the consuming skill decides whether a
`knowledge` or `structure` overlap is acceptable. A `content` conflict is
never acceptable.

---

## Scripts

| Script | Tier | Purpose |
| --- | --- | --- |
| [`scripts/apply-patch`](scripts/apply-patch) | 2 (Bash) | Main executable implementing the single-patch CLI contract above |
| [`scripts/apply-patch.usage.template`](scripts/apply-patch.usage.template) | — | Usage template read at runtime by `apply-patch` |
| [`scripts/check-patch-coexistence.py`](scripts/check-patch-coexistence.py) | 1 (Python) | Layered patch-coexistence preflight with four-dimension classification |

**Language selection rationale:** `apply-patch` is Tier 2 (Bash) per
[Scripting Language Selection Rules §3.2](../../../../../../ai-agent-rules/scripting-language-selection-rules.md)
— the script body IS shell glue (100% native binary invocation: `git`,
`trash`, `rm`, `cat`). `check-patch-coexistence.py` is Tier 1 (Python
3.12+ stdlib) because it parses patches, drives a worktree lifecycle,
and emits structured JSON.

**Portable anchored paths:** `apply-patch` resolves its own directory via
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
# Expected: prints "file.txt", exits 0, patch file disposed

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
- [ ] **Registration Audit** — Row inserted alphabetically in `AGENTS-legacy.md` and the skill is listed in `skill-library-domain-grouping`
- [ ] **Script Smoke Test** — Run `apply-patch` and `check-patch-coexistence.py` (see above)

---

## Related Skills

- **Adjacent:** [`git-atomic-commit-construction`](../../../../git-atomic-commit-construction/SKILL.md),
  [`git-hunk-staging-primitives`](../../../../git-hunk-staging-primitives/SKILL.md),
  [`git-cross-ref-file-parity`](../../../../git-cross-ref-file-parity/SKILL.md)
- **Post-apply proof:** [`git-worktree-state-fingerprint`](../../audit/git-worktree-state-fingerprint/SKILL.md)
  — reconstruct the pre-state and prove the applied patch did not disturb it.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Traceability

See [TRACEABILITY.md](TRACEABILITY.md).
