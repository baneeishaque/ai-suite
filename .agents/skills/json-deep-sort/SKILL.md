---
name: json-deep-sort
description: Composer — deep-sort JSON/JSONC files (object keys and primitive arrays) in place, preserving comments and merge-friendly trailing commas; delegates to the jsonc-cst-util base primitive.
category: Data Processing
---

# json-deep-sort (v2)

> **Name:** json-deep-sort<br>
> **Description:** Composer — deep-sort object keys and primitive arrays in JSON/JSONC files in place while
preserving comments and merge-friendly trailing commas; delegates all parsing and serialization to the
jsonc-cst-util base primitive.<br>
> **Category:** Data Processing

## Description

Domain composer over the [`jsonc-cst-util`](../json/jsonc-cst-util/SKILL.md) base primitive. It
sorts one or more JSON/JSONC files in place: object keys case-sensitively (matching the historical
`sort_keys=True` behavior) and arrays whose elements are all strings, numbers, or booleans —
strings case-insensitively, numbers numerically, booleans `false` before `true`.

Unlike the legacy v1 inline implementation (a `python -c` snippet that parsed with strict
`json.load`), comments are preserved, JSONC files keep merge-friendly trailing commas, CRLF line
endings survive, and mixed or structured arrays are left in order while their elements are still
recursed into.

## Composition Rationale

This skill is a composer: it does NOT re-implement JSONC parsing, sorting, or serialization. It
orchestrates one atomic base skill:

1. **[`jsonc-cst-util`](../json/jsonc-cst-util/SKILL.md)** — `scripts/sort-json.py` calls its
   `jsonc_cst.py sort <file> --in-place` subcommand once per file, passing `--mode` and `--indent`
   through, and consumes only the exit code. The base owns the CST parse, the deep-sort algorithm,
   and the merge-friendly serialization.

The composer's value-add over the base: multi-file iteration in a single invocation, the legacy
in-place default UX, and a stable domain-named entry point (`scripts/sort-json.py`) that callers can
use without knowing the base's subcommand shape. Inlining the base would duplicate the CST parser
that [`opencode-jsonc-util`](../opencode-jsonc-util/SKILL.md) also consumes.

## Related Skills

- [`json-diff-leaf`](../json-diff-leaf/SKILL.md) — recursive leaf-value diff; sorting first reduces
  key-order noise in the diff.
- [`json-content-compare-ignore-keys`](../json-content-compare-ignore-keys/SKILL.md) — hash-based JSON
  snapshot comparison; sorting first stabilizes the hash.
- [`json-block-indent-override`](../json-block-indent-override/SKILL.md) — per-key indent overrides
  inside JSON blocks.

## Environment & Dependencies

| Requirement | Version | Notes |
| --- | --- | --- |
| Python | 3.12+ | Stdlib only (`argparse`, `subprocess`, `pathlib`) |
| `jsonc-cst-util` base skill | v1+ | Must be installed at `.agents/skills/json/jsonc-cst-util/`; the script verifies its existence and exits 1 with a clear error when missing |

## CLI Contract

```bash
python3 scripts/sort-json.py <file>... [--mode auto|jsonc|strict] [--indent N]
```

| Argument | Required | Description |
| --- | --- | --- |
| `files` | Yes (1+) | JSON/JSONC files; each is sorted IN PLACE |
| `--mode` | No | Passthrough to the base mode resolution (`auto` default) |
| `--indent` | No | Passthrough to the base serializer (default: 2) |

**Exit codes:**

| Code | Meaning |
| --- | --- |
| 0 | Every file sorted successfully |
| 1 | One or more files failed (remaining files are still attempted; per-file diagnostics come from the base on stderr) |

## Sort Semantics

- Object keys: case-sensitive lexicographic sort of the decoded key.
- Primitive arrays (all elements strings/numbers/booleans): strings case-insensitively, numbers
  numerically, booleans `false` before `true` (in mixed number/boolean arrays, numbers first).
- Mixed or structured arrays (containing `null`, objects, or arrays): NOT reordered; elements are
  still recursed into.
- Comments travel with the member/element they annotate; JSONC files keep merge-friendly trailing
  commas; CRLF is preserved when present.
- Duplicate keys are preserved (stable sort keeps their original relative order).

## Protocol

1. Resolve the base script path anchored on this script's own location; verify it exists (exit 1
   with a clear error if missing).
2. For each input file, invoke the base `sort` subcommand with `--in-place` and the requested
   `--mode`/`--indent`.
3. Count failures without aborting the remaining files; exit 0 only when all succeeded.

## Edge Cases

- JSONC file: `auto` mode resolves to `jsonc`; comments and trailing commas are preserved.
- Strict JSON file: `auto` resolves to `strict`; no trailing commas are added.
- Explicit `--mode strict` on a commented file: the base refuses that file with exit 3, counted as
  a failure; other files still process.
- One invalid file does not abort the batch.

## Verification

```bash
printf '{\n  // note\n  "b": 1,\n  "a": [3, 1, 2],\n}\n' > sample.jsonc
python3 scripts/sort-json.py sample.jsonc
cat sample.jsonc   # "a" first, array sorted, comment kept, trailing comma kept
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Traceability

See [TRACEABILITY.md](TRACEABILITY.md).
