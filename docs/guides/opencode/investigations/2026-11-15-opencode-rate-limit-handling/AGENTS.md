# OpenCode Rate-Limit Handling Investigation — Agent Contract

## Purpose

Preserve the verified 2026-11-15 investigation of the `class_rate_limit` and `org_token_rate_limit_day` errors, the
OpenCode retry mechanics that do and do not handle them, the configuration settings that exist, and the gateway
failover options.

## Ownership

- `README.md`: the comprehensive incident report, root-cause analysis, configuration audit, gateway options,
  remediation, and validation criteria.
- `sources.md`: the primary public citations, verification scope, and qualifiers.
- This file owns the folder's evidence and documentation contracts.

## Local Contracts

- Inherit the repository root contract, `docs/AGENTS.md`, and `docs/guides/opencode/AGENTS.md`.
- Keep incident observations, source-derived explanations, configuration facts, and recommendations distinct.
- Do not include OpenCode session identifiers or machine-local scratch paths in this durable document.
- Preserve exact error classes, model identifiers, and version qualifiers.
- A free-core allowance is provider policy, not an OpenCode defect. A retry wait is client behavior, not a quota
  increase.
- Recommendations are not implementation status. Documentation does not establish that a configuration change was
  applied.

## Work Guidance

- Explain unfamiliar terms before using them in comparisons.
- When adding a later measurement, identify it as a new observation and preserve this document's dated evidence.
- Prefer the plain `gpt-6-luna` core identifier for long agent sessions; keep `:free` for free-only validation.
- Point current operating instructions at the Experiential Labs provider guide and the OpenCode documentation home.

## Verification

- Run the standalone `/opt/homebrew/bin/markdownlint-cli2` from the repository root on changed Markdown files.
- Verify every relative link resolves.
- Re-check provider quota wording and OpenCode retry constants against the version-matched source before relying on
  them for a new incident.

## Child DOX Index

No narrower contracts. This file owns the two documents in this folder.
