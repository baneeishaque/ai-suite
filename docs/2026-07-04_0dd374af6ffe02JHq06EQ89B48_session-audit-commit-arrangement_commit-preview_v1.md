# Arranged Commits Preview — Master Plan

**Branch**: `main` | **Scope**: sessions 3,5–23 per session audit report

**Total commits**: 16 across 4 batches (≤5 per batch §2g)

**Cross-reference management** (§2f.1): Each SKILL.md staged via
`stage-file-excluding-lines.py` to defer forward cross-ref lines to
uncommitted skills. Back-refs to already-committed skills land in full.
Deferred lines are committed when the target skill commits and `git add`
picks up the working-tree delta.

---

## Execution Plan

### Batch 1 — OpenCode Infrastructure (4 commits)

| # | Message | Files | Deferrals |
|---|---|---|---|
| 1 | `feat(skill): add opencode-jsonc-util base skill` | `opencode-jsonc-util/{AGENTS.md,SKILL.md,scripts/read-jsonc.py}` + `opencode-config-preserve/SKILL.md` (+1) + `opencode-google-gemini-config/SKILL.md` (+1) + `opencode-provider-persistence-config/SKILL.md` (+1) + `mcp-cross-tool-config-sync/SKILL.md` (+1) | None |
| 2 | `feat(skill): add opencode-remote-mcp-setup skill` | `opencode-remote-mcp-setup/{AGENTS.md,SKILL.md,scripts/validate-opencode-mcp.py}` | None |
| 3 | `feat(mcp): add remote MCP support and OpenCode generators` | `mcp-management/SKILL.md` + `mcp-cross-tool-config-sync/{SKILL.md,scripts/generate-configs.py}` + `mcp-management/scripts/test-pipe.py` | — |
| 4 | `feat(skill): add opencode-permission-config skill` | `opencode-permission-config/{SKILL.md,scripts/verify-permission-pattern.py}` | — |

### Batch 2 — Session Base Extractors (5 commits)

| # | Message | Defer (forward refs) | Keep (back refs) |
|---|---|---|---|
| 5 | `feat(skill): add opencode-session-write-extractor` | file-recovery, session-full-change, edit-extractor, diff-extractor, bash-write-extractor | — |
| 6 | `feat(skill): add opencode-session-edit-extractor` | edit-application, session-full-change | C5 (write-extractor) |
| 7 | `feat(skill): add opencode-session-bash-block-extractor` | bash-file-ops, session-file-ops, session-full-change | — |
| 8 | `feat(skill): add opencode-session-bash-write-extractor` | file-recovery, session-full-change | C5–C7 |
| 9 | `feat(skill): add opencode-session-diff-extractor` | agents-md-recovery, session-full-change | — |

### Batch 3 — Composers Level 1 (5 commits)

| # | Message | Defer (forward refs) | Keep (back refs) |
|---|---|---|---|
| 10 | `feat(skill): add opencode-session-bash-file-ops-classifier` | session-file-ops, session-full-change | C7 (bash-block) |
| 11 | `feat(skill): add session-file-ops-audit` | session-full-change, batch-orchestrator | C7, C10 |
| 12 | `feat(skill): add file-recovery-from-session` | edit-application, session-full-change | C5, C8 |
| 13 | `feat(skill): add edit-application-from-session` | session-full-change, batch-orchestrator | C6, C12 |
| 14 | `feat(skill): add agents-md-recovery-from-session` | — | C9 |

### Batch 4 — Composers Level 2 (2 commits)

| # | Message | Defer | Keep |
|---|---|---|---|
| 15 | `feat(skill): add session-full-change-audit` | batch-orchestrator | C5–C14 |
| 16 | `feat(skill): add session-audit-batch-orchestrator` | — | C5–C15 |

---

## AGENTS.md Hunk Strategy

| Hunk | Rows | Strategy |
|---|---|---|
| Hunk 8 | opencode-jsonc-util | Staged in C1 via `agents-md-stage-row.py` |
| Hunk 9 | opencode-remote-mcp-setup | Staged in C2 via `agents-md-stage-row.py` |
| Hunk 10 | C5 + C6 + C7 + C8 + C9 + C10 (6 rows) | One row per commit via `--mode staged`, reading previous HEAD |
| Hunk 11 | C11 + C15 + C16 | C11 row in Batch 3; C15 + C16 rows in Batch 4 |
| Hunk 4 (partial) | file-recovery, edit-application, agents-md-recovery | Via `stage-file-excluding-lines.py` to exclude fnmatch row |

---

## Verification Plan (per batch)

1. `git status` — confirm only intended files staged
2. `git diff --cached --stat` — confirm file count and magnitude
3. `git diff --cached AGENTS.md` — confirm only expected new row(s)
4. `git diff --cached <skill>/SKILL.md` — confirm no deferred lines
5. `git log --oneline -3` after each — confirm message format
