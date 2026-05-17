# AGENTS.md — git-parallel-branch-decommission

Passive context bridge. The active SSOT is [SKILL.md](SKILL.md).

## Purpose

When a parallel feature branch (e.g., `<canonical>-ai_demo`) has accumulated
commits that mix functional code, opt-in diagnostics, and personal-only
documentation, this skill decomposes those commits across the correct
destinations — canonical team branch, opt-in team branch, personal sandbox —
with mixed commits split per file, then deletes the parallel branch.

## When tools should consult this skill

- User asks to clean up, retire, or decommission a long-lived parallel /
  sibling / spike branch without losing salvageable content.
- A divergence audit reveals commits on a parallel branch that fall into
  multiple content categories.
- A mixed commit must be split such that different file slices land on
  different destination branches.

## When NOT to consult this skill

- Single-destination promotion of a refined branch → use
  [git-branch-promotion](../git-branch-promotion/SKILL.md).
- Re-ordering commits on a single branch → use
  [git-rebase-standardization](../git-rebase-standardization/SKILL.md) or
  [git-history-refinement](../git-history-refinement/SKILL.md).

Refer to [SKILL.md](SKILL.md) for the full operational protocol, the
classification matrix, the per-destination cherry-pick mechanics, the
sandbox-rebuild fallback, and the per-push authorization gates.
