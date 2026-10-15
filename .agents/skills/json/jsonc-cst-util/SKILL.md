---
name: jsonc-cst-util
description: Base primitive — CST-aware JSONC read / sort / format that preserves comments and applies merge-friendly trailing commas; consumed by json-deep-sort and opencode-jsonc-util.
category: Base-Utility
---

# jsonc-cst-util (v1)

> **Name:** jsonc-cst-util<br>
> **Description:** Base primitive — read, sort, and format JSONC through a comment-preserving concrete syntax
tree; JSONC output carries merge-friendly trailing commas on every item.<br>
> **Category:** Base-Utility

## Description

Generic base primitive for reading, sorting, and formatting JSONC — JSON extended with `//` line
comments, `/* */` block comments, and optional trailing commas. Unlike a strip-then-`json.loads`
approach, the script parses JSONC into a concrete syntax tree (CST) that retains every comment and
every scalar lexeme, so a sort/format round-trip never drops comments, never rewrites string
escapes, and never corrupts comma hygiene.

Project-wide trailing-comma policy enforced by this skill: trailing commas are NEVER removed unless
the caller explicitly requests `--mode strict`; JSONC output applies **merge-friendly trailing
commas** — a comma after *every* item of every multi-line object and array, including the last — so
appending or removing an item never requires touching the previous item's line.

## Composition Rationale

This skill owns exactly one operation: "parse JSONC into a comment-preserving CST, optionally
deep-sort it, and serialize it back with mode-appropriate comma hygiene." The CST parse/serialize
primitive is generic — any workflow that edits a JSONC config file (sorting keys, normalizing
indentation, stripping comments for strict consumers) can reuse it. Known consumers that depend on
this skill's public contract (CLI, exit codes, stdout JSON):

| Composer | Composition Mechanism |
| --- | --- |
| [`json-deep-sort`](../../json-deep-sort/SKILL.md) | Its `scripts/sort-json.py` calls `jsonc_cst.py sort <file> --in-place` once per file, passing `--mode`/`--indent` through; consumes only the exit code. |
| [`opencode-jsonc-util`](../../opencode-jsonc-util/SKILL.md) | Its `scripts/read-jsonc.py` calls `jsonc_cst.py read <file>` via subprocess and parses the strict-JSON stdout; keeps its own CLI/API contract for its downstream consumers. |

## Related Skills

- [`json-diff-leaf`](../../json-diff-leaf/SKILL.md) — recursive leaf-value diff of two JSON files.
- [`json-content-compare-ignore-keys`](../../json-content-compare-ignore-keys/SKILL.md) — hash-based JSON snapshot comparison.
- [`json-block-indent-override`](../../json-block-indent-override/SKILL.md) — per-key indent overrides inside JSON blocks.

## Environment & Dependencies

| Requirement | Version | Notes |
| --- | --- | --- |
| Python | 3.12+ | Stdlib only (`json`, `re`, `argparse`, `pathlib`, `dataclasses`) — no pip dependencies |
| OS | Linux, macOS, Windows | Byte-safe UTF-8 I/O; CRLF preserved |

## Mode Resolution

`--mode` accepts `auto` (default), `jsonc`, or `strict`.

| Requested | Resolved behavior |
| --- | --- |
| `auto` | Resolves to `jsonc` when the path ends in `.jsonc`, or the input contains comments, or it contains a trailing comma; otherwise resolves to `strict`. |
| `jsonc` | Comments preserved; merge-friendly trailing commas emitted after every item of every multi-line object/array. |
| `strict` | Strict JSON: no trailing commas emitted. If the input contains comments, the command refuses with exit 3 — strict JSON cannot represent them, and silently dropping comments would violate the project policy. |

## CLI Contract

```bash
python3 scripts/jsonc_cst.py read   <file>
python3 scripts/jsonc_cst.py sort   <file> [--mode auto|jsonc|strict] [--indent N] [--in-place | --output PATH]
python3 scripts/jsonc_cst.py format <file> [--mode auto|jsonc|strict] [--indent N] [--in-place | --output PATH]
```

| Subcommand | Behavior |
| --- | --- |
| `read` | Strip comments and trailing commas; print strict JSON to stdout (always stdout; never mutates the file). |
| `sort` | Deep-sort object keys and primitive arrays (see Sort Semantics), then re-emit. |
| `format` | Re-emit with canonical indentation and mode-appropriate commas; performs NO reordering. |

