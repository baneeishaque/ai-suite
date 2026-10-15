---
name: opencode-jsonc-util
description: Base — read OpenCode JSONC config files (comments, trailing commas) via the jsonc-cst-util CST parser; stable read-jsonc.py CLI/API for opencode-remote-mcp-setup, opencode-permission-config, and other consumers.
category: Base-Utility
---

# OpenCode JSONC Utility (v2)

> **Name:** opencode-jsonc-util<br>
> **Description:** Wrapper — read OpenCode JSONC config files through the jsonc-cst-util base primitive and
emit strict JSON; preserves a stable CLI/API contract for downstream consumers.<br>
> **Category:** Base-Utility

## Description

Base primitive for reading OpenCode's JSONC configuration format — files that permit `//` comments
and trailing commas, which standard `json.loads` rejects. Parsing is delegated to the
[`jsonc-cst-util`](../json/jsonc-cst-util/SKILL.md) CST base primitive; this skill keeps the stable,
domain-named `read-jsonc.py` CLI/API contract that downstream scripts already invoke by path.

The v1 line-based stripper could not handle `/* */` block comments and could misread `//` inside
strings containing escaped quotes; v2 delegates to the CST parser, which is string-aware and
comment-correct.

## JSONC Format Summary

OpenCode config files (`opencode.json`, `opencode.jsonc`) extend JSON with two relaxations:

1. **Trailing commas** are permitted before `]` and `}`.
2. **`//` comments** are permitted as full-line or inline (trailing) comments.

## Composition Rationale

This skill is a thin wrapper over [`jsonc-cst-util`](../json/jsonc-cst-util/SKILL.md): it does NOT
re-implement JSONC parsing. `scripts/read-jsonc.py` calls the base's
`jsonc_cst.py read <file>` subcommand via a path anchored on its own location, parses the
strict-JSON stdout, and re-emits it under this skill's contract. The wrapper's value-add is the
frozen, domain-named contract (`read-jsonc.py <file>` CLI + `read_jsonc()` API) that downstream
consumers invoke directly — that contract stays fixed even if the base primitive's CLI evolves.

Base skill:

1. **[`jsonc-cst-util`](../json/jsonc-cst-util/SKILL.md)** — `read` subcommand; consumes stdout
   strict JSON and the exit code.

## Related Skills

- [`opencode-provider-persistence-config`](../opencode-provider-persistence-config/SKILL.md) — OpenCode credential
  storage details.
- [`opencode-google-gemini-config`](../opencode-google-gemini-config/SKILL.md) — Gemini provider configuration.
- [`opencode-config-preserve`](../opencode-config-preserve/SKILL.md) — OpenCode config preservation.

## Environment & Dependencies

| Requirement | Version | Notes |
| --- | --- | --- |
| Python | 3.12+ | Stdlib only (`json`, `subprocess`, `pathlib`) |
| `jsonc-cst-util` base skill | v1+ | Must be installed at `.agents/skills/json/jsonc-cst-util/` |

## Usage

### CLI

```bash
python3 scripts/read-jsonc.py <file-path>
```

- Reads the file, strips comments and trailing commas, outputs valid JSON (indent 2) to stdout.
- Exit 0 on success, 1 on failure with diagnostic to stderr
  (`ERROR: file not found: ...` / `ERROR: invalid JSONC: ...`).

### Python

Import `read_jsonc` from `scripts/read-jsonc.py`:

```python
from read_jsonc import read_jsonc
data = read_jsonc("/path/to/opencode.json")
```

Raises `ValueError` on invalid JSONC and `FileNotFoundError` when the base script is missing.

## Protocol

1. Resolve the base script path anchored on this script's own location.
2. Invoke the base `read` subcommand for the target file.
3. Forward the base's strict-JSON stdout; map any base failure to exit 1 with the base diagnostic.

## Composition by Higher-Level Skills

| Composer | Composition Mechanism |
| --- | --- |
| [`opencode-remote-mcp-setup`](../opencode-remote-mcp-setup/SKILL.md) | `scripts/validate-opencode-mcp.py` calls `read-jsonc.py <file>` via subprocess and JSON-parses the stdout to validate the `mcp` section. |
| [`opencode-permission-config`](../opencode-permission-config/SKILL.md) | `scripts/verify-permission-pattern.py` calls `read-jsonc.py <source>` for JSONC configs; falls back to plain `json.load` when the reader fails. |
| [`opencode-installed-plugin-lookup`](../opencode/opencode-installed-plugin-lookup/SKILL.md) | `scripts/locate-installed-plugins.py` calls `read-jsonc.py` via its repo-root-anchored path to read the user/project opencode config. |
| [`cross-tool-shell-command-permission-sync`](../general/permission-sync/cross-tool-shell-command-permission-sync/SKILL.md) | `scripts/sync-permission-rules.py` calls `read-jsonc.py` for each tool config, falling back to `json` on failure. |
| [`pr-merge-decision-classifier`](../github/repo/pr-merge-decision-classifier/SKILL.md) | `scripts/classify-pr.py` reads `provider.<name>.api` from the OpenCode JSONC config via `read-jsonc.py`. |

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Traceability

See [TRACEABILITY.md](TRACEABILITY.md).
