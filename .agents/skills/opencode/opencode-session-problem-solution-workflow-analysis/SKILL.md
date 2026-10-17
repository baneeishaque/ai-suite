---
name: opencode-session-problem-solution-workflow-analysis
description: >-
  Analyze an opencode logger-plugin session log to identify the problem, its
  solution, and the entire workflow executed — via a deterministic report
  skeleton over the base transcript extractor plus agent judgement guidance.
category: Tool-Configuration
---

# OpenCode Session Problem-Solution-Workflow Analysis (v1)

## Composition Rationale

This skill is a **composer**: it does NOT re-implement YAML parsing or
transcript extraction. It orchestrates one base skill:

1. **[`opencode-session-yaml-transcript-extractor`](../opencode-session-yaml-transcript-extractor/SKILL.md)** —
   invoked FIRST. The composer shells out to its
   `scripts/extract-yaml-transcript.py --input <session> --truncate <N>`
   via subprocess (path anchored on the composer script's own location,
   `Path(__file__).resolve().parents[2]`), and consumes the stdout JSONL
   (session_header / user_text / thinking / tool_call records) at its step 1.

The composer's domain-specific value-add over the base alone: the
reconstruction procedure itself — reading the problem out of the user's
messages (incl. correction turns), locating the accepted solution, and
classifying tool sequences into accepted vs rejected paths — plus the
deterministic markdown report skeleton (session meta, per-turn chronology,
summary table) emitted by `scripts/reconstruct-workflow.py`.

Inlining the transcript parse here would duplicate logic that any other
session-analysis composer (summarization, debugging forensics, fidelity
scans) also consumes.

Bidirectional discoverability: the base lists this composer in its
`## Composition by Higher-Level Skills` table.

***

## 1. Environment & Dependencies

| Requirement | Minimum | Verification |
| --- | --- | --- |
| Python | 3.11+ (3.12 recommended) | `python3 --version` |
| Base skill installed | present | the composer exits 4 with a clear error if `opencode-session-yaml-transcript-extractor/scripts/extract-yaml-transcript.py` is missing |

The composer script is stdlib-only (`json`, `subprocess`, `argparse`,
`pathlib`, `datetime`, `sys`). The base skill brings the PyYAML
dependency — see its Environment & Dependencies section.

***

## 2. Operational Logic

### 2.1 The 7-step analysis procedure (Zero Omission)

1. **Locate the session's log files** — `.opencode/logs/ses_<id>/` per-turn
   directory (`000-header-*.yaml` + `NNN-<timestamp>.yaml`; filename order
   IS chronological) or the monolithic `ses_<id>.yaml`. Both layouts are
   accepted by `--input`.
2. **Extract the transcript** — run the base
   `extract-yaml-transcript.py` (via the composer script, or directly):
   one JSONL record per narrative element with global `index` and `turn`.
3. **Render the deterministic skeleton** — run
   `scripts/reconstruct-workflow.py --input <session> --output <report.md>`:
   session meta (id/title when present), `## 3. Workflow Executed` per-turn
   chronology (user text, thinking, tool calls with truncated args/results),
   per-turn tool-call summary table.
4. **Identify the Problem** (judgement) — read the user's textual messages:
   the FIRST message states the original ask; correction turns
   ("no, this is wrong", "yes - got it") mark rejected vs accepted states.
   Quote the exact user text that defines the problem.
5. **Identify the Solution** (judgement) — the state/answer the user
   ultimately accepts. Cite the concrete evidence path that produced it
   (DB key, file path, CLI command, output record).
6. **Classify the workflow** (judgement over the skeleton) — mark each
   tool-call prefix as accepted path or rejected/alternative path, using the
   thinking text and the correction turns as the boundary signal.
7. **Synthesize** — fill `## 1. Problem`, `## 2. Solution`,
   `## 4. Rejected / Alternative Paths`, `## 5. Final State` in the report;
   the `## 3. Workflow Executed` section is already deterministic.

### 2.2 Judgement guidance

