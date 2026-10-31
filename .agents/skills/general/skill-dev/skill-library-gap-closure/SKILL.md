---
name: skill-library-gap-closure
description: Closes skill-library documentation gaps discovered from real session evidence —
  automatically acquires or ingests the session transcripts, full-fidelity JSONL, workflow
  report, and path-attribution evidence, then emits a ranked per-gap register with evidence
  and a new-skill-versus-enrichment verdict, and routes each gap into skill-factory for
  implementation under a plan-first approval gate.
category: Skill-Authoring
---

# Skill Library Gap Closure (v1.4)

> **Skill ID:** `skill-library-gap-closure`<br>
> **Version:** 1.4.0<br>
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)<br>
> **Layer:** Composer (per [skill-factory §2.0 Layering Decision](../../../skill-factory/SKILL.md))

## Description

Owns the end-to-end workflow of turning **evidence of undocumented practice** into
closed documentation gaps:

1. **Acquire** session evidence — generate the session transcript files, a full-fidelity
   machine JSONL, a workflow-analysis report skeleton, and an absolute-path manifest
   from the session under audit, without a separate user prompt.
2. **Ingest** the workflow-analysis report (or any narrative evidence of procedures
   that were executed ad hoc).
3. **Extract** one row per candidate gap, each carrying its source evidence.
4. **Verify** each gap against the library — the decisive step that separates a real gap
   from a procedure already documented elsewhere.
5. **Verdict** per gap: enrich an existing owner, or create a new skill.
6. **Map** each cited path token to the session, turn, tool call, and call index that
   touched it, producing an evidence index for verification.
7. **Plan** the closure, gated on explicit approval.
8. **Route** each gap into [`skill-factory`](../../../skill-factory/SKILL.md) §6 (enrich)
   or §2 (create), then audit.

This skill owns NO authoring mechanics — it decides *what* to change and *where*, then
delegates *how*.

## Composition Rationale

This skill is a **composer** over existing skills. It re-implements nothing.
When `--verify-text` is supplied, the driver first composes
[`opencode-current-session-id`](../../../opencode/opencode-current-session-id/SKILL.md):
it runs `find-current-session.py --verify-text` before the bundle and fails
closed on no match or ambiguity.

1. [`opencode-session-analysis-bundle`](../../../opencode/session/opencode-session-analysis-bundle/SKILL.md)
   — invoked FIRST through this skill's `scripts/run-gap-closure-evidence.py`. The driver
   runs its `scripts/run-session-analysis-bundle.py --session-id <id> --repo <repo>
   --purpose skill-library-gap-closure-evidence`; the bundle produces the session's
   `transcripts/*-transcript.yaml` human transcripts, the full-fidelity JSONL, the
   report skeleton, and the JSON manifest this skill consumes.
2. [`opencode-session-path-attribution`](../../../opencode/opencode-session-path-attribution/SKILL.md)
   — invoked once candidate gaps and their cited path tokens exist, through the same
   driver's `--attribution-only` mode. The driver runs its
   `scripts/attribute-path-to-session.py --session <id> --path <token> --json --output
   <evidence-dir>/path-attribution/<slug>.json`; the records populate the Evidence
   Verification Index.
3. [`opencode-session-problem-solution-workflow-analysis`](../../../opencode/opencode-session-problem-solution-workflow-analysis/SKILL.md)
   — owns the report's problem/solution/workflow structure. The bundle generates the
   skeleton; this skill fills the judgement sections per that skill's §2.1 steps 4–7.
4. [`skill-factory`](../../../skill-factory/SKILL.md) — §5.5 supplies the new-vs-enrich
   placement test; §6 owns single-skill enrichment; §2 owns new-skill creation.
5. [`skill-library-domain-grouping`](../../skill-library-domain-grouping/SKILL.md) — owns
   taxonomy placement and the ≤10 item-per-folder cap that decides where a new skill lands.
6. [`skill-cross-reference-audit`](../../skill-cross-reference-audit/SKILL.md) — the
   structural audit that runs after each closure batch.
7. [`deterministic-artifact-in-place-amendment`](../../planning/deterministic-artifact-in-place-amendment/SKILL.md)
   — decides whether an existing skill doc can be amended in place rather than regenerated.
8. [`planning-artifact-lifecycle`](../../planning/planning-artifact-lifecycle/SKILL.md) —
   owns the plan-first approval gate this skill defers to.

Inlining any of the above is FORBIDDEN. In particular, the new-vs-enrich test must NOT be
re-derived here with an ad-hoc search; §2.3 mandates the skill-factory method.

## 1. Environment & Dependencies

