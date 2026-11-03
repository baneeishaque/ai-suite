# Traceability — opencode-session-deletion

## Origin

Created to close a documented gap (no library coverage for end-to-end OpenCode
session deletion) surfaced during an OpenCode session analysis and gap-closure
audit. The analysis evidence is local-only and intentionally not linked here.

## Composed Capabilities

| Capability | Owner |
| --- | --- |
| Logger-log discovery and removal | `opencode-session-log-cleanup` |
| Trash-based file removal | `safe-file-cleanup` |
| Active-session resolution | `opencode-current-session-id` |
| Database record deletion | `opencode session delete` CLI |

## Design Decisions

- Default `--dry-run`; destructive behavior requires `--execute`.
- Scratch removal is per-file because new files may appear in the session
  scratch folder after discovery.
- Post-deletion verification re-enumerates and exits `1` on any remainder.
