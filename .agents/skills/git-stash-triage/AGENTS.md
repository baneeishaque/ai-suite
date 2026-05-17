# AGENTS.md — git-stash-triage

This skill governs all work performed within this folder.

When operating in this directory, the agent MUST:

1. Treat [SKILL.md](SKILL.md) as the Single Source of Truth (SSOT) for
   triage protocol, classification rubric, and disposition mechanics.
2. Apply the hang-free inspection pattern (Phase 1) for every stash
   inspection — no `git stash show -p` without `--no-pager` and dump-to-file.
3. Require explicit user authorization for every destructive step
   (`stash drop`, `stash clear`).
4. Delegate to [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
   for commit construction, and to
   [`git-personal-sandbox-remote`](../git-personal-sandbox-remote/SKILL.md)
   for Bucket C dispositions — never duplicate their logic here.