| Requirement | Minimum | Verification |
| :--- | :--- | :--- |
| Python | 3.10+ (path attribution uses PEP 604 unions; verified on 3.12; driver is stdlib-only) | `python3 --version` |
| PyYAML / ruamel.yaml | any | required by the session-analysis bases |
| `opencode-session-analysis-bundle` | present | `test -f .agents/skills/opencode/session/opencode-session-analysis-bundle/scripts/run-session-analysis-bundle.py` |
| `opencode-session-path-attribution` | present | `test -f .agents/skills/opencode/opencode-session-path-attribution/scripts/attribute-path-to-session.py` |
| `opencode-current-session-id` | present | `test -f .agents/skills/opencode/opencode-current-session-id/scripts/find-current-session.py` |
| `scratch-artifact-naming` | present | `test -f .agents/skills/general/file/scratch-artifact-naming/scripts/resolve-scratch-path.py` |
| `markdownlint-cli2` | any | `markdownlint-cli2 <path>` — gate before presenting any artifact |
| git | any modern version | `git --version` |

## 2. Operational Logic

### 2.1 Evidence acquisition

When the evidence source is a session (a session ID, or a report whose transcript set is
absent), acquire the evidence before extracting any gap. Do NOT ask the user to run the
bundle or transcribe the session separately.

**Step 0 — verify the session before acquiring evidence.** Resolve and verify the session
against a unique phrase from the current user message:

```bash
python3 .agents/skills/opencode/opencode-current-session-id/scripts/find-current-session.py \
    --verify-text "<unique phrase from the current user message>" --json
```

If it exits `1` (no match) or `2` (multiple matches), stop and present the candidates; do
not run the driver. Pass the verified session ID and the same phrase to the driver as
`--session-id` and `--verify-text`; the driver re-verifies and records
`session_verification` in the manifest.

```bash
python3 .agents/skills/general/skill-dev/skill-library-gap-closure/scripts/run-gap-closure-evidence.py \
    --session-id <ses-id> \
    --verify-text "<unique phrase from the current user message>" \
    --repo <repo> \
    --purpose skill-library-gap-closure-evidence \
    --json
```

The driver:

1. verifies the session when `--verify-text` is supplied and fails closed (exit `2`) on
   no match or ambiguity;
2. runs [`opencode-session-analysis-bundle`](../../../opencode/session/opencode-session-analysis-bundle/SKILL.md);
3. writes the session's `transcripts/*-transcript.yaml` human transcripts;
4. writes the full-fidelity JSONL and the report skeleton to session scratch;
5. writes `gap-closure-evidence-manifest.json` with the absolute paths of the session
   directory, source logs, transcripts, report, and JSONL, plus the
   `session_verification` record.

The `session_verification` record carries `status` (`verified` or `unverified` in a
written manifest), `text_sha256`, `matched_session`, and `candidates`. The verifier's
`ambiguous` and `no_match` statuses stop the driver before a manifest is written.

Fill the report's `## 1. Problem`, `## 2. Solution`, `## 4. Rejected / Alternative
Paths`, and `## 5. Final State` sections per
[`opencode-session-problem-solution-workflow-analysis`](../../../opencode/opencode-session-problem-solution-workflow-analysis/SKILL.md)
§2.1 steps 4–7. The `## 3. Workflow Executed` section is deterministic and must not be
rewritten.

If a report was supplied, it remains the authoritative analysis. The driver still
generates the archival transcript set and a fresh baseline skeleton; do not overwrite the
supplied report.

### 2.2 Evidence intake

Accept an evidence source: a workflow-analysis report, a walkthrough, or a user narrative
describing procedures that were worked out by hand. Record, per candidate gap, the
*source evidence* — the turn ordinal, log path, or quoted user instruction that shows the
procedure was actually needed.

Record the evidence anchor as a structured tuple: session ID, turn ordinal, tool name,
tool-call index, source log path, transcript path, and — when a repository path is cited —
the attribution file. A bare turn ordinal or a quoted sentence is not a complete anchor.

A gap with no evidence is a hunch. Hunches go into the plan as optional, never as
committed scope.

### 2.3 Verification — the decisive step

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
it costs time, not correctness. Do not treat a missing register as a reason to skip §2.3.

**Durability boundary.** What is committed is capability-facing metadata only: the public
`CHANGELOG.md` and `TRACEABILITY.md` companions per skill. Historical analysis — evidence
quotes, per-gap identifiers, hunk anchors, insertion-point tables — stays local. Keep those
companions short; they describe what a skill does, not the history of how it was decided.

