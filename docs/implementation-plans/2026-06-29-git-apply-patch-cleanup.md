# [Create git-apply-patch-cleanup Base Skill] (v1)

## Rule Compliance Reference

- [/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md](/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md)
- [/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-rule-standardization-rules.md](/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-rule-standardization-rules.md) §2 (Skill-First Architecture, Layered Composition)
- [/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md](/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md) (Skill Generation Protocol)

---

## 1. Goal Description & Versioning

**Primary Goal**: Create a reusable, domain-agnostic base skill `git-apply-patch-cleanup` that encapsulates the workflow of applying a git patch file and optionally deleting the source patch — as demonstrated in our session where we applied `/Users/dk/lab-data/oleovista-acers/oleovista-acers-03-51-16.patch` to generate `session-ses_0f0e.md` and then deleted the patch file.

**Version**: v1 (initial)

---

## 2. Layering Decision

**Base Skill** (domain-agnostic primitive) — **MANDATORY** per [ai-rule-standardization-rules.md §2.2.1 Layered Composition Mandate](/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-rule-standardization-rules.md#221-layered-composition-mandate-base--composer).

*Rationale*: "Apply a patch file using `git apply` and optionally delete the source patch" is a generic Git operation reusable across any repo/domain. Multiple composer skills (e.g., `acers-patch-import`, `staging-patch-apply`) could compose this base.

---

## 3. Proposed Skill Structure

```
/Users/dk/lab-data/ai-suite/.agents/skills/git-apply-patch-cleanup/
├── SKILL.md                    # SSOT with YAML frontmatter, env deps, CLI contract, traceability
├── AGENTS.md                   # Companion bridge (no frontmatter, 5 required sections)
└── scripts/
    └── apply-patch.bash         # Tier-2 Bash: git apply + optional cleanup
```

---

## 4. Skill Specification

| Attribute | Value |
|-----------|-------|
| **Skill name** | `git-apply-patch-cleanup` |
| **Type** | Base skill (domain-agnostic primitive) |
| **Category** | Git-Operations |
| **Script tier** | Tier 2 (Bash) — body IS shell glue (`git apply` + `rm`) |
| **Script extension** | `.bash` (per [Bash Scripting Rules §Naming](/Users/dk/lab-data/ai-suite/ai-agent-rules/bash-scripting-rules.md)) |
| **CLI contract** | `apply-patch <patch-file> [--cleanup] [--dry-run] [--stat]` |

---

## 5. Operational Procedure (to encode in SKILL.md)

1. **Verify dependencies** — `git` available, in a git repo (`git rev-parse --git-dir`)
2. **Validate patch** — `git apply --check <patch-file>` (exit 0 = clean apply)
3. **Optional dry-run** — `git apply --stat <patch-file>` to preview changes
4. **Apply patch** — `git apply <patch-file>`
5. **Verify result** — `git status --short` shows expected changes
6. **Optional cleanup** — If `--cleanup` flag: `rm -f <patch-file>`
7. **Output** — Print applied files list (from `git apply --stat` or `git diff --name-only`)

---

## 6. Files to Create

| File | Purpose |
|------|---------|
| `/Users/dk/lab-data/ai-suite/.agents/skills/git-apply-patch-cleanup/SKILL.md` | SSOT with YAML frontmatter, env deps, CLI contract, traceability |
| `/Users/dk/lab-data/ai-suite/.agents/skills/git-apply-patch-cleanup/AGENTS.md` | Companion bridge (5 required sections per skill-factory §2.3.2) |
| `/Users/dk/lab-data/ai-suite/.agents/skills/git-apply-patch-cleanup/scripts/apply-patch` | Executable script (Tier-2, portable anchored paths) |

---

## 7. Verification Gates (per Skill Factory §3)

1. **Redaction & Portability Audit** — Run `redaction-portability` skill on all generated files
2. **Markdown Lint** — `markdownlint-cli2 --fix` then `markdownlint-cli2` on SKILL.md, AGENTS.md
3. **Cross-Reference Audit** — `skill-cross-reference-audit` script
4. **Invocation Audit** — `verify-doc-invocations.py` on SKILL.md
5. **Bridge Audit** — Confirm AGENTS.md has 5 sections, no frontmatter, 40–120 lines
6. **Registration Audit** — Row inserted alphabetically in root `AGENTS.md`
7. **Script Smoke Test** — Run script from repo root and `/tmp` with test patch

---

## 8. Change History

| Timestamp | Summary of Changes | Rationale |
| :--- | :--- | :--- |
| [2026-06-29 04:35] | Initial plan v1 | Document workflow from completed session as reusable base skill |

---

## 9. User Questions & Answers

| Question | Answer |
| :--- | :--- |
| Should this be in ai-suite or oleovista-acers? | Per [ai-rule-standardization-rules.md §2](/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-rule-standardization-rules.md#2-skill-first-architecture), base skills go in the general skill library (`ai-suite/.agents/skills/`) for maximum reusability. Composer skills for specific projects go in project `.agents/skills/`. |
| Why Tier-2 (Bash) not Tier-1 (Python)? | The script body IS shell glue (100% native binary invocation: `git apply`, `git rev-parse`, `rm`). Per [Scripting Language Selection Rules](/Users/dk/lab-data/ai-suite/ai-agent-rules/scripting-language-selection-rules.md) §3.2, Tier-2 is reserved for "scripts whose body IS shell glue (≤ 80% native-binary invocation in sequence)". |
| Should we also create a composer skill? | Not in this plan. Composer skills (e.g., `acers-patch-import`) can be created later when a project-specific need arises. This plan creates ONLY the base primitive. |