---
name: opencode-session-analysis-bundle
description: End-to-end opencode session analysis bundle — adjacent YAML transcripts, scratch workflow report, and path manifest in one composer run.
category: Session-Analysis
---

# Opencode Session Analysis Bundle (v1)

> **Skill ID:** `opencode-session-analysis-bundle`<br>
> **Version:** 1.0.0<br>
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)<br>
> **Layer:** Composer

## Composition Rationale

This skill is a **composer**: it owns no discovery, extraction, naming, or reconstruction logic. It orchestrates
five existing skills in fixed order, shelling out to their CLIs through a thin driver
(`scripts/run-session-analysis-bundle.py`, Tier 1, `parents[3]`-anchored to `opencode/`):

1. [`opencode-current-session-id`](../../opencode-current-session-id/SKILL.md) — invoked FIRST (Step 0). The
   driver runs `scripts/find-current-session.py --json` (or accepts `--session-id`) and reads `session_id`,
   `pending`, and `log_dir`. A `pending: false` result is a stderr warning, never a silent accept.
2. [`opencode-installed-plugin-lookup`](../../opencode-installed-plugin-lookup/SKILL.md) — invoked at Step 1
   (unless `--log-dir` is given). The driver runs `scripts/locate-installed-plugins.py --plugin logger --json`
   and reads `logs_dir` as the session-log root.
3. [`opencode-session-yaml-conversation-extractor`](../../opencode-session-yaml-conversation-extractor/SKILL.md) —
   invoked at Step 2. The driver runs `scripts/extract-yaml-conversation.py --input <ses-dir> --output-dir
   <ses-dir>/transcripts`; the per-turn `*-transcript.yaml` adjacency is consumed as the archival transcript set.
4. [`opencode-session-yaml-transcript-extractor`](../../opencode-session-yaml-transcript-extractor/SKILL.md) —
   invoked at Step 3 (unless `--no-jsonl`). The driver runs `scripts/extract-yaml-transcript.py --input <ses-dir>
   --output <scratch-stem>.jsonl` (no truncation: full fidelity beside the scratch report).