### 2.4 New-skill-versus-enrichment verdict

Apply [`skill-factory`](../../../skill-factory/SKILL.md) §5.5 to each `PARTIAL` /
`NOT_DOCUMENTED` row:

- An owner exists and the gap is inside its declared scope → **enrich** that skill.
- No owner, but the capability is a reusable generic primitive → **new base skill** first,
  then a composer over it (§2.0 layering test: "could a different domain need this?").
- No owner, and the capability is an ordered domain workflow → **new composer skill**.

Prefer enriching over creating: a new skill for a one-off adds surface area and splits the
SSOT.

### 2.5 Scope the audit to the WHOLE evidence set

Derive the candidate list from **every** workflow in the evidence, not only the one that
prompted the question. A closure pass that audits one turn and declares the rest clean is
the single most common failure mode of this workflow: the gaps it misses are invisible
because they were never looked for.

### 2.6 Path evidence index

After the candidate gaps exist, collect every repository path or artifact path cited as
evidence and write one token per line to `<evidence-dir>/path-tokens.txt`. Then run:

```bash
python3 .agents/skills/general/skill-dev/skill-library-gap-closure/scripts/run-gap-closure-evidence.py \
    --session-id <ses-id> \
    --verify-text "<unique phrase from the current user message>" \
    --repo <repo> \
    --purpose skill-library-gap-closure-evidence \
    --evidence-dir <evidence-dir> \
    --attribution-only \
    --paths-file <evidence-dir>/path-tokens.txt \
    --json
```

Reuse the verified phrase from §2.1; attribution-only also fails closed on no match or
ambiguity. The driver defaults to the audited session. Add `--cross-session` when a path may have
been touched by another session; record that choice in the register.

Every returned record is a JSON array of tool calls that contain the token. Build the
`Evidence Verification Index` in the gap register and the plan of action from these
records and the bundle manifest. A `no_match` result is recorded as `no_match`; it is not
positive evidence. An attribution exit code `2` is a hard stop.

### 2.6.1 Deliberate re-run of the evidence pass

Re-auditing the same session is expected: the register is local-only (§2.3). Run it
deliberately, never by overwriting the prior pass.

1. **New purpose.** Append a rerun suffix to `--purpose` (for example
   `skill-library-gap-closure-evidence-rerun2`) so the new artifacts are not confused
   with the first pass.
2. **Separate evidence directory.** Point `--evidence-dir` at a sibling directory (for
   example `<scratch>/gap-closure-rerun2`), never the first pass's directory.
3. **Pre-create the redirect target.** A report redirect fails with
   `no such file or directory` when the directory does not exist. Create it first:

   ```bash
   mkdir -p <scratch>/gap-closure-rerun2
   ```

4. **Re-verify the session.** Reuse the verified phrase from §2.1 (or a fresh unique
   phrase from the current turn) and pass `--verify-text`; the driver fails closed on
   no match or ambiguity.
5. **Run the driver** with the new purpose and evidence directory:

   ```bash
   python3 .agents/skills/general/skill-dev/skill-library-gap-closure/scripts/run-gap-closure-evidence.py \
       --session-id <ses-id> \
       --verify-text "<unique phrase from the current user message>" \
       --repo <repo> \
       --purpose skill-library-gap-closure-evidence-rerun2 \
       --evidence-dir <scratch>/gap-closure-rerun2 \
       --json
   ```

6. **Keep the prior pass.** Do not delete or overwrite the earlier report or manifest;
   compare the new manifest to the prior one and record what changed in the register.

The driver's "No report overwrite" guardrail protects a supplied report; it does not
protect a directory path you reuse. The separate `--evidence-dir` is what makes the
re-run deliberate. If you only need to amend a filled report, use
[`deterministic-artifact-in-place-amendment`](../../planning/deterministic-artifact-in-place-amendment/SKILL.md)
instead of re-running the bundle.

### 2.7 Plan-first gate

Emit the ranked gap register and a versioned plan under `docs/` using
[`planning-artifact-lifecycle`](../../planning/planning-artifact-lifecycle/SKILL.md) and
[`planning-artifact-naming`](../../planning/planning-artifact-naming/SKILL.md), then
**stop** and present for approval. No skill folder, script, or registry row is created
before explicit approval.

The register and plan MUST each contain an `Evidence Verification Index` table covering
every gap row, including `DOCUMENTED` rows, with the columns defined in the evidence
manifest contract. The plan MUST also list the absolute paths of the evidence manifest,
report, JSONL, transcript directory, and attribution directory so the user can inspect
them directly.

