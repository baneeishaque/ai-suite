# [Skill-Factory Cross-Reference & Indent-Continuity Violations] (v1)

## Rule Compliance Reference

- [ai-agent-planning-rules.md](../../ai-agent-rules/ai-agent-planning-rules.md)
- [skill-factory SKILL.md](../../.agents/skills/skill-factory/SKILL.md) — §2.0 Layering Decision, §2.4 Registration, §3 Post-Drafting Checklist
- [skill-cross-reference-audit SKILL.md](../../.agents/skills/general/skill-cross-reference-audit/SKILL.md) — Composition/Related duplicate detection
- [list-indent-consistency SKILL.md](../../.agents/skills/general/list-indent-consistency/SKILL.md) — continuation-line indent drift detection
- [Markdown Generation Rules](../../ai-agent-rules/markdown-generation-rules.md)

---

## Violations Found

### V1: §2.0 Layering Decision — Exemplar Skills Don't Follow Convention (L37–48)

**Location**: `skill-factory/SKILL.md` L37–48

**Description**: The "Layerable" option (item 2) uses `vscode-search-exclude-glob` and `vscode-search-exclude-submodules` as the reference exemplar of the base/composer pattern. Neither skill has `## Composition by Higher-Level Skills` or `## Related Skills` sections.

**Analysis**: These skills predate the Composition/Related convention. The exemplar teaches readers to split into base+composer but doesn't demonstrate how to document the relationship. New skills following this exemplar verbatim would omit the required cross-references.

**Severity**: Medium (documentation accuracy)

**Root Fix**: Either (a) update the exemplar skills to include the correct Composition+Related sections, or (b) replace the exemplar with a pair that follows the convention (e.g., a freshly created demo pair).

---

### V2: §3 Portability Audit — Indent-Continuity Drift (L290–293)

**Location**: `skill-factory/SKILL.md` L290–293

**Description**: The `- **Portability, Redaction & PII Audit**` bullet's continuation lines use 2-space indent. The drift detector reports "expected 7 spaces, found 2 spaces" for L291–293.

**Analysis**: L290 has marker `- ` at column 0 with text starting at column 2. Continuation lines L291–293 should use 2-space indent to align with text — which they do. The drift detector's "expected 7" is a false positive: it incorrectly attributes these lines to the sub-list marker column (the numbered items at L294+) instead of the parent bullet marker column. Whether the detector has a bug or the indent style is genuinely mismatched needs investigation.

**Severity**: Low (visual alignment is correct; detector may be wrong)

**Root Fix**: Run `detect-list-indent-drift.py --fix` and verify the result. If the detector misattributes blocked continuations to a sibling list's marker column, the detector needs a bug fix.

---

### V3: §3 Composition Audit — Self-Contradictory Instructions (L351–368)

**Location**: `skill-factory/SKILL.md` L351–368

**Description**: Point 3 (L356–358) instructs the composer to link back to the base in **both** `## Composition Rationale` **and** `## Related Skills`. Point 4 (L359–365) immediately runs the `skill-cross-reference-audit`, which treats `## Composition Rationale` as a Composition section and flags any skill appearing in both Composition and Related as a duplicate violation (per `skill-cross-reference-audit/SKILL.md` L60–64). The instruction creates the very violation the audit detects.

**Analysis**: The audit's rule (L60–64 of the audit skill) counts `## Composition Rationale` as a Composition section alongside `## Composition by Higher-Level Skills` and `## Called Base Skills`. So when point 3 tells the composer to put the base in BOTH `## Composition Rationale` AND `## Related Skills`, the audit will flag it as "Duplicate In Composition And Related." This is a logical contradiction within the §3 checklist itself.

**Severity**: High (breaks the audit for any composer following instructions)

**Root Fix**: In `skill-factory/SKILL.md` L356–358, remove the instruction to add the base to the composer's `## Related Skills` section. The `## Composition Rationale` reference already establishes the bidirectional discoverability. Change:

