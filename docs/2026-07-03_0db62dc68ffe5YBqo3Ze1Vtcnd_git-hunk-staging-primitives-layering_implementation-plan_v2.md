# Git Hunk Staging Primitives Layering (v2)

## Rule Compliance Reference
- [AI Agent Planning Rules](../../../ai-agent-rules/ai-agent-planning-rules.md)
- [AI Rule Standardization Rules](../../../ai-agent-rules/ai-rule-standardization-rules.md)
- [Skill Factory SKILL.md](../../../.agents/skills/skill-factory/SKILL.md)

---

## 1. Goal Description

Extract generic Git hunk-staging primitives from `git-atomic-commit-construction` into a dedicated **base skill** (`git-hunk-staging-primitives`), then update `git-atomic-commit-construction` to act as a **composer** that invokes the base skill. This satisfies the Layered Composition Mandate (base → composer) for maximum reusability.

---

## 2. Current State (After Recheck)

**Scripts in `git-atomic-commit-construction/scripts/` (4 scripts):**
| Script | Purpose | Documented In |
|---|---|---|
| `stage-hunk-from-diff.py` | Stage hunks matching pattern from diff | §3i, §2f.1 |
| `stage-file-excluding-lines.py` | Stage file minus matching lines (working tree) | §2f.1, §3i.1 |
| `stage-head-synthesize.py` | Stage HEAD with mechanical substitutions | §13 (HEAD-Synthesis) |
| `agents-md-stage-row.py` | Stage single AGENTS.md row | §2f, skill-factory |

**Ad-hoc script created in session (not yet committed):** `stage_specific_hunks.py` — stage specific hunk indices from a file's diff against HEAD.