The plan MUST surface a per-script tier declaration for every proposed new script, per
[`skill-factory`](../../../skill-factory/SKILL.md) §2.2.1.1 item 4.

The plan MUST contain a `## Files to Touch (absolute)` section with one row per file:
absolute path, owning gap, and the concrete change. A plan whose touch list is empty or
uses relative paths MUST NOT be presented for approval.

### 2.8 Routing and closure

For each approved row, route to skill-factory §6 (enrich) or §2 (create). Then:

- Register each new skill in [`skill-library-domain-grouping`](../../skill-library-domain-grouping/SKILL.md)
  BEFORE its `AGENTS-legacy.md` row, so the index never advertises an unregistered skill.
- Run [`skill-cross-reference-audit`](../../skill-cross-reference-audit/SKILL.md) after the
  batch and require zero new issues.
- Lint every touched markdown with `markdownlint-cli2` and require a clean gate.

## 3. Scripts

This skill ships one Tier-1 composer driver of its own. It does NOT re-implement session
extraction, path attribution, or planning logic; it sequences the composed CLIs and
persists a gap-closure-scoped evidence manifest.

| Step | Script owner |
| :--- | :--- |
| Evidence acquisition + manifest | [`scripts/run-gap-closure-evidence.py`](scripts/run-gap-closure-evidence.py) (this skill; composes verification, the bundle, and attribution) |
| Session verification | `opencode-current-session-id/scripts/find-current-session.py` (composed by the driver when `--verify-text` is supplied) |
| Session analysis bundle | `opencode-session-analysis-bundle/scripts/run-session-analysis-bundle.py` |
| Path attribution | `opencode-session-path-attribution/scripts/attribute-path-to-session.py` |
| Evidence report skeleton | `opencode-session-problem-solution-workflow-analysis/scripts/reconstruct-workflow.py` (called by the bundle) |
| Structural audit | `skill-cross-reference-audit/scripts/audit-cross-refs.py` |
| Taxonomy placement | `skill-library-domain-grouping` §1.2 (tree notation, no script) |
| Amend-vs-regenerate | `deterministic-artifact-in-place-amendment/scripts/detect-regeneration-need.py` |

The driver resolves the scripts it composes — the session verifier, session-analysis
bundle, path attribution, and `resolve-scratch-path.py` — relative to its own location
(`Path(__file__).resolve().parents[4]`) and verifies each mode-required script with
`Path.is_file()` before execution. A missing composed script is a distinct exit-4
diagnostic, never a silent re-implementation.

## 4. Guardrails

- No skill folder, script, or registry row is created before explicit plan approval.
- **Every plan names its files.** A plan MUST carry a `## Files to Touch (absolute)`
  section; a plan without it is incomplete and MUST NOT reach the approval gate.
- Every `NOT_DOCUMENTED` verdict MUST cite a zero-hit library-wide search.
- Every candidate gap from the evidence set MUST appear in the register, including
  `DOCUMENTED` ones.
- Committed artifacts MUST NOT carry session identifiers or references to gitignored
  `docs/` planning files — see [`redaction-portability`](../../../redaction-portability/SKILL.md).
- A parallel `ai-agent-rules/*.md` file MUST NOT be authored for any gap closed here.
- **Single-invocation evidence acquisition.** When the evidence source is a session, run
  the gap-closure driver. Do NOT ask the user to run the bundle or transcribe the session
  separately.
- **Verified session required under concurrency.** Never run the driver on a session that
  has not been verified against the current user turn when more than one session has an
  in-flight marker. Pass `--verify-text`; the driver fails closed (exit `2`) on no match or
  ambiguity and records `session_verification` in the manifest.
- **Human and machine artifacts are distinct.** Transcripts are human-facing derived
  artifacts; source logs and the full-fidelity JSONL are machine-facing. Never delete,
  trim, or annotate source logs or transcripts to make a report shorter.
- **Every claim is anchored.** Every gap row and every plan action cites at least one
  Evidence Verification Index row. A `no_match` attribution is not positive evidence.
- **Attribution exit codes are enforced.** Exit `1` is a recorded `no_match`; exit `2` is
  an infrastructure failure and stops the closure pass.
- **No report overwrite.** If a filled report exists, do not re-run the bundle by reflex.
  Use [`deterministic-artifact-in-place-amendment`](../../planning/deterministic-artifact-in-place-amendment/SKILL.md)
  to decide whether to regenerate or amend in place.
- **Local-only evidence.** The manifest, transcripts, attribution records, register, and
  plan stay under `.opencode/logs/`, `scratch/`, or `docs/`. Committed skill files carry
  no session identifiers and no links to those local paths.

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
