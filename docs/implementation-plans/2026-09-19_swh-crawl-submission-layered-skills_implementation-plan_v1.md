# SWH Crawl-Submission Automation — Layered Skill Architecture (v1)

## Rule Compliance Reference

- [ai-agent-planning-rules.md](../../ai-agent-rules/ai-agent-planning-rules.md)
- [ai-rule-standardization-rules.md](../../ai-agent-rules/ai-rule-standardization-rules.md) — Skill-First Architecture, Layered Composition Mandate, Script SSOT
- [skill-factory/SKILL.md](../../.agents/skills/skill-factory/SKILL.md) — §2.0 Layering Decision, §2.1 Directory Structure
- [skill-library-domain-grouping/SKILL.md](../../.agents/skills/general/skill-library-domain-grouping/SKILL.md) — Domain taxonomy placement
- [git-atomic-commit-construction-rules.md](../../ai-agent-rules/git-atomic-commit-construction-rules.md) — Atomic commit construction
- [scripting-language-selection-rules.md](../../ai-agent-rules/scripting-language-selection-rules.md) — Tier 1 Python for all scripts
- [redaction-portability-rules.md](../../ai-agent-rules/redaction-portability-rules.md) — No absolute paths, no org-private identifiers

---

## 1. Goal Description

Decompose the SWH (Software Heritage) crawl-submission automation into a **layered skill architecture** following the Skill-First mandate:
- **Base skills** (domain-agnostic primitives): `git-blob-hash`, `content-ingestion-check`
- **Composer skills** (SWH-specific workflows): `swh-save-code-now`, `swh-ingest-verify`, `swh-content-link-mint`
- CI workflow `.github/workflows/swh-verify.yml` orchestrating per-push verification

All scripts are Python 3.12+ (Tier 1), JXA for macOS Chrome automation, Bash for CI glue. No third-party dependencies.

---

## 2. Architecture Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOFTWARE-HERITAGE DOMAIN                      │
├──────────────────────────┬──────────────────────┬────────────────┤
│  swh-save-code-now       │  swh-ingest-verify   │ swh-content-   │
│  (JXA Chrome + origins)  │  (verify engine +    │ link-mint      │
│                          │   GH Action)         │ (mint links)   │
└──────────────┬───────────┴──────────┬───────────┴───────┬────────┘
               │                      │                   │
               ▼                      ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GENERAL-FILE BASE SKILLS                    │
