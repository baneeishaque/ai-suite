# [Merge Split Text Files with Overlap Deduplication] (v1)

## Rule Compliance Reference
- [AI Agent Planning Rules](../../../ai-suite/ai-agent-rules/ai-agent-planning-rules.md)
- [AI Rule Standardization Rules](../../../ai-suite/ai-agent-rules/ai-rule-standardization-rules.md)
- [Skill Factory Skill](../../../ai-suite/.agents/skills/skill-factory/SKILL.md)
- [Scripting Language Selection Rules](../../../ai-suite/ai-agent-rules/scripting-language-selection-rules.md)
- [Markdown Generation Rules](../../../ai-suite/ai-agent-rules/markdown-generation-rules.md)

---

## Goal
Create a reusable skill ecosystem for merging split text files (specifically opencode session exports) that have overlapping/duplicated content, producing a single deduplicated output file.

---

## Starting Point
User has two opencode session export files:
- `session-ses_0f0e-1.md` (13,433 lines)
- `session-ses_0f0e-2.md` (14,663 lines)

File 2 contains the first ~274 lines duplicated from the end of file 1. The task completed successfully by manually identifying the overlap boundary (the second "## Assistant (Build · MiMo V2.5 Free · 27.4s)" section in file 2) and concatenating file 1 + unique tail of file 2.

---

## Plan

### Step 1: Create Base Skill — `text-file-merge-overlap-dedup`
**Type**: Base skill (domain-agnostic primitive)
**Location**: `/Users/dk/lab-data/ai-suite/.agents/skills/text-file-merge-overlap-dedup/`

**Deliverables**:
- `SKILL.md` — operational protocol with YAML frontmatter
- `AGENTS.md` — companion bridge
- `scripts/merge_overlap.py` — Python 3.12+ script (Tier 1 per scripting rules)
  - Accepts: `--file1`, `--file2`, `--output`, `--min-overlap-lines` (default: 10)
  - Algorithm: Find longest common substring (LCS) at boundary of file1 end / file2 start using sliding window with rolling hash for efficiency
  - Handles: UTF-8, CRLF/LF normalization, large files (streaming)
  - Emits: deduplicated merged file, overlap report (start line in file1, start line in file2, line count)
- `scripts/verify_merge.py` — verification script that confirms byte-for-byte reproducibility of original files from merge + overlap metadata

### Step 2: Create Composer Skill — `opencode-session-merge`
**Type**: Composer skill (domain-specific)
**Location**: `/Users/dk/lab-data/oleovista-acers/.agents/skills/opencode-session-merge/`

**Deliverables**:
- `SKILL.md` — operational protocol
- `AGENTS.md` — companion bridge
- `scripts/merge_opencode_session.py` — Python 3.12+ script
  - Accepts: `--session-id`, `--part1`, `--part2`, `--output-dir`
  - Delegates to base skill via relative path: `../../../../ai-suite/.agents/skills/text-file-merge-overlap-dedup/scripts/merge_overlap.py`
  - Adds opencode-specific intelligence:
    - Recognizes opencode session header format (`# Opencode ...`, `**Session ID:**`, `**Created:**`)
    - Can auto-detect overlap by scanning for duplicate session headers
    - Emits merged file as `session-<id>-merged.md`
  - Verifies using base skill's verification script

### Step 3: Register Skills
- Update root `AGENTS.md` in both repositories:
  - `/Users/dk/lab-data/ai-suite/AGENTS.md` — register base skill
  - `/Users/dk/lab-data/oleovista-acers/AGENTS.md` — register composer skill