5. [`opencode-session-problem-solution-workflow-analysis`](../../opencode-session-problem-solution-workflow-analysis/SKILL.md)
   invoked at Step 4. The driver runs that composer's `scripts/reconstruct-workflow.py --input <ses-dir>
   --truncate <N> --output <scratch-stem>.md`; the agent then fills its judgement sections.
6. [`scratch-artifact-naming`](../../../general/file/scratch-artifact-naming/SKILL.md) — invoked at Step 1 for
   placement. The driver runs `scripts/resolve-scratch-path.py --repo <repo> --purpose <slug>` and appends
   `.md` / `.jsonl` to the printed stem.

The composer's domain-specific value-add over the five skills alone: one CLI surface guaranteeing discovery →
locate → transcribe → report → manifest ordering, turn-exclusion semantics, and an absolute-path manifest.
Inlining any base would duplicate logic other composers consume. Bidirectional discoverability: each composed
skill lists this bundle back (Composition table or Related Skills).

## 1. Environment & Dependencies

| Requirement | Minimum | Verification |
| :--- | :--- | :--- |
| Python | 3.9+ (stdlib-only driver) | `python3 --version` |
| PyYAML | any | `python3 -c "import yaml"` (transcript base) |
| ruamel.yaml | any | `python3 -c "import ruamel.yaml"` (conversation base) |
| git | any | `git --version` (scratch repo must exist) |

## 2. Operational Logic

- **Step 0 — Resolve session.** Auto-discover via `find-current-session.py --json`, or take `--session-id`
  (resolved in the current run, never remembered). Refuse to guess when several sessions are in-flight: surface
  candidates. Verify the pending-marker flag before use.
- **Step 1 — Locate logs + scratch stem.** Logger root from `locate-installed-plugins.py --plugin logger --json`
  (or `--log-dir`); `ses-dir = <root>/ses_<id>`, missing → exit 3. Scratch stem from `resolve-scratch-path.py`.
- **Step 2 — Adjacent transcripts.** Conversation extractor with `--output-dir <ses-dir>/transcripts`
  (idempotent rewrite; time fields are dropped by the base, so reruns are byte-identical absent new turns).
- **Step 3 — Full-fidelity JSONL.** Transcript extractor `--output <stem>.jsonl`, untruncated (skip: `--no-jsonl`).
- **Step 4 — Report skeleton.** `reconstruct-workflow.py --input <ses-dir> --truncate <N> --output <stem>.md`.
- **Step 5 — Exclusions.** Each `--exclude-turn N` (+ `--exclude-reason`) is passed straight through to the
  generator, which emits the exclusion stub in place of the turn body, writes the header banner, and recomputes
  the summary totals over included turns only. The driver performs NO post-hoc appendix and NO count repair of
  its own — an appendix cannot repair counts it has already printed above itself.

  **Source logs and transcripts stay complete.** They are the archival record and are never trimmed, deleted, or
  annotated. Exclusion is an ANALYSIS-layer concept: it changes what the report says, not what the evidence
  contains. This is a hard rule, not a convenience.

  **Regenerate-vs-amend.** If a filled-in report needs a further change, do not re-run the bundle by reflex — that
  discards the merged judgement sections. Decide with
  [`deterministic-artifact-in-place-amendment`](../../../general/planning/deterministic-artifact-in-place-amendment/SKILL.md):
  produce a baseline, compare, and amend in place when the verdict is `FRESH`.
- **Step 6 — Judgement + manifest.** Fill workflow-analysis judgement sections; driver prints the JSON manifest
  (session dir, transcripts, report, JSONL) to stdout — the absolute-path inventory.

## 3. Driver CLI Contract

```bash
python3 scripts/run-session-analysis-bundle.py [--session-id <ses>] [--log-dir <dir>] [--repo <dir>]
    [--purpose <slug>] [--truncate <N>] [--no-jsonl] [--exclude-turn <N>]... [--exclude-reason <text>]
```

Exit codes: `0` bundle complete; `2` a base extraction failed; `3` session dir missing; `4` a composed script
is missing (pre-flight). Stdout carries ONLY the JSON manifest; diagnostics go to stderr.

## 4. Scripts

- [`scripts/run-session-analysis-bundle.py`](scripts/run-session-analysis-bundle.py) — Tier-1 driver (stdlib
  `argparse`, `subprocess`, `pathlib`, `json`, `sys`); resolves every base through
  `Path(__file__).resolve().parents[3]` and exits non-zero with a clear error when one is absent.

## 5. Composition by Higher-Level Skills

| Composer | Composition Mechanism |
| :--- | :--- |
| [`skill-library-gap-closure`](../../../general/skill-dev/skill-library-gap-closure/SKILL.md) | Evidence acquisition: the gap-closure driver calls `scripts/run-session-analysis-bundle.py --session-id <id> --repo <repo> --purpose skill-library-gap-closure-evidence`; it consumes the JSON manifest to locate the adjacent `*-transcript.yaml` files, full-fidelity JSONL, and report skeleton before gap extraction. |

## Related Skills

- [`opencode-session-transcript-to-source-resolve`](../../opencode-session-transcript-to-source-resolve/SKILL.md) —
  reverse navigator: resolves bundle `transcripts/` paths back to source logs for machine analysis.
- [`opencode-session-yaml-tool-call-extractor`](../../opencode-session-yaml-tool-call-extractor/SKILL.md) —
  parallel base for tool-call-only JSONL when the full narrative is unneeded.
- [`session-full-change-audit`](../../../session-full-change-audit/SKILL.md) — sibling composer complementing
  the workflow reconstruction with the all-change audit.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Traceability

See [TRACEABILITY.md](TRACEABILITY.md).