| Flag | Default | Meaning |
| --- | --- | --- |
| `--mode` | `auto` | Mode resolution per the table above |
| `--indent` | `2` | Spaces per nesting level |
| `--in-place` | off | Rewrite the input file (mutually exclusive with `--output`) |
| `--output PATH` | — | Write the result to PATH (mutually exclusive with `--in-place`) |

Without `--in-place` or `--output`, `sort`/`format` write the result to stdout.

**Exit codes:**

| Code | Meaning |
| --- | --- |
| 0 | Success |
| 1 | I/O error or JSONC parse error (diagnostic with line/column on stderr) |
| 2 | Usage error (argparse) |
| 3 | `--mode strict` conflicts with comments present in the input |

## Comment Model

| Position | Definition |
| --- | --- |
| File-leading / file-trailing | Comments before / after the root value |
| Leading | Own-line comments between the previous item's separator and the item |
| Trailing | Comments on the same line as the item's value or its separator comma |
| Dangling | Own-line comments between the last item and a closing `}` / `]` |

All comments are re-emitted with the member/element they annotate, so they travel with their item
when sorting repositions it.

## Sort Semantics

- Object keys: case-sensitive lexicographic sort of the decoded key — identical to legacy
  `json-deep-sort` / `sort_keys=True` behavior.
- Primitive arrays: arrays whose elements are ALL strings, numbers, or booleans are sorted —
  strings case-insensitively, numbers numerically, booleans `false` before `true` (in mixed
  number/boolean arrays, all numbers sort before booleans).
- Mixed or structured arrays (containing `null`, objects, or arrays) are NOT reordered; their
  elements are still recursed into so nested objects get sorted.
- Duplicate keys are preserved (stable sort keeps their original relative order); `read` collapses
  them last-wins like any Python JSON parser.
- Sorting changes array order by design — that is the operation's contract.

## Formatting Semantics

- Merge-friendly trailing comma: in jsonc mode, every item of every multi-line object/array gets a
  comma, including the last.
- Empty containers stay inline: `{}` / `[]`.
- One member/element per line; scalars stay on their key's line.
- Line endings: CRLF is preserved when the input uses CRLF; otherwise LF.
- Input may carry a UTF-8 BOM; output is written as UTF-8 without BOM.
- String and number lexemes are preserved byte-for-byte (no escape normalization, no number
  re-formatting).

## Protocol

1. Read the file as bytes and decode UTF-8 (tolerating a BOM); tokenize into punctuation, scalars,
   and comments (string-aware — `//` inside a string is never a comment).
2. Scan for comments/trailing commas and resolve the effective mode.
3. Parse into the CST; on `sort`, recursively sort object members and sortable primitive arrays.
4. Serialize with the requested indent and mode-appropriate commas; write to stdout, `--output`, or
   `--in-place`; preserve CRLF when present.

## Edge Cases

- Empty root object/array with comments inside: comments are kept as dangling.
- Scalar root (e.g. `42`) with file-leading/trailing comments: supported.
- Unterminated string or block comment: parse error, exit 1 with line/column.
- A strict JSON file without comments resolves to `strict` in auto mode and round-trips without
  trailing commas.
- A JSONC file passed with explicit `--mode strict` is refused (exit 3) rather than comment-stripped.

## Verification

```bash
# Semantics preserved through sort (compare the two read outputs)
python3 scripts/jsonc_cst.py read fixture.jsonc > before.json
python3 scripts/jsonc_cst.py sort fixture.jsonc --mode jsonc --output sorted.jsonc
python3 scripts/jsonc_cst.py read sorted.jsonc > after.json

# Idempotency (second sort must be byte-identical)
python3 scripts/jsonc_cst.py sort sorted.jsonc --mode jsonc --output sorted2.jsonc
cmp sorted.jsonc sorted2.jsonc

# Strict refusal on commented input (expect exit 3)
python3 scripts/jsonc_cst.py sort fixture.jsonc --mode strict; echo "exit=$?"
```

## Composition by Higher-Level Skills

| Composer | Composition Mechanism |
| --- | --- |
| [`json-deep-sort`](../../json-deep-sort/SKILL.md) | `scripts/sort-json.py` calls `jsonc_cst.py sort <file> --in-place` once per file with `--mode`/`--indent` passthrough; consumes the exit code only. |
| [`opencode-jsonc-util`](../../opencode-jsonc-util/SKILL.md) | `scripts/read-jsonc.py` calls `jsonc_cst.py read <file>` via subprocess and parses the strict-JSON stdout, preserving its own CLI/API contract for downstream consumers. |

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Traceability

See [TRACEABILITY.md](TRACEABILITY.md).
