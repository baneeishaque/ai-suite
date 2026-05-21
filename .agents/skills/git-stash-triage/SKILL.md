---
name: git-stash-triage
description: Industrial protocol for classifying, disposing, and (when appropriate) promoting pre-existing Git stashes to atomic commits or personal-sandbox branches — covers hang-free inspection, content-based classification, apply-not-pop verification, and rule-driven disposition.
category: Git & Repository Management
---

# Git Stash Triage Skill (v1)

> **Skill ID:** `git-stash-triage`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

You discover one or more pre-existing entries in `git stash list` — created in
a prior session, by another tool, or by yourself before context-switching.
You need a disciplined protocol to:

1. **Inspect** stash contents without hanging the terminal (the pager trap).
2. **Classify** each stash by content into one of four disposition buckets.
3. **Decide** the correct disposition with the user (no auto-destruction).
4. **Execute** the disposition safely (apply-not-pop until verified).
5. **Drop** only after the disposition is materialized and verified.

This skill is the read-then-decide complement to
[`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
§9 (which covers stash-as-shelf during commit reconstruction). This skill
covers stashes you did NOT just create.

## When to Apply

Apply this skill when:

- `git stash list` returns ≥ 1 entry whose origin is unclear or stale.
- A workspace switch / repo audit / pre-rebase check surfaces stashes that
  must be disposed of (not silently carried forward).
- Restoring an old WIP and promoting it to a real commit / branch is on the
  table.

Do NOT apply when:

- You just created the stash 5 seconds ago as a temporary shelf during the
  same atomic-commit flow — use the inline `git stash pop` step in
  [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
  §9.
- The stash is known to belong to a feature you are about to resume — just
  `git stash pop` (no triage needed).

## Prerequisites

| Requirement | Minimum |
|---|---|
| VCS | Git 2.x+ |
| Shell | PowerShell 5.1+ or POSIX shell |
| Disposition authority | User authorization required for every destructive step (drop) |

---

## Operational Logic

### Phase 0 — Discover

Stashes are local refs (`refs/stash` plus reflog entries). They never push
with branches, so they are at risk if the clone is lost.

```powershell
git -C <repo-path> stash list
git -C <repo-path> show-ref | Select-String stash       # confirms refs/stash
git -C <repo-path> reflog stash                         # full history including dropped-but-not-pruned
```

If `git stash list` returns no output AND `show-ref | Select-String stash`
also returns no output, there are no stashes — exit the skill.

> [!IMPORTANT]
> If a UI client (VS Code Source Control, IntelliJ, GitKraken) shows
> stashes that `git stash list` does not, check for **secondary worktrees**
> (`git worktree list`) — each worktree has independent stash refs not
> visible from sibling worktrees.

### Phase 1 — Inspect Without Hanging

`git stash show -p` and `git stash show --stat` invoke a pager by default.
In agent-driven terminals (no TTY, or a TTY that the agent cannot interact
with), this **hangs the entire VS Code window** until manually killed.

**Hang-free inspection protocol** — always use `--no-pager` AND dump to a
file:

```powershell
$repo = '<repo-path>'
# --stat first (fast overview)
git -C $repo --no-pager stash show --stat 'stash@{N}' | Out-File "$repo\.stash_stat.txt" -Encoding utf8
# Full patch (may be large)
git -C $repo --no-pager stash show -p    'stash@{N}' | Out-File "$repo\.stash_patch.txt" -Encoding utf8
```

To inspect changes scoped to a single pathspec, use `git diff` between the
stash and its parent (since `git stash show` does not accept pathspec):

```powershell
git -C $repo --no-pager diff 'stash@{N}^' 'stash@{N}' -- '*.launch' `
  | Out-File "$repo\.stash_diff.txt" -Encoding utf8
```

Read the dump files via your editor's `read_file` tool — never paginate in
the terminal.

> [!CAUTION]
> Use `.stash_*.txt` filenames so the dumps are easy to spot in
> `git status` and explicitly delete in Phase 5. NEVER commit these files.
> Add them to `.git/info/exclude` if you intend to inspect repeatedly.

### Phase 2 — Classify

For each stash, classify its content into one of four buckets:

| Bucket | Content fingerprint | Default disposition |
|---|---|---|
| **A — Obsolete/duplicate** | Changes are already merged, already on disk, or superseded by newer commits | DROP (after user confirms) |
| **B — Active feature WIP** | Source-code changes belonging to a known feature branch / Jira ticket | APPLY to that feature branch + atomic commit |
| **C — Personal sandbox** | IDE artifacts, machine-specific configs, build outputs, runtime-location tweaks — not for team origin | APPLY to personal-sandbox branch (delegate to [`git-personal-sandbox-remote`](../git-personal-sandbox-remote/SKILL.md)) |
| **D — Unknown / mixed** | Unclear provenance OR mixes buckets B and C | SPLIT — apply, hunk-stage by classification, multiple atomic commits |

**Classification heuristics:**

- Paths under `.idea/`, `.vscode/`, `.metadata/`, `.settings/`, generated
  Ant `build.xml`, `javaCompiler*.args`, `*.iml`, `Thumbs.db`, IDE
  workspace files → Bucket C.
- Paths under `src/`, `lib/`, `test/`, application source → Bucket B
  (correlate with active feature branch via Jira ID in branch name).
- Both → Bucket D.
- Empty stash, or stash whose diff is now a no-op against current HEAD
  (`git diff <stash> HEAD` is empty) → Bucket A.

### Phase 3 — Decide (User Authorization Gate)

Present the classification to the user as a verdict table:

```text
stash@{0}  Bucket C  46 files +17,155  PDE build artifacts + 2 launch tweaks
stash@{1}  Bucket A  3 files +12       Already-committed README changes
stash@{2}  Bucket B  5 files +130      WIP on SWIT-12345 feature/foo
```

For each row, propose the default disposition and request the user's
explicit `go` / `start` / numbered choice. NEVER auto-execute drops.

> [!WARNING]
> `git stash drop` / `git stash pop` / `git stash clear` are destructive.
> Stashes are NOT in the reflog after being dropped (reflog entries are
> garbage-collected). Lost stash content is unrecoverable without
> `git fsck --lost-found` heroics and may not be found at all. Always
> require explicit user authorization per stash.

### Phase 4 — Execute Disposition

#### 4a — Bucket A (Drop)

> **Stronger pre-drop verification (recommended for safety stashes)**:
> before invoking `stash drop`, run the
> [`git-ref-content-audit`](../git-ref-content-audit/SKILL.md) per-file
> blob-equality audit to prove every file the stash captures (including its
> untracked tree at `<stash>^3`) is byte-identical or knowingly-refined in
> the disposition target (usually `HEAD`). A `✅ FULLY SUPERSEDED` verdict
> upgrades Bucket A from "applied content already in tree" to "every
> stashed blob proven equal at HEAD".
>
> ```bash
> python3 .agents/skills/git-ref-content-audit/scripts/audit-ref-content.py \
>     --repo $repo --stash N --ref-b HEAD --show-diffs
> ```

```powershell
git -C $repo stash drop 'stash@{N}'
git -C $repo stash list   # verify N decremented or list empty
```

#### 4b — Bucket B or C (Apply → Commit → Drop)

ALWAYS use `apply` not `pop`. `pop` drops the stash atomically with the
apply — if the apply succeeds but the subsequent commit fails (conflicts,
hook rejection, mis-staged hunks), you have neither the stash nor the
commit. `apply` preserves the stash until you have verified the commit.

```powershell
# 1. (Pre-flight) Make sure the working tree is clean
git -C $repo status --short

# 2. (Optional) Switch to or create the destination branch
git -C $repo checkout <feature-branch>            # Bucket B
# OR
git -C $repo checkout -b personal/<purpose>       # Bucket C — see git-personal-sandbox-remote skill

# 3. Apply (NOT pop)
git -C $repo stash apply 'stash@{N}'

# 4. Inspect the working tree against the planned classification
git -C $repo status --short
git -C $repo diff --stat

# 5. Stage and commit atomically per git-atomic-commit-construction skill
git -C $repo add <paths>
git -C $repo commit -F <message-file>             # see SSOT mandate below

# 6. Verify the commit
git -C $repo log -1 --format='%H %s'
git -C $repo diff HEAD~1 HEAD --stat

# 7. ONLY after the commit is verified, drop the stash
git -C $repo stash drop 'stash@{N}'
```

> [!IMPORTANT]
> **Commit message authoring** — use the BOM-free, variable-expansion-safe
> pattern when authoring the message via PowerShell:
>
> ```powershell
> $msg = @'
> chore(scope): subject line
>
> Body paragraph...
> Use ${var} forms — single-quoted here-string PREVENTS expansion.
> '@
> $utf8NoBom = [Text.UTF8Encoding]::new($false)
> [IO.File]::WriteAllText("$repo\.git\COMMIT_EDITMSG_NEW", $msg, $utf8NoBom)
> ```
>
> NEVER use `Out-File -Encoding utf8` (writes BOM, leaks into commit subject
> as `∩╗┐` glyphs). NEVER use double-quoted here-strings (`@"..."@`) — they
> expand `$variable` and `${variable}` references mid-message, corrupting
> sentences like `location=${workspace_loc}/...`.

#### 4c — Bucket D (Split — Apply → Hunk-Stage → Multiple Commits)

Same as 4b but instead of staging whole files, use interactive add to
separate hunks per classification bucket:

```powershell
git -C $repo stash apply 'stash@{N}'
git -C $repo add -p              # hunk-by-hunk: stage only Bucket B hunks
git -C $repo commit -F <feature-msg>
git -C $repo add -p              # second pass: stage only Bucket C hunks
git -C $repo commit -F <sandbox-msg>
git -C $repo status --short      # MUST be clean
git -C $repo stash drop 'stash@{N}'
```

Each commit MUST follow
[`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md).

### Phase 5 — Clean Up Inspection Artifacts

```powershell
Remove-Item "$repo\.stash_stat.txt", "$repo\.stash_patch.txt", "$repo\.stash_diff.txt" `
  -ErrorAction SilentlyContinue
git -C $repo status --short   # MUST be clean
```

---

## SSOT Compliance

This skill consumes — never duplicates — the following authoritative rules:

- **Commit construction** — every commit produced in Phase 4 MUST follow
  [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
  for atomicity, staging discipline, and message format.
- **Commit messages** — Conventional Commits subject + body per the
  project's commit-message rules (resolved via
  [`git-commit-message-reword`](../git-commit-message-reword/SKILL.md)
  when retrofitting).
- **Personal sandbox routing** — Bucket C dispositions MUST delegate
  branch/remote setup to
  [`git-personal-sandbox-remote`](../git-personal-sandbox-remote/SKILL.md)
  rather than inventing a parallel scheme.
- **Push authorization** — when the disposition includes a push, the
  global "agent MUST NEVER `git push` automatically" rule from
  [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
  applies — explicit user `start` required.

---

## Anti-Patterns

| Anti-pattern | Why it's wrong | Correct alternative |
|---|---|---|
| `git stash show -p stash@{0}` in agent terminal without `--no-pager` | Hangs VS Code (pager blocks on TTY) | Phase 1 dump-to-file pattern |
| `git stash pop` followed by attempt to commit | If commit fails after pop, stash is gone | `apply` + verify + `drop` (Phase 4b) |
| Auto-drop "obviously obsolete" stash without user confirmation | Stash content is unrecoverable after drop | Phase 3 user gate |
| `Out-File -Encoding utf8` for commit message | Writes UTF-8 BOM → subject shows `∩╗┐` glyph | `[IO.File]::WriteAllText` with `UTF8Encoding($false)` |
| Double-quoted here-string (`@"..."@`) for commit message body | PowerShell expands `$var` / `${var}` mid-message | Single-quoted (`@'...'@`) here-string |
| `git stash show -p stash@{0} -- '*.launch'` | `stash show -p` does NOT accept pathspec — fails with "Too many revisions" | Use `git diff 'stash@{N}^' 'stash@{N}' -- '*.launch'` instead |

---

## Traceability

- Initial design driven by a live-session episode where an unaudited stash
  containing 46 PDE artifacts + 2 personal launch tweaks was discovered,
  classified as Bucket C (Personal Sandbox), and promoted to
  `personal/sandbox` on a freshly-created personal remote via the
  [`git-personal-sandbox-remote`](../git-personal-sandbox-remote/SKILL.md)
  skill — surfaced the hang-prevention, apply-not-pop, BOM-free,
  expansion-safe, and `stash show -p` pathspec-limitation rules captured
  here.

---

<!-- Generated by the Skill Factory (skill-factory v1) -->
