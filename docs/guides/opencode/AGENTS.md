# OpenCode Documentation — Agent Contract

## Purpose

Own local, human-readable OpenCode setup guidance and dated investigations in this directory.

## Ownership

- `README.md` is the human entry point and investigation index.
- `investigations/` contains dated case folders with findings, recommendations, and supporting evidence.
- Runtime configuration, plugins, and skill implementations retain their existing source owners.

## Local Contracts

- Follow the repository-root DOX contract and every nearer contract below this directory.
- This directory inherits the repository's local-only documentation convention.
- Use lowercase kebab-case names, with `README.md` and `AGENTS.md` as conventional exceptions.
- Name an investigation `YYYY-MM-DD-descriptive-topic`; keep session identifiers in evidence metadata.
- Distinguish incident observations, source-derived explanations, current catalog snapshots, and recommendations.
- Keep recommendations separate from implementation status. Documentation does not establish that a fix was applied.
- Link related documents relatively. Put external citations and their verification scope in a source register.

## Work Guidance

- Write for a reader unfamiliar with model APIs, tokens, provider quotas, and agent tools.
- Preserve important numbers, provider-qualified model IDs, error wording, and version qualifiers.
- Keep each finding's detailed explanation in one owning document; use summaries and links elsewhere.
- Preserve dated evidence when adding a later investigation or a post-remediation validation result.

## Verification

- Run the repository Markdown lint pipeline with the standalone `markdownlint-cli2` binary from the repository root.
- Check relative links and review code fences, tables, and reading order after automatic formatting.

## Child DOX Index

- [`investigations/2026-11-04-model-behavior/AGENTS.md`](investigations/2026-11-04-model-behavior/AGENTS.md)
  owns the Qwen, NVIDIA, and Cohere incident, configuration snapshot, compatibility data, and remediation guidance.
- [`investigations/2026-11-15-opencode-rate-limit-handling/AGENTS.md`](investigations/2026-11-15-opencode-rate-limit-handling/AGENTS.md)
  owns the Experiential Labs free-core rate-limit incident, OpenCode retry mechanics, configuration audit, and
  OmniRoute failover options.
- [`providers/experiential-labs/AGENTS.md`](providers/experiential-labs/AGENTS.md)
  owns the current Experiential Labs refresh, free-only visibility, troubleshooting, and rollback procedure.
