---
name: opencode-session-yaml-tool-call-extractor
description: >-
  Base — extract every assistant tool call (tool, args, result) from opencode
  logger-plugin YAML logs (monolithic ses_<id>.yaml OR per-turn ses_<id>/
  directory of NNN-*.yaml files) as chronological JSONL; domain-agnostic
  primitive for any YAML-log analysis or file-change recovery workflow.
category: OpenCode
---

# OpenCode Session YAML Tool-Call Extractor (v1)

## 1. Environment & Dependencies

| Requirement | Minimum | Verification |
| --- | --- | --- |
| Python | 3.12+ | `python3 --version` |
| PyYAML | any | `python3 -c "import yaml"` |

PyYAML is the only third-party dependency (PEP 723 / pip or system
package manager). The script imports `yaml` at module top; a missing
package produces a traceback — install it with
`python3 -m pip install pyyaml` or the system package manager before use.

***

## 2. Operational Logic

### 2.1 Input Layouts

The opencode logger plugin writes two YAML layouts, both accepted by
`--input`:

| Layout | Path | Content |
| --- | --- | --- |
| Monolithic | `.opencode/logs/ses_<id>.yaml` | Multi-document YAML (`---` separated): doc 1 = session header (`session:` key); docs 2..N = turns (`user:` / `assistant:`) |
| Per-turn directory | `.opencode/logs/ses_<id>/` | One file per turn: `000-header-*.yaml` + `NNN-<timestamp>.yaml`; filename order = chronological order |

### 2.2 Turn Schema

```yaml
---
user:
  text: |-
    ...
  time: ...
assistant:
  - agent: build
    model: {id: ..., provider: ...}
    thinking: |-
    tool_calls:
      - tool: write
        args: {filePath: ..., content: ...}
        result: |-
```

`assistant` and `tool_calls` are lists but may appear as a single dict —
both shapes are normalized. Turns without `tool_calls` are skipped.

### 2.3 Output Record

One JSONL record per tool call, chronological order
(per-turn file order, then in-list order):

```json
{"index": 0, "tool": "bash", "args": {"command": "..."}, "result": "..."}
```

| Key | Type | Meaning |
| --- | --- | --- |
| `index` | int | Global 0-based tool-call counter across the whole session |
| `tool` | str | Tool name (`write`, `edit`, `bash`, `skill`, ...) |
| `args` | dict | Raw tool arguments (unchanged from YAML) |
| `result` | str | Raw tool result text (may be large) |

***

## 3. CLI Contract (Stable)

```bash
python3 scripts/extract-yaml-tool-calls.py --input <path> \
    [--tool write] [--tool edit] [--output <file>]
```

| Flag | Required | Description |
| --- | --- | --- |
| `--input` | Yes | Monolithic `.yaml` file OR per-turn directory of `NNN-*.yaml` files |
| `--tool` | No | Filter to one tool name (repeatable) |
| `--output` | No | Write JSONL to file instead of stdout |

### Exit Codes

| Code | Meaning |
| --- | --- |
| 0 | Success — at least one tool call found |
| 1 | No tool calls found matching criteria |
| 2 | Parse failure (YAML error, read error) |
| 3 | Input path not found |

### Output Semantics

- stdout carries ONLY the JSONL payload (no diagnostics) — safe to pipe
- Informational messages go to stderr (`Found N tool call(s)`, warnings)
- Malformed YAML in one file logs a stderr warning and continues
- Records are emitted with `ensure_ascii=False`

***

## 4. Scripts

- [`scripts/extract-yaml-tool-calls.py`](scripts/extract-yaml-tool-calls.py) —
  Tier-1 Python CLI (stdlib + PyYAML)

***

## Related Skills

| Skill | Relationship |
| --- | --- |
| [`opencode-current-session-id`](../opencode-current-session-id/SKILL.md) | Sibling in the `opencode/` group — resolves the current session ID/title from the same logger logs |
| [`opencode-session-yaml-transcript-extractor`](../opencode-session-yaml-transcript-extractor/SKILL.md) | Parallel base skill — per-turn transcript JSONL (user text + thinking + tool calls) over the same YAML layouts; this skill's superset |
| [`opencode-session-problem-solution-workflow-analysis`](../opencode-session-problem-solution-workflow-analysis/SKILL.md) | Sibling composer — reconstructs problem/solution/executed-workflow reports over the transcript base (adjacent analysis domain) |
| [`jsonl-content-extractor`](../../jsonl-content-extractor/SKILL.md) | Parallel base skill — key-path extraction over JSONL (different input format) |

***

## 7. Traceability

- Origin: Session `ses_046cbc31fffe2WLkugMfyQfmhJ` — created as Phase A of
  the YAML-log upgrade for the file-changes session skill family
- Source of truth for the YAML layout: the opencode logger-plugin artifacts
  under `.opencode/logs/`
- Created 2026-07-31

***

## 8. Changelog

See [CHANGELOG.md](CHANGELOG.md).
