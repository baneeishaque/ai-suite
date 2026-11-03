# opencode-session-deletion — Agent Contract

## Purpose

Owns the end-to-end deletion of an OpenCode session: database record,
logger-plugin logs, scratch artifacts, and planning artifacts, with discovery,
explicit confirmation, per-file removal, and verification.

## Ownership

- `SKILL.md` — the skill contract.
- `scripts/delete-session.py` — the deterministic orchestrator.
- `CHANGELOG.md` / `TRACEABILITY.md` — metadata companions.

## Local Contracts

- Deletion requires a passing `skill-library-gap-closure` run on the target
  session (zero open gaps); `--execute` also requires
  `--gap-closure-cleared`, otherwise it exits `2`.
- Destructive removal requires `--execute` plus explicit user confirmation;
  the default mode is `--dry-run`.
- Scratch files are removed individually, never folder-wide.
- Composed scripts (`opencode-session-log-cleanup`, `safe-file-cleanup`) are
  required in execute mode; a missing one is exit `2`.
- No `rm`; `safe-file-cleanup` uses the system trash.
- When the plan was authored by another session, verify its content markers
  against the current working tree (case-insensitive by default) before
  `--execute`; STOP if the plan has no marker baseline or any marker is
  missing. Recover a retired plan from the OS Trash by exact filename.
- An explicit `execute <plan>` instruction that names a deletion-only plan
  satisfies the confirmation gate; no second prompt is issued. Any other
  instruction requires fresh confirmation.

## Work Guidance

- Close the target session's TUI before deleting logs, or the logger may
  recreate them.
- Re-verify after ~10 seconds and repeat if logs reappear.
- Leave unexpected/new scratch files untouched and report them.
- Reuse related authoring-session logs from the Trash destination used by
  `opencode-session-log-cleanup` when the session record is already gone.

## Verification

- `python3 scripts/delete-session.py --help`
- Dry-run against a non-existent fake ID exits `1` with no deletion.
- `markdownlint-cli2 SKILL.md AGENTS.md CHANGELOG.md TRACEABILITY.md`

## Child DOX Index

None.
