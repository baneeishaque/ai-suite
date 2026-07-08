# Git Branch Promotion — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware agent runtimes that auto-load `AGENTS.md` by filename convention. The operational SSOT lives in [`SKILL.md`](SKILL.md). This file is intentionally non-actionable — read `SKILL.md` before executing any promotion step. The skill audits cherry-pick equivalence between two branches, cherry-picks unique commits, verifies tree parity, and executes an authorized force-push promotion with full backup and rollback support.

The skill is a post-processing composer that runs after any history rewriter (bulk reword, single reword, history refinement, feature-branch atomic commit) has produced a parallel branch and before that branch displaces the canonical branch on the remote. It handles the full pipeline: audit, cherry-pick reconciliation, tree-parity verification, promotion, cleanup, and submodule pointer management.

## When This Skill Applies

- A parallel or refined branch (e.g., `master-2` produced by a bulk reword, history refinement, or atomic-commit workflow) is ready to replace the canonical branch on `origin` and the two branches have diverged.
- A reword/rebase operation has produced a side branch whose patch-id equivalents on the canonical side must be audited using `git log --cherry-pick` before the branch can be promoted.
- Cherry-pick reconciliation is needed: commits unique to the canonical side must be cherry-picked onto the refined branch in chronological order before promotion, with each pick inspected individually.
- A force-push (`--force-with-lease`) of the canonical branch is required, and the workflow demands local and remote backup, tree-parity verification (`git diff --stat` empty + commit-count parity), and explicit user authorization gates at every destructive step.
- Cleanup of the refined branch alias and promotion backup is needed after successful promotion, with user authorization required before deletion of rollback artifacts.
- The promotion involves a submodule whose parent repository pointer must be bumped, and whose historical pointers may need repair if the submodule history was rewritten.
- The canonical branch has advanced on the remote during the promotion workflow (stale info), requiring a re-fetch, re-audit, and re-cherry-pick cycle before retrying the force-push.

Do NOT use this skill when the refined branch contains unique content that must be fanned out across multiple branches (use `git-parallel-branch-decommission` instead), or when the promotion is a simple fast-forward with no cherry-pick reconciliation needed (standard `git push` suffices).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure. The skill executes in three phases: Phase 1 audits cherry-pick equivalence via `git log --cherry-pick`, producing a commit count summary for user decision; Phase 2 backs up both branches, cherry-picks canonical-only commits in chronological order (each inspected individually), and verifies tree parity (empty diff, equal commit count, zero left-only); Phase 3 promotes via `git reset --hard` + `git push --force-with-lease` under explicit authorization, followed by optional cleanup. Submodule pointer bump and historical pointer repair (§7) must be handled separately. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`git-divergence-audit`](../git-divergence-audit/SKILL.md) — deep categorization of canonical-only commits when §2.3 is invoked; produces a Commit Action Mapping (CAM) table for deciding which commits to cherry-pick versus drop
- [`git-commit-edit`](../git-commit-edit/SKILL.md) — base of the commit-rewrite stack; defines the push-authorization gate that this skill mirrors in §5
- [`git-commit-message-reword`](../git-commit-message-reword/SKILL.md) — upstream rewriter that commonly produces the refined branch consumed by this skill; consult for single-commit reword cases
- [`git-commit-message-bulk-reword`](../git-commit-message-bulk-reword/SKILL.md) — range rewriter that produced the `master-2` branch in the originating session; consult for bulk reword scenarios requiring promotion
- [`git-history-refinement`](../git-history-refinement/SKILL.md) — upstream rewriter (split/reorder) that produces a refined branch for promotion; coordinates with this skill for post-refinement promotion
- [`git-feature-branch-atomic-commit`](../git-feature-branch-atomic-commit/SKILL.md) — upstream per-commit branch workflow; consult before promoting to ensure each branch's PR has merged or is intentionally being fast-forwarded
- [`git-dependent-branch-restack-cascade`](../git-dependent-branch-restack-cascade/SKILL.md) — downstream cascade for restacking dependent branches (diagnostics, opt-in instrumentation, personal sandbox) rooted on the pre-promotion canonical tip
- [`git-absorbed-branch-decommission`](../git-absorbed-branch-decommission/SKILL.md) — downstream cleanup of the refined branch after promotion is complete; safely deletes the absorbed branch with verified audit trail
- [`git-parallel-branch-decommission`](../git-parallel-branch-decommission/SKILL.md) — alternative when the parallel branch's commits need fan-out across multiple destinations (canonical + opt-in + personal sandbox) rather than single-branch promotion
- [`git-github-auth-fallback`](../git-github-auth-fallback/SKILL.md) — auth-resolution fallback when `git push --force-with-lease` fails with credential errors; MUST be invoked before retrying a failed force-push
- [`git-submodule-pointer-repair`](../git-submodule-pointer-repair/SKILL.md) — historical pointer repair for parent repos when the promoted submodule had rewritten history; required when canonical-side history was rewritten
- [`terminal-fallback-via-vscode-tasks`](../terminal-fallback-via-vscode-tasks/SKILL.md) — fallback routing for git commands when direct-shell tool (`run_in_terminal`) is unavailable; cited in §1.6 Environment requirements
- [`git-cross-ref-file-parity`](../git-cross-ref-file-parity/SKILL.md) — file-level cross-reference verification between branches; useful when the tree-parity check in §4 reveals file-count discrepancies that need deeper investigation
- [`skill-cross-reference-audit`](../general/skill-cross-reference-audit/SKILL.md) — automated audit for skill graph issues in the library; run after creating or modifying this skill to verify cross-reference integrity
