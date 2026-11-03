---
name: opencode-session-deletion
description: Composer — delete an OpenCode session end-to-end (database record, logger logs, scratch artifacts, and planning artifacts) with discovery, explicit confirmation, per-file removal, and verification.
category: OpenCode
---

# opencode-session-deletion (v1)

> **Name:** opencode-session-deletion<br>
> **Description:** Composer — delete an OpenCode session end-to-end (DB
> record, logger logs, scratch artifacts, plan artifacts) with discovery,
> explicit confirmation, per-file removal, and verification.<br>
> **Category:** OpenCode

## Description

Delete an OpenCode session completely. This composer owns the whole
lifecycle: confirm the session exists, inventory its database record, logger
artifacts, scratch files, and planning artifacts, require explicit user
confirmation, delete the database record (`opencode session delete`), remove
the logger logs (delegated), remove scratch files individually (never
folder-wide), optionally retire planning artifacts, and verify that no trace
remains.

## Composition Rationale

This skill is a composer. It does not reimplement log discovery/removal or
trash semantics; it sequences existing capabilities:

1. `opencode session delete <id>` — removes the database record.
2. [`opencode-session-log-cleanup`](../../opencode-session-log-cleanup/SKILL.md) —
   discovers and removes the logger-plugin per-turn logs, top-level session
   files, and transcripts.
3. [`safe-file-cleanup`](../../../general/file/safe-file-cleanup/SKILL.md) —
   trash-based per-file removal for scratch/plan artifacts.
4. [`opencode-current-session-id`](../../opencode-current-session-id/SKILL.md) —
   optional verification of the active session before deletion.

The composer's value-add is the end-to-end order, the per-file scratch
discipline (new files may appear), the TUI-closure/recreation guard, and the
verification gate.

## Related Skills

- [`opencode-session-deletion-plan`](../opencode-session-deletion-plan/SKILL.md) —
  upstream; renders the versioned plan this composer executes.
- [`opencode-session-yaml-tool-call-extractor`](../../opencode-session-yaml-tool-call-extractor/SKILL.md) —
  sibling; parses the same logger YAML logs this composer removes.

## Environment & Dependencies

| Requirement | Version | Notes |
| --- | --- | --- |
| Python | 3.10+ | Stdlib only — no pip dependencies |
| `opencode` CLI | present on `PATH` | Provides `opencode session list` / `delete` |
| `opencode-session-log-cleanup` skill | — | At `../../opencode-session-log-cleanup/` |
| `safe-file-cleanup` skill | — | At `../../../general/file/safe-file-cleanup/` |

## CLI Contract

`scripts/delete-session.py`:

| Argument | Required | Description |
| --- | --- | --- |
| `session_id` | Yes | OpenCode session ID (e.g. `ses_<id>`) |
| `--logs-dir` | No | Logs directory (default: `.opencode/logs`) |
| `--scratch-root` | No | Scratch root (default: `scratch`) |
| `--docs-dir` | No | Docs directory (default: `docs`) |
| `--dry-run` | No | Inventory only (default) |
| `--execute` | No | Perform the deletion |
| `--retire-docs` | No | Also trash matching plan artifacts in `--docs-dir` |
| `--skip-db` | No | Do not call `opencode session delete` |
| `--gap-closure-cleared` | Required with `--execute` | Acknowledge that gap-closure ran and zero gaps remain |
| `--json` | No | Emit JSON instead of text |

Exit codes:

- `0` — artifacts found and (in `--execute` mode) removed and verified.
- `1` — no artifacts found, or paths remain after deletion.
- `2` — a composed script is missing or a fatal error occurred.

## Protocol

0. **Gap-closure gate (mandatory).** Run `skill-library-gap-closure` on the
   target session and close every `NOT_DOCUMENTED` / `PARTIAL` gap it reports.
   Deletion is BLOCKED until the latest gap-closure pass reports zero open
   gaps (all gaps are `DOCUMENTED` or closed). Record the pass and its verdict.
1. Accept the target `session_id` (never guess it).

   **Cross-session content-survival guard (mandatory when the plan was
   authored by a different session).** Read the plan's marker list; if the
   plan is already retired, recover it from the OS Trash by exact filename.
   Verify every marker against the CURRENT working tree with the plan's match
   mode (case-insensitive by default; a lowercase literal can false-negative
   `Gap-closure gate` versus `gap-closure gate`). Record `git status --short`
   for every marker file. Dirty files are allowed — only the markers must
   survive. STOP if the plan carries neither a marker list nor an explicit
   `markers: none`, if any marker is missing, or if neither the plan nor
   usable related logs can be recovered from the Trash. Never guess a
   baseline. When related authoring-session logs are needed, reuse the Trash
   destination used by
   [`opencode-session-log-cleanup`](../../opencode-session-log-cleanup/SKILL.md).

2. Run the inventory and present it:

   ```bash
   python3 .agents/skills/opencode/session/opencode-session-deletion/scripts/delete-session.py <id> --dry-run
   ```

3. Require explicit user confirmation. An explicit instruction that names the
   plan and whose sole action is deletion (for example `execute <plan-path>`)
   satisfies this gate: the plan's mandatory gap-closure gate is always
   present and records the approved deletion scope, so no second `yes` /
   `delete` prompt is issued. Any other instruction requires a fresh
   confirmation.
4. Ensure the target session's TUI is closed; otherwise the logger may
   recreate logs after cleanup.
5. Execute, passing the gap-closure clearance flag:

   ```bash
   python3 .agents/skills/opencode/session/opencode-session-deletion/scripts/delete-session.py <id> --execute --gap-closure-cleared
   ```

   `--execute` without `--gap-closure-cleared` exits `2` (gate not cleared).
6. Re-verify after ~10 seconds; if logs reappear, close the TUI and repeat.
7. Report what was removed and what was left untouched.

## Edge Cases

- **Open gaps**: deletion is blocked until `skill-library-gap-closure`
  reports zero open gaps; `--execute` requires `--gap-closure-cleared`.
- **Session not found in DB**: continue with log/scratch cleanup only.
- **No artifacts at all**: exit `1`; nothing deleted.
- **Target TUI still open**: logs may reappear; close it and repeat the
  verification step.
- **Missing marker baseline**: if the plan has neither a marker list nor an
  explicit `markers: none`, STOP and re-plan; never infer markers from memory.
- **Retired plan**: recover it from the OS Trash by exact filename; related
  authoring-session logs may be reused from the Trash destination used by
  [`opencode-session-log-cleanup`](../../opencode-session-log-cleanup/SKILL.md).
- **Dirty working tree**: allowed; only the declared markers must survive.
- **New scratch files**: the composer only removes the files it discovered
  during this run; new or unexpected files are left untouched and reported.
- **Partial removal**: the composer re-enumerates and exits `1` if anything
  remains.
- **`opencode` CLI missing**: warn and skip the DB step; logs/scratch still
  proceed (use `--skip-db` explicitly in automation).
- **Docs retirement**: only files matching the session ID are considered, and
  only with `--retire-docs`.

## Composition by Higher-Level Skills

None — this skill is a leaf composer in the opencode/session group.

## Traceability

See [TRACEABILITY.md](TRACEABILITY.md).

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