```
    3. **Bidirectional Discoverability**: Confirm the base skill lists the new composer in its
       `## Composition by Higher-Level Skills` table, and the composer links back to the base in its
       `## Composition Rationale` and `## Related Skills` sections.
```

To:

```
    3. **Bidirectional Discoverability**: Confirm the base skill lists the new composer in its
       `## Composition by Higher-Level Skills` table, and the composer links back to the base in its
       `## Composition Rationale` section.
```

---

### V4: `skill-cross-reference-audit` Self-Violation — `skill-factory` in Both Sections (L21, L149)

**Location**: `skill-cross-reference-audit/SKILL.md` L21 (`## Composition Rationale`) and L149 (`## Related Skills`)

**Description**: The audit tool's own SKILL.md lists `skill-factory` in BOTH its `## Composition Rationale` (L21–23: "The skill-factory consumes in its Post-Drafting Checklist") AND its `## Related Skills` (L149–150: "skill-factory — consumer of this audit"). Running the audit on itself reports this as a "Duplicate In Composition And Related" violation.

**Analysis**: `skill-factory` is already listed in the Composition Rationale as a consumer — that's the correct home (stronger relationship). Adding it to Related Skills as well creates the duplication the audit is designed to detect.

**Severity**: High (the auditor violates its own rule; undermines credibility)

**Root Fix**: Remove `skill-factory` from `skill-cross-reference-audit/SKILL.md` `## Related Skills` section (L149–150). It is already correctly listed in `## Composition Rationale`.

---

### V5: `script-template-extraction` Self-Violation — `skill-factory` in Both Sections

**Location**: `script-template-extraction/SKILL.md` L14 (`## Composition Rationale`) and L151 (`## Related Skills`)

**Description**: Same pattern as V4 — `skill-factory` is listed in both the Composition Rationale (as delegator) and Related Skills (as defining mandate). The audit flags this as a duplicate.

**Analysis**: The Composition Rationale mention (L19, L25) already covers the relationship. Adding `skill-factory` to Related Skills is redundant.

**Severity**: Medium

**Root Fix**: Remove `skill-factory` from `script-template-extraction/SKILL.md` `## Related Skills` section.

---

## Additional Issues Detected by Audit

### 29 Skills Missing Related Sections With Composition

The `skill-cross-reference-audit` reports 29 skills that have a Composition section but are missing a `## Related Skills` section entirely. These include skills created/updated in recent sessions:

- `list-indent-consistency`
- `directory-tree-audit`
- `human-scanable-organization`
- `skill-library-domain-grouping`
- `git-commit-edit`
- and 24 others

**Root Fix**: Either (a) add a `## Related Skills` section to each, or (b) if the skill genuinely has no related skills, ensure the composition rationale is self-contained enough that the missing section is acceptable per the factory's audit rules.

---

## Proposed Changes

| # | File | Change |
|---|------|--------|
| 1 | `skill-factory/SKILL.md` L356–358 | Remove `and \`## Related Skills\`` from point 3 of Composition Audit |
| 2 | `skill-cross-reference-audit/SKILL.md` L149–150 | Remove `skill-factory` bullet from Related Skills |
| 3 | `script-template-extraction/SKILL.md` L151 | Remove `skill-factory` bullet from Related Skills |
| 4 | `skill-factory/SKILL.md` L290–293 (and surrounding §3 checklist) | Run `detect-list-indent-drift.py --fix` to repair indent continuity |
| 5 | 29 skills | Add `## Related Skills` sections where missing |

---

## Verification

After all changes:

```bash
python3 .agents/skills/general/skill-cross-reference-audit/scripts/audit-cross-refs.py
# Expected: 0 Duplicate In Composition And Related issues

python3 .agents/skills/general/list-indent-consistency/scripts/detect-list-indent-drift.py
# Expected: 0 drift (or confirmed false positives documented)
```

---

## Change History

| Timestamp | Summary of Changes | Rationale |
| :--- | :--- | :--- |
| 2026-06-20 | Initial plan (v1) | Document all violations found during skill-factory cross-reference audit |
