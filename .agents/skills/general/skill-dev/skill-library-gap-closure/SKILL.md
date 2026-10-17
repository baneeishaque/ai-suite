---
name: skill-library-gap-closure
description: Closes skill-library documentation gaps discovered from real session evidence —
  ingests a workflow-analysis report, emits a ranked per-gap register with evidence and a
  new-skill-versus-enrichment verdict, then routes each gap into skill-factory for
  implementation under a plan-first approval gate.
category: Skill-Authoring
---

# Skill Library Gap Closure (v1)

> **Skill ID:** `skill-library-gap-closure`<br>
> **Version:** 1.0.0<br>
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)<br>
> **Layer:** Composer (per [skill-factory §2.0 Layering Decision](../../../skill-factory/SKILL.md))

## Description

Owns the end-to-end workflow of turning **evidence of undocumented practice** into
closed documentation gaps:

1. **Ingest** a session workflow-analysis report (or any narrative evidence of procedures
   that were executed ad hoc).
2. **Extract** one row per candidate gap, each carrying its source evidence.
3. **Verify** each gap against the library — the decisive step that separates a real gap
   from a procedure already documented elsewhere.
4. **Verdict** per gap: enrich an existing owner, or create a new skill.
5. **Plan** the closure, gated on explicit approval.
6. **Route** each gap into [`skill-factory`](../../../skill-factory/SKILL.md) §6 (enrich)
   or §2 (create), then audit.

This skill owns NO authoring mechanics — it decides *what* to change and *where*, then
delegates *how*.

## Composition Rationale

This skill is a **composer** over existing skills. It re-implements nothing:

1. [`opencode-session-problem-solution-workflow-analysis`](../../../opencode/opencode-session-problem-solution-workflow-analysis/SKILL.md)
   — produces the evidence report this skill consumes.
2. [`skill-factory`](../../../skill-factory/SKILL.md) — §5.5 supplies the new-vs-enrich
   placement test; §6 owns single-skill enrichment; §2 owns new-skill creation.
3. [`skill-library-domain-grouping`](../../skill-library-domain-grouping/SKILL.md) — owns
   taxonomy placement and the ≤10 item-per-folder cap that decides where a new skill lands.
4. [`skill-cross-reference-audit`](../../skill-cross-reference-audit/SKILL.md) — the
   structural audit that runs after each closure batch.
5. [`deterministic-artifact-in-place-amendment`](../../planning/deterministic-artifact-in-place-amendment/SKILL.md)
   — decides whether an existing skill doc can be amended in place rather than regenerated.
6. [`planning-artifact-lifecycle`](../../planning/planning-artifact-lifecycle/SKILL.md) —
   owns the plan-first approval gate this skill defers to.

Inlining any of the above is FORBIDDEN. In particular, the new-vs-enrich test must NOT be
re-derived here with an ad-hoc search; §2.2 mandates the skill-factory method.

## 1. Environment & Dependencies

| Requirement | Minimum | Verification |
| :--- | :--- | :--- |
| Python | 3.9+ (for the gap-register script and composed bases) | `python3 --version` |
| PyYAML / ruamel.yaml | any | required by the session-analysis bases |
| `markdownlint-cli2` | any | `markdownlint-cli2 <path>` — gate before presenting any artifact |
| git | any modern version | `git --version` |

## 2. Operational Logic

### 2.1 Evidence intake

Accept an evidence source: a workflow-analysis report, a walkthrough, or a user narrative
describing procedures that were worked out by hand. Record, per candidate gap, the
*source evidence* — the turn ordinal, log path, or quoted user instruction that shows the
procedure was actually needed.

A gap with no evidence is a hunch. Hunches go into the plan as optional, never as
committed scope.

### 2.2 Verification — the decisive step

