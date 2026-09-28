# Traceability

## Provenance

- **Created**: 2026-09-25
- **Workflow guide**: [PR-review workflow guide](../../../../../docs/pr-review-workflow-guide.md)
- **Author**: AI Agent (opencode)
- **Design decisions (Phase 0):** local Laya backend, auto-execute on MERGE (`--execute`),
  stricter thresholds 0.9 / 0.5.

## References

- `scripts/classify-pr.py`, `scripts/laya-server.bash`, `scripts/fixtures/` — shipped artifacts
- [`SKILL.md`](SKILL.md) — operational SSOT
- [`CHANGELOG.md`](CHANGELOG.md) — release history
- [`skill-factory`](../../../skill-factory/SKILL.md) — skill creation protocol
- [`skill-library-domain-grouping`](../../../general/skill-library-domain-grouping/SKILL.md) — taxonomy placement (`github/repo/`)
- [`opencode-jsonc-util`](../../../opencode-jsonc-util/SKILL.md) — JSONC provider base-URL resolution
- `docs/pr-review-workflow-guide.md` — workflow SSOT this skill integrates with (Stage 6)