**Workflows in `git-atomic-commit-construction/SKILL.md`:**
- §2f.1: Deferred Cross-Reference Hunk Pattern
- §3i: Selective Hunk Extraction via Diff Patching
- §3i.1: Adjacent-Lines Isolation (our session's work)
- §13: Intermediate State Synthesis — now has **4-primitive table** (including `stage-head-synthesize.py`)

**Root `AGENTS.md`:** Updated with many new skills (alphabetically sorted).

**Existing related skills in `/Users/dk/lab-data/ai-suite/.agents/skills/`:**
- `git-atomic-commit-construction` (our composer target)
- `git-history-refinement` (uses commit construction)
- `git-pre-execution-safety-stash` (uses staging)
- Many other git-* skills

**Rules in `/Users/dk/lab-data/ai-suite/ai-agent-rules/`:**
- `git-atomic-commit-construction-rules.md`
- `git-commit-message-rules.md`
- `git-operation-rules.md`
- `git-history-refinement-rules.md`
- `git-rebase-standardization-rules.md`

---

## 3. Layering Decision (Reaffirmed)

**Test:** *"Could a different domain ever need the same primitive?"*

**Answer: YES** — All 5 primitives are generic Git operations reusable by ANY skill doing commit construction, history refinement, patch manipulation, or submodule sync.

**Mandatory Split:**
1. **Base Skill:** `git-hunk-staging-primitives` — owns ONLY the 5 generic primitives (scripts + minimal prose)
2. **Composer Skill:** `git-atomic-commit-construction` — domain-specific workflows invoking the base skill

---

## 4. Proposed Changes

### 4.1 Create Base Skill: `git-hunk-staging-primitives`

**Location:** `.agents/skills/git-hunk-staging-primitives/`

**Directory Structure:**
```
git-hunk-staging-primitives/
├── SKILL.md          # Active SSOT (YAML frontmatter + prose)
├── AGENTS.md         # Companion bridge (no frontmatter)
└── scripts/
    ├── agents-md-stage-row.py
    ├── stage-file-excluding-lines.py
    ├── stage-head-synthesize.py
    ├── stage-hunk-from-diff.py
    └── stage-specific-hunks.py    # NEW: promote our ad-hoc script
```

**SKILL.md Contents:**
- YAML frontmatter: `name: git-hunk-staging-primitives`, `description: "Generic Git hunk-staging primitives for commit construction and history refinement"`, `category: Git & Repository Management`
- Environment & Dependencies: Python 3.12+, Git 2.x
- Operational Logic: Each script documented with invocation examples, flag reference, edge cases
- SSOT Compliance: Links to `git-atomic-commit-construction-rules.md` and `git-operation-rules.md`
- **No domain logic** — no commit-preview formatting, no "adjacent-lines fallback" workflow

**Scripts:** All five scripts shipped as deterministic Tier-A primitives per `script-over-instruction-decomposition`.

---

### 4.2 Update `git-atomic-commit-construction` as Composer

**Changes:**
1. **Remove** `scripts/` folder entirely (delegates to base skill)
2. **Update** invocation paths in prose to use base skill:
   - §2f.1: `$(dirname "$0")/../../git-hunk-staging-primitives/scripts/stage-file-excluding-lines.py`
   - §3i: `$(dirname "$0")/../../git-hunk-staging-primitives/scripts/stage-hunk-from-diff.py`
   - §3i.1: Same as §2f.1
   - §2f: `$(dirname "$0")/../../git-hunk-staging-primitives/scripts/agents-md-stage-row.py`
   - §13: `$(dirname "$0")/../../git-hunk-staging-primitives/scripts/stage-head-synthesize.py`
3. **Add** Composition Rationale section (per skill-factory §2.2.2):
   > This skill is a composer: it does NOT re-implement hunk-staging primitives. It orchestrates `git-hunk-staging-primitives` via its public CLI contract.
4. **Update** Related Skills table: link to `git-hunk-staging-primitives`
5. **Add** base skill to "Composition by Higher-Level Skills" table in base skill

---

### 4.3 Enrichments Already Done (Session)

The following are ALREADY in `git-atomic-commit-construction/SKILL.md`:
- §3i.1: Adjacent-Lines Isolation (git add -p Split Failure Fallback)
- §13 enrichment: Scripted Fallback (includes `stage-head-synthesize.py` as preferred for HEAD-based transforms)
- Common Pitfalls row: "`git add -p` split rejected on adjacent added/deleted lines"
- 4-primitive table in §13

**No further composer-side action needed** — these remain as domain-specific workflows.

---

### 4.4 Register Base Skill

**Root `AGENTS.md` skills table:**
- Insert `git-hunk-staging-primitives` row at alphabetical position (after `git-history-refinement`, before `git-operation-blocking-hooks`)
- Use base skill's own `agents-md-stage-row.py` with `--mode worktree` for registration

---

## 5. Step-by-Step Execution Plan

| Step | Action | Commit Type | Files |
|---|---|---|---|
| 1 | Create `git-hunk-staging-primitives/` dir, copy 4 scripts + add `stage-specific-hunks.py`, write SKILL.md + AGENTS.md | `feat` | New skill dir + 5 scripts |
| 2 | Remove `scripts/` from `git-atomic-commit-construction`, update invocation paths, add Composition Rationale | `refactor` | `git-atomic-commit-construction/SKILL.md` |
| 3 | Update base skill's "Composition by Higher-Level Skills" table | `docs` | `git-hunk-staging-primitives/SKILL.md` |
| 4 | Register base skill in root AGENTS.md | `chore` | `AGENTS.md` |

**Each step = one atomic commit** (maximum atomicity mandate).

---

## 6. Verification Gates

- [ ] Base skill scripts run end-to-end on fresh checkout (idempotent, deterministic)
- [ ] Composer skill invocations use correct relative paths (`$(dirname "$0")/../../git-hunk-staging-primitives/scripts/...`)
- [ ] Both skills pass markdownlint-cli2
- [ ] Root AGENTS.md alphabetical order maintained
- [ ] Cross-reference audit passes (`skill-cross-reference-audit`)

---

## 7. Change History

| Timestamp | Summary | Rationale |
|---|---|---|
| 2026-07-03 04:30 | v1 created | Initial plan per layering mandate |
| 2026-07-03 04:45 | v2 after recheck | Another session added `stage-head-synthesize.py`; ad-hoc `stage_specific_hunks.py` must be promoted; 5 primitives total |

---

## 8. User Questions & Answers

*None yet.*