### Step 4: Verification
- Run `markdownlint-cli2 --fix` on all new markdown files
- Execute test merge with the original session files
- Verify round-trip: original file 1 + unique tail of file 2 = merged output

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `/Users/dk/lab-data/ai-suite/.agents/skills/text-file-merge-overlap-dedup/SKILL.md` | Create |
| `/Users/dk/lab-data/ai-suite/.agents/skills/text-file-merge-overlap-dedup/AGENTS.md` | Create |
| `/Users/dk/lab-data/ai-suite/.agents/skills/text-file-merge-overlap-dedup/scripts/merge_overlap.py` | Create |
| `/Users/dk/lab-data/ai-suite/.agents/skills/text-file-merge-overlap-dedup/scripts/verify_merge.py` | Create |
| `/Users/dk/lab-data/oleovista-acers/.agents/skills/opencode-session-merge/SKILL.md` | Create |
| `/Users/dk/lab-data/oleovista-acers/.agents/skills/opencode-session-merge/AGENTS.md` | Create |
| `/Users/dk/lab-data/oleovista-acers/.agents/skills/opencode-session-merge/scripts/merge_opencode_session.py` | Create |
| `/Users/dk/lab-data/ai-suite/AGENTS.md` | Modify (add base skill row) |
| `/Users/dk/lab-data/oleovista-acers/AGENTS.md` | Modify (add composer skill row) |

---

## Commands to Execute

```bash
# Build and test base skill
cd /Users/dk/lab-data/ai-suite/.agents/skills/text-file-merge-overlap-dedup
python3 scripts/merge_overlap.py \
  --file1 /Users/dk/lab-data/oleovista-acers/session-ses_0f0e-merged.md \
  --file2 /Users/dk/lab-data/oleovista-acers/session-ses_0f0e-merged.md \
  --output /tmp/test_merge.md \
  --min-overlap-lines 10

# Test composer skill
cd /Users/dk/lab-data/oleovista-acers/.agents/skills/opencode-session-merge
python3 scripts/merge_opencode_session.py \
  --session-id ses_0f0e4ae04ffe3gUzLmI23GTlBD \
  --part1 /Users/dk/lab-data/oleovista-acers/session-ses_0f0e-1.md \
  --part2 /Users/dk/lab-data/oleovista-acers/session-ses_0f0e-2.md \
  --output-dir /Users/dk/lab-data/oleovista-acers

# Verify markdown lint
markdownlint-cli2 --fix /Users/dk/lab-data/ai-suite/.agents/skills/text-file-merge-overlap-dedup/SKILL.md
markdownlint-cli2 --fix /Users/dk/lab-data/ai-suite/.agents/skills/text-file-merge-overlap-dedup/AGENTS.md
markdownlint-cli2 --fix /Users/dk/lab-data/oleovista-acers/.agents/skills/opencode-session-merge/SKILL.md
markdownlint-cli2 --fix /Users/dk/lab-data/oleovista-acers/.agents/skills/opencode-session-merge/AGENTS.md
```

---

## Verification Gates
1. Base skill script exits 0 on success, 1 with diagnostic on failure
2. Merged output matches manually-created `session-ses_0f0e-merged.md` (diff -q)
3. Verification script confirms round-trip integrity
4. Markdown lint passes with zero violations
5. Both AGENTS.md bridges pass bridge audit (5 required sections, no frontmatter, 40-120 lines)

---

## Change History

| Timestamp | Summary of Changes | Rationale |
|-----------|-------------------|-----------|
| [2026-06-29 04:30] | Initial plan v1 created | Document the two-skill layered approach for merge with overlap deduplication |

---

## User Questions & Answers

**Q: Why two skills instead of one?**
A: The overlap detection algorithm is a generic primitive (could apply to log files, SQL dumps, any split text files). The Skill Factory §2.0 layering test applies: "Could a different domain ever need the same primitive?" → Yes. Therefore layering is MANDATORY.

**Q: Why Python (Tier 1) not PowerShell?**
A: Per Scripting Language Selection Rules §3-§5, Python 3.12+ is default for text processing, JSON, data munging. Rolling hash / LCS algorithm is algorithmic work, not shell glue.

**Q: What overlap detection algorithm?**
A: Sliding window with rolling hash (Rabin-Karp style) on last N lines of file1 vs first N lines of file2. Finds longest common contiguous line sequence. O(n) expected time, handles large files.

**Q: Where do scripts live?**
A: Base skill scripts in ai-suite (shared repo). Composer script in oleovista-acers (project repo). Composer resolves base via relative path from its own location.