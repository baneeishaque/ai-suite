# AGENTS.md — git-personal-sandbox-restack

Passive context bridge. The active SSOT is [SKILL.md](SKILL.md).

## Purpose

When a personal sandbox branch needs to be re-anchored onto the current tip of
a moving team / feature / ticket branch (without losing personal content),
this skill orchestrates the `rebase --onto`, resolves the typical
modify-vs-delete (DU) conflicts, runs a six-axis content-equality audit
(patch-id / files-touched / file-set / per-file bytes / tree / tip-byte), and
gates the `--force-with-lease` push behind explicit user authorization.

## When tools should consult this skill

- A personal sandbox branch needs to be re-anchored onto the current tip of
  the active feature / ticket branch.
- A six-axis equality audit is required between the pre-rebase and
  post-rebase tips before force-pushing the sandbox.
- A modify-vs-delete (DU) conflict needs to be resolved during a rebase
  with `git add` / `git rm` discipline.

## When NOT to consult this skill

- The sandbox just needs a vanilla `git rebase` against `master` / `main`
  without an audit → run rebase directly.
- The sandbox contains team work that hasn't been promoted yet → use
  [git-branch-promotion](../git-branch-promotion/SKILL.md) first.
- The parallel branch the sandbox sits next to is being decommissioned →
  use [git-parallel-branch-decommission](../git-parallel-branch-decommission/SKILL.md),
  whose Phase 2 rebuild path subsumes the restack.

Refer to [SKILL.md](SKILL.md) for the full operational protocol, the
six-axis audit, the DU conflict recipe, the PowerShell `$pid` pitfall, and
the per-push authorization gate.