For each candidate gap, decide whether the library ALREADY documents it. Use
[`skill-factory`](../../../skill-factory/SKILL.md) §5.5: search the library on a 2–3 word
topic phrase, then read the owning skill's `## Description` and `## Composition
Rationale` to confirm it is genuinely in scope.

Record the verdict as one of:

| Verdict | Meaning |
| :--- | :--- |
| `DOCUMENTED` | An existing skill owns it. No change; record the owner to prevent re-audit. |
| `PARTIAL` | An owner exists but a specific sub-procedure is missing. Enrichment. |
| `NOT_DOCUMENTED` | No owner. Candidate for a new skill or a new section. |

**Negative evidence must be verified, not assumed.** When concluding `NOT_DOCUMENTED`, run
a library-wide search for the distinguishing token of the procedure and record that the
search returned zero hits. A verdict backed by "I did not see it" is not a verdict.

**Record the not-gaps.** Every candidate gap that verifies as `DOCUMENTED` belongs in the
register. Without that section the next closure pass re-audits the same ground.

**Re-audit is an acceptable fallback cost.** The register is a LOCAL-ONLY artifact: session
logs and planning documents under `docs/` can contain sensitive information and must never
be published without deliberate review, so the register is not committed. When a later
closure pass finds no surviving register, re-running the audit is the correct action —
it costs time, not correctness. Do not treat a missing register as a reason to skip §2.2.

**Durability boundary.** What is committed is capability-facing metadata only: the public
`CHANGELOG.md` and `TRACEABILITY.md` companions per skill. Historical analysis — evidence
quotes, per-gap identifiers, hunk anchors, insertion-point tables — stays local. Keep those
companions short; they describe what a skill does, not the history of how it was decided.

### 2.3 New-skill-versus-enrichment verdict

Apply [`skill-factory`](../../../skill-factory/SKILL.md) §5.5 to each `PARTIAL` /
`NOT_DOCUMENTED` row:

- An owner exists and the gap is inside its declared scope → **enrich** that skill.
- No owner, but the capability is a reusable generic primitive → **new base skill** first,
  then a composer over it (§2.0 layering test: "could a different domain need this?").
- No owner, and the capability is an ordered domain workflow → **new composer skill**.

Prefer enriching over creating: a new skill for a one-off adds surface area and splits the
SSOT.

### 2.4 Scope the audit to the WHOLE evidence set

Derive the candidate list from **every** workflow in the evidence, not only the one that
prompted the question. A closure pass that audits one turn and declares the rest clean is
the single most common failure mode of this workflow: the gaps it misses are invisible
because they were never looked for.

### 2.5 Plan-first gate

Emit the ranked gap register and a versioned plan under `docs/` using
[`planning-artifact-lifecycle`](../../planning/planning-artifact-lifecycle/SKILL.md) and
[`planning-artifact-naming`](../../planning/planning-artifact-naming/SKILL.md), then
**stop** and present for approval. No skill folder, script, or registry row is created
before explicit approval.

The plan MUST surface a per-script tier declaration for every proposed new script, per
[`skill-factory`](../../../skill-factory/SKILL.md) §2.2.1.1 item 4.

### 2.6 Routing and closure

For each approved row, route to skill-factory §6 (enrich) or §2 (create). Then:

- Register each new skill in [`skill-library-domain-grouping`](../../skill-library-domain-grouping/SKILL.md)
  BEFORE its `AGENTS-legacy.md` row, so the index never advertises an unregistered skill.
- Run [`skill-cross-reference-audit`](../../skill-cross-reference-audit/SKILL.md) after the
  batch and require zero new issues.
- Lint every touched markdown with `markdownlint-cli2` and require a clean gate.

## 3. Scripts

This skill ships no executable script of its own: every deterministic step it owns is
already a script in a composed skill, and the Tier Decomposition Mandate requires reusing
those rather than re-implementing them. The composed CLIs are:

| Step | Script owner |
| :--- | :--- |
| Evidence report | `opencode-session-problem-solution-workflow-analysis/scripts/reconstruct-workflow.py` |
| Structural audit | `skill-cross-reference-audit/scripts/audit-cross-refs.py` |
| Taxonomy placement | `skill-library-domain-grouping` §1.2 (tree notation, no script) |
| Amend-vs-regenerate | `deterministic-artifact-in-place-amendment/scripts/detect-regeneration-need.py` |

Per [`skill-factory`](../../../skill-factory/SKILL.md) §2.1, a skill with no scripts MUST
NOT have a `scripts/` directory.

## 4. Guardrails

- No skill folder, script, or registry row is created before explicit plan approval.
- Every `NOT_DOCUMENTED` verdict MUST cite a zero-hit library-wide search.
- Every candidate gap from the evidence set MUST appear in the register, including
  `DOCUMENTED` ones.
- Committed artifacts MUST NOT carry session identifiers or references to gitignored
  `docs/` planning files — see [`redaction-portability`](../../../redaction-portability/SKILL.md).
- A parallel `ai-agent-rules/*.md` file MUST NOT be authored for any gap closed here.

## 5. Composition by Higher-Level Skills

| Composer | Composition Mechanism |
| :--- | :--- |
| `(none yet)` | — |

## Related Skills

Skills this composer SEQUENCES are claimed in `## Composition Rationale`, not repeated
here: per §5.2.1 a name belongs in exactly one of Composition or Related. This section
therefore lists only the looser sibling association.

- [`rule-to-skill-industrialization`](../../../rule-to-skill-industrialization/SKILL.md) —
  the sibling for a RULE-file input, where a redundant rule is decomposed and its source
  decommissioned. This skill is the sibling for SESSION-EVIDENCE input, where nothing is
  decommissioned and only gaps are closed. The two differ on that point, so a reader
  choosing between them should check which input they actually have.

## 6. Traceability

See [TRACEABILITY.md](TRACEABILITY.md).

## 7. Changelog

See [CHANGELOG.md](CHANGELOG.md).