- **Correction turns are the strongest signal**: a user message beginning
  with "no", "wrong", or restating the ask ("i want open editors. also all
  my editor tabs are pinned.") closes the previous attempt and re-opens the
  problem. The turn immediately AFTER the last correction carries the
  accepted direction.
- **The solution must be evidenced**: record the exact artifact that
  produced it (e.g. `state.vscdb` key `memento/workbench.parts.editor` →
  `editorpart.state.serializedGrid`, `sticky: N` = pinned count) — a
  solution without a path is an assertion, not an answer.
- **Rejected paths precede the correction**: a rejected path is a tool-call
  prefix that the thinking text abandons ("doesn't expose", "not persisted",
  "rejected path") or that a correction turn overrides.
- **Bound output size**: always pass `--truncate` (default 500) — full
  args/results must never be dumped to scrollback; the complete fidelity
  lives in the JSONL, not the report.

***

## 3. Scripts

- [`scripts/reconstruct-workflow.py`](scripts/reconstruct-workflow.py) —
  Tier-1 Python CLI (stdlib): subprocesses the base extractor, builds the
  report skeleton.

### CLI Contract (Stable)

```bash
python3 scripts/reconstruct-workflow.py --input <yaml-file|dir> \
    [--truncate <N>] [--output <report.md>] \
    [--exclude-turn <N>]... [--exclude-reason <text>]
```

| Flag | Required | Description |
| --- | --- | --- |
| `--input` | Yes | Monolithic `.yaml` file OR per-turn session directory |
| `--truncate` | No | Truncate text/args/result to N chars (default 500) |
| `--output` | No | Write the report to file instead of stdout |
| `--exclude-turn <N>` | No | Exclude a per-turn ORDINAL from the analysis (repeatable). Renders as a stub and is dropped from the summary counts. |
| `--exclude-reason <text>` | No | Rationale recorded for every excluded turn, in the banner and each stub. |

With neither exclusion flag the output is byte-identical to the pre-flag report; the default path is
regression-gated against a frozen session fixture.

### Exit Codes

| Code | Meaning |
| --- | --- |
| 0 | Success — report generated |
| 2 | Base extraction failed (parse error, no records) |
| 3 | Input path not found |
| 4 | Base skill script missing |

### Output Contract

The report is a markdown skeleton: session meta blockquote, `## 1. Problem`,
`## 2. Solution`, `## 3. Workflow Executed` (deterministic per-turn
chronology + summary table), `## 4. Rejected / Alternative Paths`,
`## 5. Final State`. The TBD placeholder blocks are the agent-judgement
sections to be filled per §2.1 steps 4–7.

### Turn exclusion

**Ordinal vs index vs heading — three different numbers.** Never conflate them:

| Concept | Source | Used for |
| --- | --- | --- |
| Per-turn **ordinal** | the `turn` field; `-1` on the session header record | `--exclude-turn`, `### Turn N` headings |
| Global **index** | the `index` field; 0-based across the whole session | `- **[index]**` tool-call citations in prose |

Excluding a turn by ordinal does **not** renumber the remaining `### Turn N` headings, and it **does**
invalidate every global `index` citation that pointed into the excluded turn. Strike those citations and
repair the totals the generator does not own.

**Excluded turn rendering.** An excluded turn keeps its `### Turn N` heading position and is replaced in
place by a stub carrying the reason. A header banner lists every excluded ordinal. The `### Summary` total
and per-turn table are recomputed over INCLUDED turns only.

**Self-referential exclusion.** A turn that issues the exclusion instruction is excluded by passing its own
ordinal in the same run. There is no special syntax, and the stub is built from the same single records pass,
so no recursion is possible.

**Source data is never modified.** Source logs and the adjacent `*-transcript.yaml` files stay complete —
they are the archival record. Exclusion is an ANALYSIS-layer concept only.

### Regenerate-vs-amend gate

When a report needs a change the generator cannot express, do not blindly re-run it: re-running discards
merged judgement sections. Decide with
[`deterministic-artifact-in-place-amendment`](../../general/planning/deterministic-artifact-in-place-amendment/SKILL.md):
generate a baseline, compare, and amend in place when the verdict is `FRESH`.

***

## Related Skills

| Skill | Relationship |
| --- | --- |
| [`opencode-session-yaml-tool-call-extractor`](../opencode-session-yaml-tool-call-extractor/SKILL.md) | Parallel base — tool-call-only extraction; useful when only the call sequence is needed |
| [`opencode-current-session-id`](../opencode-current-session-id/SKILL.md) | Sibling — resolves the CURRENT session's ID/title from the same logs |
| [`session-full-change-audit`](../../session-full-change-audit/SKILL.md) | Sibling composer — all-change audit of a session (write/edit/bash heredoc); complements the workflow reconstruction |
| [`session-file-ops-audit`](../../session-file-ops-audit/SKILL.md) | Sibling composer — bash file-operation audit; complements the workflow reconstruction |
| [`opencode-session-analysis-bundle`](../session/opencode-session-analysis-bundle/SKILL.md) | Consumer composer - shells out to `scripts/reconstruct-workflow.py --input <ses-dir> --truncate <N> --output <report.md>` at bundle Step 4 and fills its judgement sections |

***

## 4. Traceability

- Origin: 2026-08-11 — created after analyzing the "Listing absolute paths of open VSCode files" workflow,
  which demonstrated the undocumented problem → solution → workflow reconstruction procedure; the composer
  script generalizes the ad-hoc summarizer + narrative dumper used during that analysis.
- Created 2026-08-11

***

## 5. Changelog

See [CHANGELOG.md](CHANGELOG.md).
