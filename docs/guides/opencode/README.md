<!-- title: OpenCode setup and diagnostic documentation -->

# OpenCode Setup and Diagnostic Documentation

Detailed local documentation for using OpenCode in the AI-suite repository. Start with the dated investigation that
matches the installed version and the behavior being examined.

## Start Here

- [2026-11-04 model-behavior investigation](investigations/2026-11-04-model-behavior/README.md): verified explanations
  for false media warnings, repeated compaction, unavailable models, session-ID mistakes, and prompt overhead.
- [Model-selection guide](investigations/2026-11-04-model-behavior/model-selection-guide.md): understand which
  provider routes fit Build, Plan, or the zero-tool AgentX agent.
- [Remediation and validation](investigations/2026-11-04-model-behavior/remediation-and-validation.md): prioritized
  changes, expected outcomes, and evidence needed to confirm a fix.
- [2026-11-15 rate-limit handling investigation](investigations/2026-11-15-opencode-rate-limit-handling/README.md):
  explain the Experiential Labs free-core quota, OpenCode retry behavior, the missing per-provider retry settings, and
  OmniRoute failover options.
- [Experiential Labs provider guide](providers/experiential-labs/README.md): operate the 963-definition free-only
  provider, refresh the catalog, and troubleshoot grants, BYOK, Batch, billing, and metadata gaps.

## Documentation Map

```text
opencode/
├── AGENTS.md
├── README.md
├── investigations/
    ├── 2026-11-04-model-behavior/
    │   ├── AGENTS.md
    │   ├── README.md
    │   ├── incident-report.md
    │   ├── root-cause-analysis.md
    │   ├── configuration-audit.md
    │   ├── model-selection-guide.md
    │   ├── remediation-and-validation.md
    │   └── evidence/
    │       ├── README.md
    │       ├── methodology.md
    │       ├── sources.md
    │       ├── manifest.json
    │       └── data/
    └── 2026-11-15-opencode-rate-limit-handling/
        ├── AGENTS.md
        ├── README.md
        └── sources.md
└── providers/
    └── experiential-labs/
        ├── AGENTS.md
        ├── README.md
        ├── refresh-and-verify.md
        └── troubleshooting.md
```

## How to Read These Documents

1. Read the investigation overview for the verified conclusion and corrections to earlier claims.
2. Read the incident report to establish what happened and when.
3. Read the root-cause analysis to understand the mechanisms.
4. Use the configuration audit and model-selection guide for setup decisions.
5. Use the remediation guide to define and validate changes.
6. Consult evidence and sources when checking a specific claim or updating the analysis.
7. Use the Experiential Labs guide for current provider operations; use its linked research for catalog semantics.

## Scope and Freshness

An investigation is a dated record. Model availability, quotas, pricing, supported features, and software behavior
can change. Historical snapshots remain useful evidence even after the live catalog changes.

This documentation follows the existing local-only `docs/` convention. The root repository's public documentation
does not need local evidence paths to explain its own operation.