├──────────────────────────────┬──────────────────────────────────┤
│  git-blob-hash               │  content-ingestion-check           │
│  (compute-blob-sha1.py)      │  (check-ingestion.py)              │
│  git hash-object equivalent  │  archive content-known check       │
└──────────────────────────────┴──────────────────────────────────┘
```

---

## 3. Files Created

### Base Skills (general/file/)

| Skill | Files |
|-------|-------|
| `git-blob-hash` | `SKILL.md`, `AGENTS.md`, `scripts/compute-blob-sha1.py`, `scripts/compute-blob-sha1.py.md` |
| `content-ingestion-check` | `SKILL.md`, `AGENTS.md`, `scripts/check-ingestion.py`, `scripts/check-ingestion.py.md` |

### Composer Skills (software-heritage/)

| Skill | Files |
|-------|-------|
| `swh-save-code-now` | `SKILL.md`, `AGENTS.md`, `scripts/swh-save.jxa`, `scripts/swh-save-inject.js`, `scripts/swh-save.jxa.md`, `origins.txt` |
| `swh-ingest-verify` | `SKILL.md`, `AGENTS.md`, `scripts/verify-ingest.py`, `scripts/verify-ingest.py.md`, `scripts/resolve-heads.bash`, `scripts/run-swh-verify.bash` |
| `swh-content-link-mint` | `SKILL.md`, `AGENTS.md`, `scripts/mint-content-links.py`, `scripts/mint-content-links.py.md` |

### CI Workflow

| File | Role |
|------|------|
| `.github/workflows/swh-verify.yml` | GitHub Actions workflow (triggers on push, calls skill scripts) |

---

## 4. Dependency Resolution (Portability Mandate)

All composer scripts resolve base scripts via paths anchored on **their own location**:

```python
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLOB_HASH_SCRIPT = os.path.join(SCRIPT_DIR, "../../../general/file/git-blob-hash/scripts/compute-blob-sha1.py")
INGEST_CHECK_SCRIPT = os.path.join(SCRIPT_DIR, "../../../general/file/content-ingestion-check/scripts/check-ingestion.py")
```

This satisfies the Layered Composition Mandate: pipelines work regardless of caller's `cwd`.

---

## 5. Verification Results

| Test | Result |
|------|--------|
| Python compile (all 5 scripts) | ✅ `python3 -m py_compile` |
| JXA compile (`swh-save.jxa`) | ✅ `osacompile -l JavaScript` |
| Bash syntax (CI wrappers) | ✅ `bash -n` |
| Minter reproduces procedure hashes | ✅ `53b4386b...` and `1c3aafd9...` byte-exact |
| `--lines` gate enforcement | ✅ exit 2 without `--verify`/`--force-lines` |
| Ingestion check UNKNOWN→exit 1 | ✅ consistent with live API (origin not archived) |
| Base-script resolution from diff cwd | ✅ tested from `/Users/dk/lab-data` |

---

## 6. Cross-Reference Audit

All internal references resolve to skills present in the worktree:
- `browser-network-interception` (pre-existing, tracked)
- `git-blob-hash`, `content-ingestion-check` (new base)
- `swh-save-code-now`, `swh-ingest-verify`, `swh-content-link-mint` (new composers)

External references to untracked skills (`macos-app-control`) removed.

---

## 7. Pending Registration (Follow-up)

The following registrations require edits to files **outside the worktree** (main tree):
1. **Root AGENTS.md Child DOX Index** — add `software-heritage/` domain entry (worktree branch has older AGENTS.md without Child DOX Index)
2. **skill-library-domain-grouping** — add `software-heritage/` to taxonomy (§1.1 tree, §1.2 listing). The SSOT file is untracked in main tree.

These will be handled at merge time with explicit permission.

---

## 8. Change History

| Timestamp | Summary of Changes | Rationale |
|-----------|-------------------|-----------|
| 2026-09-19 17:00 | Created base skills `git-blob-hash`, `content-ingestion-check` under `general/file/` | Layered Composition Mandate: extract domain-agnostic primitives |
| 2026-09-19 17:15 | Created composer skills `swh-save-code-now`, `swh-ingest-verify`, `swh-content-link-mint` under new `software-heritage/` domain | SWH-specific workflows as composers delegating to base skills |
| 2026-09-19 17:30 | Created CI workflow `.github/workflows/swh-verify.yml` + wrapper scripts in skill | Workflow-First Priority: CI stability before commit |
| 2026-09-19 17:45 | Fixed cross-references: replaced `macos-app-control` with tracked `browser-network-interception` | SSOT integrity: no references to untracked skills |
| 2026-09-19 18:00 | Verified all scripts compile and minter reproduces procedure hashes byte-exact | Fidelity Mandate: zero omission |

---

## 9. Proposed Atomic Commits (Preview)

### Batch 1 — Base Skills (no cross-deps)
1. `feat(scripts): add git-blob-hash base skill` — `general/file/git-blob-hash/`
2. `feat(scripts): add content-ingestion-check base skill` — `general/file/content-ingestion-check/`

### Batch 2 — SWH Composers + CI (depend on Batch 1)
3. `feat(scripts): add swh-save-code-now composer` — `software-heritage/save-code-now/`
4. `feat(scripts): add swh-ingest-verify composer` — `software-heritage/ingest-verify/`
5. `feat(scripts): add swh-content-link-mint composer` — `software-heritage/content-link-mint/`

### Batch 3 — CI Integration (depends on Batch 2)
6. `test(workflow): add SWH ingest verification GitHub Actions` — `.github/workflows/swh-verify.yml`

---

## 10. Authorization Required

Per git-atomic-commit-construction §2g (batch-by-batch), I await your "start batch 1" before committing any changes. The worktree is currently clean with all files staged as untracked additions.