# Traceability

## Provenance

- **Plan**: `docs/2026-09-25_043212a4dffeqaNkrqTtLLDSUc_reviewing-associates-pr_implementation-plan_v5.md`
  (v1–v4 superseded, kept)
- **Session**: `ses_043212a4dffeqaNkrqTtLLDSUc` (`reviewing-associates-pr`), 2026-09-25
- **Author**: AI Agent (opencode)
- **Source conversation**: "Implement Laya/Jev for Auto Merge of PRs" — Phase 0 decisions:
  local Laya backend, auto-execute on MERGE (`--execute`), stricter thresholds 0.9 / 0.5.

## References

- `scripts/classify-pr.py`, `scripts/laya-server.bash`, `scripts/fixtures/` — shipped artifacts
- [`SKILL.md`](SKILL.md) — operational SSOT
- [`CHANGELOG.md`](CHANGELOG.md) — release history
- [`skill-factory`](../../../skill-factory/SKILL.md) — skill creation protocol
- [`skill-library-domain-grouping`](../../../general/skill-library-domain-grouping/SKILL.md) — taxonomy placement (`github/repo/`)
- [`opencode-jsonc-util`](../../../opencode-jsonc-util/SKILL.md) — JSONC provider base-URL resolution
- `docs/pr-review-workflow-guide.md` — workflow SSOT this skill integrates with (Stage 6)
