# Git Personal Content Extraction — AGENTS Bridge

Active SSOT: [SKILL.md](./SKILL.md)

## When this skill applies

- A single team-facing branch (e.g., `<user>-<ticket-id>`) has accumulated
  mixed commits — team-functional work alongside personal artifacts (build
  tweaks, IDE launches, personal docs, skill drafts).
- You want to PURIFY the team branch IN PLACE (keep it alive, integration sees
  only team-relevant work) and PRESERVE every personal commit on a long-lived
  `personal/sandbox` branch in original chronological position.
- The work is too large for a single rebase — execute in rounds.

## When to defer

- A parallel sibling branch exists (e.g., `<team>-ai_demo`) and you want to
  DELETE it after fanning content out → use
  [`git-parallel-branch-decommission`](../git-parallel-branch-decommission/SKILL.md).
- Only one round / one commit to extract → use
  [`git-commit-edit`](../git-commit-edit/SKILL.md) + manual sandbox cherry-pick.
- Generic history reconstruction without the team / personal split semantics →
  use [`git-history-refinement`](../git-history-refinement/SKILL.md).

See [SKILL.md](./SKILL.md) for the full 9-phase protocol.
