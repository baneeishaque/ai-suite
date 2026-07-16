# [Document AGENTS.md Recovery Workflow from OpenCode Session] (v1)

## Rule Compliance Reference

- [ai-agent-planning-rules.md](../../../ai-agent-rules/ai-agent-planning-rules.md)
- [ai-rule-standardization-rules.md](../../../ai-agent-rules/ai-rule-standardization-rules.md)
- [skill-factory/SKILL.md](../.agents/skills/skill-factory/SKILL.md)
- [scripting-language-selection-rules.md](../../../ai-agent-rules/scripting-language-selection-rules.md)
- [script-over-instruction-decomposition/SKILL.md](../.agents/skills/script-over-instruction-decomposition/SKILL.md)

---

## Starting Point

**Core Objective**: Document the workflow for recovering lost AGENTS.md content from opencode session exports after an accidental `git checkout HEAD -- AGENTS.md` operation, as reusable skills following the layered Base → Composer architecture.

---

## Deconstruction & Analysis

### What Happened (From Session `session-ses_0ef9-1.md`)

1. **Incident**: An agent executed `git -C /Users/dk/lab-data/ai-suite checkout HEAD -- AGENTS.md` (line 3384 in session)
2. **Loss**: 7 uncommitted skill rows were lost from AGENTS.md:
   - Browser Network Interception
   - Fnmatch Content Guard Pattern
   - macOS Shell Portability
   - macOS App Control
   - Markdown Lint Workflow
   - Teams Recording Download
   - Video Download from Manifest
3. **Recovery Source**: The session file contained the complete `git diff AGENTS.md` output (lines 2931-3000)
4. **Restoration Process**: Manual extraction of diff hunks → insertion at correct alphabetical positions → markdownlint fix

### Layering Decision (Skill Factory §2.0)

**Base Skill**: `opencode-session-diff-extractor`
- **Primitive**: Parse opencode session export (markdown format) → extract `git diff` output blocks → output unified diff format
- **Domain-agnostic**: Works on ANY session file, extracts ANY diff, not specific to AGENTS.md
- **CLI Contract**: `python3 scripts/extract-session-diff.py --session <file> [--file-pattern <path>]`

**Composer Skill**: `agents-md-recovery-from-session`
- **Domain-specific**: Uses base skill to extract AGENTS.md diff → applies diff to restore working tree → verifies alphabetical order → runs markdownlint
- **Composes**: `opencode-session-diff-extractor` + `git apply` + custom verification

---

## Implementation Plan

### Phase 1: Create Base Skill `opencode-session-diff-extractor`

| Step | Action | Verification |
|------|--------|--------------|
| 1.1 | Create `.agents/skills/opencode-session-diff-extractor/` directory | `ls` confirms |
| 1.2 | Write `SKILL.md` with YAML frontmatter, env deps, operational logic, SSOT links | `markdownlint-cli2 SKILL.md` = 0 errors |
| 1.3 | Write `scripts/extract-session-diff.py` (Tier-1 Python per scripting-language-selection-rules §3) | `python3 -m py_compile scripts/extract-session-diff.py` |
| 1.4 | Write `scripts/extract-session-diff.py.template` for diff output template (if needed) | Template renders correctly |
| 1.5 | Write per-skill `AGENTS.md` bridge (40-120 lines, 5 required sections) | Bridge audit passes |
| 1.6 | Register skill in root `AGENTS.md` via `agents-md-stage-row.py` | Row at correct alphabetical position |

### Phase 2: Create Composer Skill `agents-md-recovery-from-session`

| Step | Action | Verification |
|------|--------|--------------|
| 2.1 | Create `.agents/skills/agents-md-recovery-from-session/` directory | `ls` confirms |
| 2.2 | Write `SKILL.md` with composition rationale linking to base skill | `markdownlint-cli2 SKILL.md` = 0 errors |
| 2.3 | Write `scripts/recover-agents-md.py` (Tier-1 Python) | `python3 -m py_compile` |
| 2.4 | Script resolves base skill script via relative path (`../../opencode-session-diff-extractor/scripts/...`) | Import/execution works from any cwd |
| 2.5 | Write per-skill `AGENTS.md` bridge | Bridge audit passes |
| 2.6 | Register both skills in root `AGENTS.md` | Both rows at correct positions |

### Phase 3: Verification & Integration

| Step | Action | Verification |
|------|--------|--------------|
| 3.1 | Test base skill on `session-ses_0ef9-1.md` → extracts correct diff | Diff matches session lines 2941-3000 |
| 3.2 | Test composer skill end-to-end on a test AGENTS.md | Restores 7 skills in correct positions |
| 3.3 | Run markdownlint on all generated files | 0 errors |
| 3.4 | Run redaction-portability audit on all artifacts | Clean |

---

## Files to Create

| Path | Type | Description |
|------|------|-------------|
| `.agents/skills/opencode-session-diff-extractor/SKILL.md` | Skill SSOT | Base skill for extracting diffs from opencode sessions |
| `.agents/skills/opencode-session-diff-extractor/AGENTS.md` | Bridge | Per-skill companion bridge |
| `.agents/skills/opencode-session-diff-extractor/scripts/extract-session-diff.py` | Script | Tier-1 Python CLI for diff extraction |
| `.agents/skills/agents-md-recovery-from-session/SKILL.md` | Skill SSOT | Composer for AGENTS.md recovery |
| `.agents/skills/agents-md-recovery-from-session/AGENTS.md` | Bridge | Per-skill companion bridge |
| `.agents/skills/agents-md-recovery-from-session/scripts/recover-agents-md.py` | Script | Tier-1 Python CLI for recovery |

---

## Scripts Tier Declaration (Per Factory §2.2.1.1 #4)

| Script | Tier-1 (Python) Evaluation | Chosen Tier | Citation | Deviation Reason |
|--------|---------------------------|-------------|----------|------------------|
| `extract-session-diff.py` | Pure text parsing, regex, file I/O — ideal for Python | Tier-1 (Python) | §3.1 (default for new scripts) | None |
| `recover-agents-md.py` | JSON/parsing, git subprocess, file mutation — ideal for Python | Tier-1 (Python) | §3.1 (default for new scripts) | None |

---

## Change History

| Timestamp | Summary of Changes | Rationale |
|-----------|-------------------|-----------|
| [2026-06-29 13:45] | Initial plan v1 created | Document recovery workflow as layered skills per user request |

---

## User Questions & Answers

*None yet — awaiting your approval or clarifications.*