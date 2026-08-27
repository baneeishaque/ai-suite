# [Code review and merge for Jira tickets via Teams] (v17 - Consolidated)

## Rule Compliance Reference

- [`ai-agent-planning-rules.md`](../ai-agent-rules/ai-agent-planning-rules.md) — §1 Goal Description & Versioning, §2 Core Planning Directive, §7 Industrial Mandates, §8 Temporal Hygiene, §9 Plan Versioning (§7.1 CAM), §10 Task Sync, §11 Q&A, §12 Phase Gating
- [`planning-artifact-naming`](../.agents/skills/general/planning/planning-artifact-naming/SKILL.md) — §1 Formula, §1.3 `ses_` omission, §2 Registered Types
- [`planning-artifact-lifecycle`](../.agents/skills/general/planning/planning-artifact-lifecycle/SKILL.md) — Steps 1-5
- [`versioned-artifact-superset-build`](../.agents/skills/general/planning/versioned-artifact-superset-build/SKILL.md) — verbatim-superset construction (v1→v3); v4 is straight-forward consolidation of v3 final state
- [`planning-version-coverage-audit`](../.agents/skills/general/planning/planning-version-coverage-audit/SKILL.md) — FULL gate
- [`scratch-artifact-naming`](../.agents/skills/general/file/scratch-artifact-naming/SKILL.md) — `resolve-scratch-path.py` (scratch v1)
- [`repo-scratch-output-capture`](../.agents/skills/repo-scratch-output-capture/SKILL.md) — `scratch/` gitignored
- Custom docs helper `resolve-docs-path.py` — `docs/<session>/<date>/<purpose>/<artifact>_v<ver>_<time>.<ext>` (ms+timezone IST) under `.agents/skills/general/file/scratch-artifact-naming/scripts/`

## User Questions & Answers

| Question | Answer |
| --- | --- |
| Q1 Teams source — which chat, card vs link, browser automation? | A1 Group chat `Daily Standup: Frontend Development Team`. Tickets usually Jira Adaptive Cards via Teams Jira app, sometimes plain `https://*.atlassian.net/browse/XXX-NNN` links. Need browser automation. Web authenticated in Chrome. |
| Q2 Jira scope — epic & tickets? | A2 Epic & fields identified via `acli` after extracting ticket numbers from Teams. `acli` already authenticated; site & tickets derived from Teams. |
| Q3 PR mapping — where are PRs? | A3 PRs commented or in description as `PR1` (single PR deferred if >1). Single PR must be to `main`, branch contains ticket key, PR title & description must contain key (skill `gh-pr-edit`). |
| Q4 Merge policy? | A4 Rebase merge (`gh pr merge --rebase --delete-branch`), no CI checks now, user approves merge after review. |
| Q5 Failure path? | A5 `REQUEST_CHANGES` on PR is enough; Jira @mention comment. Transition/Teams notify later. Tickets handled one by one. |
| Q6 Bulk vs per-ticket? | A6 Per ticket loop. |
| Additional — ticket details correction? | Must be corrected before any operations per ticket, token budget unlimited, no tests now but must report existence everywhere (origin, personal, worktree, branches, stash). Fresh content via `gh`/GitHub API; local only for lint/build/test later. |
| Window clarification? | Last 7 days including today, times IST. |
| Gate 1 confirmation? | Confirm Jira ticket list before processing — both chat reply and file. |
| Gate 2 granularity? | Jira corrections/hierarchy handled after getting each ticket, before any processing for that ticket — explicitly confirm no actions remaining per ticket before next step. |
| Personal remote? | Repo is `acers-web` submodule under `lab-data/oleovista-acers`; contains `personal` sandbox remote per `git-personal-sandbox-remote` skill — must be searched in test sweep. Superproject not in picture. |
| Multi-PR? | Skip multi-PR tickets for now. |
| Scratch vs Docs organisation? | Scratch = ephemeral runtime captures under `scratch/` v1; Docs = durable planning artifacts under `docs/<session>/<date>/<purpose>/` with ms+timezone. |
| Markdown lint? | Use `markdownlint-cli2` direct at `/opt/homebrew/bin/markdownlint-cli2`, not `npx`. |

## Goal

Code review (then rebase merge if approved) Jira tickets posted in Microsoft Teams group chat `Daily Standup: Frontend Development Team`, targeting repo `lab-data/oleovista-acers/acers-web` (submodule, independent origin + personal remote), with per-ticket loop, dual confirmation gates, 7-day IST window, exhaustive test-existence audit including `personal` remote.

## Architecture

```text
Teams (Chrome) ──browser injection──► teams-extract (7-day IST filter)
                                    │
                              Gate 1 (both channels: file + chat)
                                    │
For each KEY in confirmed order:
  acli view --fields '*all' (+ hierarchy) ──► jira-view
  propose corrections ──► Gate 2 (per-ticket: no actions remaining?)
  Jira comment/description ADF inlineCard parse ──► PR correlation
  0 PR → @assignee Jira comment → next KEY
  >1 PR → MULTI_PR_DEFERRED → next KEY
  1 PR → gh api files/diff ──► fresh PR content (no local checkout)
         5-source test sweep (worktree, branches, origin, personal, stash) + graph oracles
         graph review (code-review-graph + gitnexus + repowise)
         gh pr review --request-changes
         Gate 3 (user approves merge) → gh pr merge --rebase --delete-branch
```

### Repo & Graph Context

- Repo root: `/Users/dk/lab-data/oleovista-acers/acers-web` — owns `src/`, `scratch/`, own `.git`, own graphs `.code-review-graph/graph.db`, `.gitnexus/`, `graphify-out/` per `acers-web/AGENTS.md:14-15,181-183,235-236`. Superproject `oleovista-acers` not touched.
- Stack: CRA5 React 18.3, TypeScript 4.9, `npm run lint` oxlint, `npx tsc --noEmit`, Jest layers `*.unit.test.*` etc `AGENTS.md:102-140`.
- Personal remote: `personal https://github.com/<user>/acers-web.git` alongside `origin` per `git-personal-sandbox-remote/SKILL.md:282-294`, branches `personal/<purpose>` `SKILL.md:308-314`.

## File Manifest

### Planning Artifacts (durable, nested `docs/` per your corrected organisation)

Via `resolve-docs-path.py` — `docs/<session-id>/<date>/<purpose>/<artifact>_v<version>_<time>.<ext>` where `<time>` is `HH-MM-SS-mmm_TZ` (milliseconds + timezone, IST `Asia/Kolkata`):

| Artifact | Nested Path Example |
| --- | --- |
| Task (live, unversioned) | `docs/fcdce5e0fffe6NwqmmaY0Db0hd/2026-08-24/code-review-and-merge-for-jira-tickets-via-teams/task_12-01-02-517_IST.md` |
| Implementation plan v4 (this file) | `docs/fcdce5e0fffe6NwqmmaY0Db0hd/2026-08-24/code-review-and-merge-for-jira-tickets-via-teams/implementation-plan_v4_12-00-40-641_IST.md` |
| Future `commit-preview`, `walkthrough` | `docs/<session>/<date>/<purpose>/<artifact>_v<ver>_<time>.md` |

Helper:

```bash
python3 .agents/skills/general/file/scratch-artifact-naming/scripts/resolve-docs-path.py \
  --repo <repo-root> --purpose <kebab> --artifact <kebab> --ext <ext> \
  [--version <int>] [--date YYYY-MM-DD] [--timezone Asia/Kolkata]
```

### Runtime Scratch Captures (ephemeral, gitignored, `acers-web/scratch/` — v1)

Via `resolve-scratch-path.py` (`scratch-artifact-naming` skill) — `scratch/<session-id>/<purpose>_<timestamp>` (no ms, no tz):

- `teams-extract_<ts>.json` / `.md` — 7-day IST window, deduplicated keys
- `jira-view_<ts>-<KEY>.json` — `acli jira workitem view --fields '*all'`
- `summary_<ts>.md` — batch accumulator
- `pr-<N>/jira-corrections_<ts>.md` — proposed field/hierarchy edits
- `pr-<N>/pr-meta_<ts>.json` — `gh --repo anushadpk/acers-web pr view <N> --json`
- `pr-<N>/files_<ts>.json` — `gh api repos/anushadpk/acers-web/pulls/<N>/files`
- `pr-<N>/diff_<ts>.diff` — `gh pr diff <N>`
- `pr-<N>/test-sweep_<ts>.md` — 5-source table (personal mandatory)
- `pr-<N>/graph-detect_<ts>.json`, `graph-impact_<ts>.json`, `review_<ts>.md`

```bash
python3 .agents/skills/general/file/scratch-artifact-naming/scripts/resolve-scratch-path.py \
  --repo /Users/dk/lab-data/oleovista-acers/acers-web --purpose teams-extract
# → scratch/fcdce5e0fffe6NwqmmaY0Db0hd/teams-extract_2026-08-24_11-55-15
python3 .agents/skills/general/file/scratch-artifact-naming/scripts/resolve-scratch-path.py \
  --repo /Users/dk/lab-data/oleovista-acers/acers-web --purpose pr-812
# → scratch/fcdce5e0fffe6NwqmmaY0Db0hd/pr-812_2026-08-24_11-55-15 (append .diff/.json)
```

`acers-web/scratch/` is gitignored via `ensure-scratch-gitignored.py`; never committed.

## Detailed Execution Steps

### Step 0 — Preflight

- Verify `acli jira auth status` and `gh auth status --repo anushadpk/acers-web` — both MUST succeed.
- Resolve repo root `acers-web` via `git -C /Users/dk/lab-data/oleovista-acers/acers-web rev-parse --show-toplevel`.
- Ensure `acers-web/scratch/` gitignored.
- Resolve scratch STEM via `resolve-scratch-path.py --repo acers-web --purpose teams-extract` — session `fcdce5e0fffe6NwqmmaY0Db0hd`.

### Step 1 — Teams Ingest (7-day IST)

- Attach Chrome `teams.microsoft.com` (reuse authenticated profile) via `macos-app-control` + `browser-network-interception`.
- Inject `scripts/teams-chat-nav/teams-chat-nav-inject.js:1-16` with `CHAT_NAME="Daily Standup: Frontend Development Team"` — click `[role="treeitem"]` match.
- Loop scroll-up, inject `teams-read-messages-inject.js:1-103` each viewport; collect `{day,time,body,jira}` where `day` is `Today`/`Yesterday`/date separator `^\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)` `teams-read-messages-inject.js:11-13`.
- Post-filter Python: localize to `Asia/Kolkata` `UTC+05:30`, map `Today` → IST today, `Yesterday` → IST today-1, dated separators parse with current IST year; keep only `date >= IST_today -6` inclusive; deduplicate by `KEY` preserving earliest `sender`/`time`; also regex fallback `([A-Z]+-\d+)` and `https://.*\.atlassian\.net/browse/.*` from `body` when adaptive card absent.
- Capture to `scratch/<session>/teams-extract_<ts>.json` `{window:{startIST,endIST,zone:"Asia/Kolkata"}, messages:[], jiraKeys:[]}` and `.md` gate table.

### Gate 1 — Ticket List Confirmation (both channels)

- Render markdown table `| # | KEY | Title | Status | Assignee | FirstSeen IST | Source card/link | Sender |` in `teams-extract_<ts>.md`.
- Present via chat and file; block — no Jira calls until you reply `proceed all` / `proceed AES-x,AES-y` / `exclude AES-z`.

### Step 2 — Per-Ticket Loop (ordered Teams appearance)

For each `KEY` in confirmed order:

#### Step 2a — Jira View & Hierarchy

```bash
acli jira workitem view <KEY> --fields '*all' --json > scratch/<session>/jira-view_<ts>-<KEY>.json
acli jira workitem comment list --key <KEY> --json
acli jira workitem link list --key <KEY> --json
```

- If `parent` / `Epic Link` present — `acli jira workitem view <PARENT> --fields '*all' --json` and optional `python3 .agents/skills/jira-workitem-hierarchy-report/scripts/jira-hierarchy-report.py --jql 'key = <EPIC>'` per `jira-workitem-hierarchy-report/SKILL.md:33-45`.
- Record `scratch/<session>/pr-<N>/jira-corrections_<ts>.md` listing proposed edits (summary, parent, labels) via `acli jira workitem edit --key <KEY> ...` — not executed yet.

#### Gate 2 — Per-Ticket Jira Actions (before any PR work)

- Prompt: `Ticket <KEY> (<summary>) — artifacts jira-view_*.json + jira-corrections_*.md. Confirm no jira ticket actions remaining for <KEY>? (yes / add correction: <instruction>)`.
- Execute any approved corrections, then require explicit `yes` to advance to Step 3.

#### Step 3 — PR Correlation (single-PR strict, multi-PR skip)

- Parse Jira: `comment list --json` + `view description` ADF `inlineCard` nodes `type:inlineCard attrs.url` `jira-inlinecard-comment/SKILL.md:168-175` plus `PR\s*\d+\s*:\s*\[.*pull\/(\d+)\]` and plain `https://github.com/.../pull/\d+`.
- Count distinct PR numbers:

| Count | Action |
| --- | --- |
| 0 | `acli jira workitem comment create --key <KEY> --body "@<assignee> no PR linked for <KEY>. Please add PR1 link; branch must contain <KEY>, PR title/description must contain <KEY>."` `jira-acli-operations/SKILL.md:360-375` → mark `NO_PR`, next KEY |
| 1 | Validate single PR — `gh --repo anushadpk/acers-web pr view <N> --json number,title,body,baseRefName,headRefName,state,url` — check `baseRefName==main`, `headRefName` contains `KEY` case-insensitive, `title`+`body` contains `KEY` per `gh-pr-edit/SKILL.md:32-43`; failures become `REQUEST_CHANGES` reasons. Proceed to Step 4. |
| >1 | Mark `MULTI_PR_DEFERRED`, no review/merge, next KEY |

#### Step 4 — Fresh PR Content + Exhaustive Test Sweep

- Fresh content (no local checkout):

```bash
gh --repo anushadpk/acers-web pr view <N> --json number,title,body,baseRefName,headRefName,state,url,author,additions,deletions,changedFiles > scratch/<session>/pr-<N>/pr-meta_<ts>.json
gh api repos/anushadpk/acers-web/pulls/<N>/files --paginate > scratch/<session>/pr-<N>/files_<ts>.json
gh --repo anushadpk/acers-web pr diff <N> > scratch/<session>/pr-<N>/diff_<ts>.diff
gh api repos/anushadpk/acers-web/pulls/<N>/commits --paginate
```

- Test sweep (5 sources inside `acers-web` only):

| Source | Probe |
| --- | --- |
| Worktree + index | `git -C acers-web status --porcelain`, `diff --name-only`, `ls-files --others --exclude-standard` + `glob **/*test* **/*spec* __tests__` |
| Local branches | `git -C acers-web branch -a --format='%(refname:short)'` then `git ls-tree -r --name-only <branch> -- '*test*' '*spec*'` |
| origin | `git -C acers-web ls-remote --heads origin`, `fetch origin`, `ls-tree remotes/origin/<branch>` |
| personal | `git -C acers-web remote -v` check for `personal` per `git-personal-sandbox-remote/SKILL.md:282-293`; `ls-remote --heads personal`, `fetch personal`, `ls-tree remotes/personal/<branch>` incl. `personal/*` `SKILL.md:308-314` |
| stash | `git -C acers-web stash list`, `stash show -p stash@{n}`, `ls-tree -r stash@{n}^3` |

- Patterns: `**/*.unit.test.*`, `**/*.component.test.*`, `**/*.integration.test.*`, `**/*.system.test.*` per `acers-web/AGENTS.md:113-125` plus `__tests__`, oracles `query_graph_tool pattern=tests_for`, Repowise `get_risk missing_tests`, `get_dead_code`.
- Output `scratch/<session>/pr-<N>/test-sweep_<ts>.md` table `| Expected test | worktree | branches | origin/* | personal/* | stash | Verdict |`.

#### Step 5 — Graph Review (acers-web graphs, unlimited tokens)

- Check freshness `get_minimal_context_tool(task="review PR #<N> <KEY>", repo_root=acers-web)`; if `status:not_ready` rebuild via `code-review-graph_build_or_update_graph_tool(repo_root=acers-web)`.
- Run `detect_changes_tool(base=main, changed_files=from files_*.json, detail_level=standard)`, `get_affected_flows_tool`, `get_impact_radius_tool(max_depth=3)`, `get_review_context_tool(include_source=true)`, `get_surprising_connections_tool`, `query_graph_tool pattern=callers_of/callees_of/tests_for` per `code-review-graph` `AGENTS.md:193-231` + gitnexus `impact` + Repowise `get_change_risk`.
- Pedagogical commit audit `python3 .agents/skills/git-commit-details-audit/scripts/audit.py <headSHA>` `git-commit-details-audit/SKILL.md:30-43`.
- Produce `scratch/<session>/pr-<N>/review_<ts>.md` sections `Meta / What changed / Why matters (flows/hubs) / Test status / Issues by risk / Recommendation`.

#### Step 6 — Submit Review

```bash
gh --repo anushadpk/acers-web pr review <N> --request-changes --body-file scratch/<session>/pr-<N>/review_<ts>.md
# verify
gh --repo anushadpk/acers-web pr view <N> --json reviews,reviewDecision
```

- Optional Jira `@mention`: `acli jira workitem comment create --key <KEY> --body "@<assignee> review posted <PR_URL> — REQUEST_CHANGES (see PR comments)"` `jira-acli-operations/SKILL.md:360-375`.

#### Gate 3 — Merge Approval (per-PR human gate)

- Only on explicit `approve merge <KEY> #<N>`:

```bash
gh --repo anushadpk/acers-web pr view <N> --json mergeable,state,baseRefName
gh --repo anushadpk/acers-web pr merge <N> --rebase --delete-branch
gh --repo anushadpk/acers-web pr view <N> --json state,mergedAt
git -C acers-web ls-remote --heads origin <branch>  # should be gone
```

- No CI wait (none configured). Transition/Teams notify deferred.

#### Step 7 — Closeout

- Append row to `scratch/<session>/summary_<ts>.md` `| Order | KEY | Sender IST | PR | Branch | Base==main | Title/Body KEY | Test exists | Review | Merge |`.
- Continue next KEY.

## Verification

- `markdownlint-cli2 --fix` direct at `/opt/homebrew/bin/markdownlint-cli2` (not `npx`) — `docs/` planning artifacts + `scratch/` runtime captures where needed.
- `python3 .agents/skills/general/skill-cross-reference-audit/scripts/audit-cross-refs.py` — 0 dangles
- `acli jira auth status`, `gh auth status --repo anushadpk/acers-web` — verde before execution
- Post-merge `gh pr view --json state` == `MERGED`, `ls-remote --heads origin <branch>` empty

## Risks & Mitigations

- Teams card not rendered — fallback plain-link regex may capture multiple keys; deduplicate preserving sender context.
- Jira ADF `inlineCard` only in comments/description — must parse both ADF layers; `acli search --fields` misses custom fields, use `view --fields '*all'`.
- `gh pr merge --rebase` fails if `mergeable==CONFLICTING` — report, no force, next ticket proceeds.
- Chrome automation fragility — keep headful `Chrome --remote-debugging-port` fallback documented in `teams-chat-nav` vs Playwright `chromium.launch`.
- IDE renderer freeze — avoid `grep -r` with file paths, redirect large outputs to `scratch/<session>/pr-<N>/` per `ide-renderer-freeze-prevention` + `repo-scratch-output-capture`.

## Change History

| Timestamp | Summary of Changes | Rationale |
| --- | --- | --- |
| 2026-08-24 | v1 baseline — Teams 7-day IST ingest, dual gates, acers-web submodule-only, 5-source test sweep including personal. | Initial build-mode plan per your Teams/Jira/PR workflow. |
| 2026-08-24 | v1 → v2: Introduced `docs/<session>/<date>/<purpose>/` for runtime captures via `resolve-docs-path.py` (ms+timezone). | Your first improved organisation request (later clarified to docs-only). |
| 2026-08-24 | v2 → v3: Corrected split — docs nested `docs/<session>/<date>/<purpose>/<artifact>_v<ver>_<time>.<ext>` (durable, `resolve-docs-path.py`), scratch reverted to v1 `scratch/<session>/<purpose>_<ts>` (ephemeral, `resolve-scratch-path.py`); note direct `markdownlint-cli2`. | Your correction: docs file organisation nested, scratch v1 is better, `npx` prohibited. |
| 2026-08-24 | v3 → v4: Consolidated straight-forward plan from v3 — single coherent document integrating final docs+scratch split, no incremental delta sections. | Your request for straight-forward plan from v3 instead of plan → change 1 → change 2. |
| 2026-08-24 | v4 → v5: Add explicit per-item completion handling for tickets like AES-1144 (Dev Complete but not Done) — multi-item checklist from Business/Functional/Validation sections must be explicitly verified per item before marking ticket complete. | User note: AES-1144 is not completed, explicitly asks for completion of each item — update plan if needed. |
| 2026-08-24 | v5 → v6: Added Team Jira Rules extraction (CTRM Build Project ▸ Paper Trades ▸ Jira Rules) + work-item card correction flow for AES-1144 via preferred acli edit (web-card fallback); IST-only timestamps + per-epic folder/detail-page contracts recorded in acers-web/docs/AGENTS.md. | User: 1144 still has jira actions — correct the details card per team rules; acli edit preferred. |
| 2026-08-24 | v6 → v7: Added Dev Complete → Official Workflow Transformation Playbook — classify actual state, preserve semantics via label + Waiting on, transition via acli, fill custom fields (10219 Waiting on / 10252 Release Status) via authenticated REST PUT fallback with field-discovery recipe; applied example AES-1144. | User: clarify non-official status transformation without info loss + missing-field filling. |
| 2026-08-24 | v7 → v8: Added Gate PR-Meta — PR title/body/branch corrections are gated like Jira actions before Phase 4; truncated-title reconstruction grounded in commits/files via gh-pr-edit skill; residual structural items (branch names, stacked bases, CONFLICTING) surfaced with options; applied to AES-1144 #693/#710. | User: PR title & body fix still not complete — corrections are also gated; update plan so subsequent actions follow gate. |
| 2026-08-24 | v8 → v9: Multi-PR Handling Policy — supersedes MULTI_PR_DEFERRED; stacked vs independent classification, per-PR Gate PR-Meta, bottom-up review order, stack merge mechanics (no delete on non-top merges, base re-target via PATCH, conflict blocking), AES-1144 example. | User: what about multi pr handling? |
| 2026-08-24 | v9 → v10: Corrected in-house stacked PR merge mechanics — top-down intra-stack first (#710 main_aes-1142-1 → main_aes-1142, --delete-branch), then base promotion (#693 main_aes-1142 → main); no re-targeting; conflicts on base PR block only promotion; supersedes v9 bottom-up+retarget subsection. | User: this is our own stacked flow, not official GitHub stacked PRs; part branches untouched for granularity. |
| 2026-08-24 | v10 → v11: Path-B recovery + pending-review migration — immutable-head lesson (rename closes PRs), replacement PRs N1/N2, unsubmitted review replay at verbatim positions (anchor-SHA proof), discard-with-message on old reviews, Jira comment id 16846 in-place URL swap. | User: path B with plan; migrate my pending review comments to correct positions; discard old reviews with messages. |
| 2026-08-24 | v11 → v12: Post-recovery hygiene rules — (1) supersession trail on closed PRs (comment+banner+review delete, executed), (2) superseded description repair without stale instructions (executed), (3) Jira bare-URL convention in PR bodies (rule + surgical fix executed), (4) review-comment level fidelity via GraphQL subjectType FILE (rule + #713 fix executed). | User: update plan re: 4 hygiene items before proceeding. |
| 2026-08-25 | v12 → v13: Code Review Workflow Rules codified (multi-PR review≠merge orders, review-before-tests gate, maximum-detail review docs, one-by-one fixes, strict linting as standing review rule) + Extended Empirical Parity Evaluation Protocol at maximum detail (9-tool steps 0–11, per-step persistence lifecycle, locked rulings Q1–Q6). | User: update plan — review order correction, review before tests, max-detail review docs, fixes one-by-one, strict linting rule, parity protocol in main plan. |
| 2026-08-25 | v13 → v14: Added Per-Pair Comparison Gate to parity protocol — each Tool-vs-Biome pair is a gated unit with arbitrarily many activities, closed only by explicit user confirmation 'no more activities for A vs Biome' before next tool starts; records premature Prettier run as parked/unscored. | User: after each pair comparison need explicit confirmation before next. |
| 2026-08-25 | v14 → v15: Added Standard Per-Pair Activity Template — formalizes the oxlint↔Biome activity set (baseline+max runs, within-tool superset, cross-tool coverage G⊇X/J-vs-B, semantic map, location drift, quality split, gate) as the fixed protocol for every pair; Biome side captured once and reused; tool-class adaptations (linter/formatter/type-checker/runtime-probe). | User: these activities are same for other pairs — codify. |
| 2026-08-26 | v15 → v16: Added oxlint CRA Baseline Hardening + CI Wiring — CRA-resemblance rationale (100% goal, minimum-over-ESLint fallback, jsx-pascal-case Node-18 gap), baseline adoption via existing npm scripts, redundant lint:tests removal, industrial group+sort normalization, and the 3-commit blank-line-anchor arrangement for in-place-edit legibility (all outcome-neutral, 1394 findings); plus GitHub Actions plan (push+PR triggers, jdx/mise-action@v2, npm ci, open failure-policy decision). | User: update the plan first before the CI workflow — record the whole oxlint baseline story and that these edits change no values. |
| 2026-08-26 | v16 → v17: CI workflow 9da79106 landed (.github/workflows/lint.yml, push+PR triggers, mise-action, annotated -f github + gate --max-warnings=1393), 3 commits pushed to origin/review/main_aes-1144 (pending 1 lint.yml), v16 title fix (v15→v16), task .github claim fix; failure-policy decision remains open (gate red until 1 rules-of-hooks error fixed). | You pushed 3 (excluding workflow); lint workflow is the pending push; update plan to reflect landed workflow and correct push counts. |

## Execution Order

1. Planning artifacts written — this file (`v4` consolidated) + `task.md` + `resolve-docs-path.py` helper.
2. Present for approval — this submission.
3. On approval — execute Steps 0–7 per ticket, pausing at Gate 1 (list), Gate 2 (per-ticket Jira), Gate 3 (per-PR merge).

## Explicit Completion Handling — Per-Item Verification (new)

For tickets where `status` is `Dev Complete` but the Jira description contains multi-item Business Requirements / Functional Requirements / Validation Rules (e.g., `AES-1144 Trader Mapping`), the plan now requires **explicit per-item completion verification** before considering the ticket complete or proceeding to PR merge.

- **Trigger:** `issuetype: Subtask`, `status.name: Dev Complete` but `Business Requirements` table (API Trader Name, System Trader, Created By, Created Date), `Functional Requirements` list (Trader Mapping maintenance page: API Trader Name, System Trader lookup Trader Role only, Many-to-One, unique API Trader Name, Active/Inactive; Trade Processing ordered steps; Validation Rules), etc., are not all marked Done.
- **Action in Step 2a/2b:** When `view --fields '*all'` shows `status: Dev Complete` but description still lists open items, create `scratch/<session>/pr-<N>/item-completion_<ts>.md` with checklist:

  ```markdown
  - [ ] Trader Mapping master fields (API Trader Name, System Trader) — code exists?
  - [ ] System Trader lookup Trader Role only
  - [ ] Many-to-One mapping
  - [ ] Unique API Trader Name constraint
  - [ ] Active/Inactive status
  - [ ] Trade Processing steps 1-5 (read, search, active mapping check, etc.)
  - [ ] Validation Rules (mandatory, unique, Trader Role only, etc.)
  ```

  For each item, record `code location` (`acers-web/src/...`), `PR evidence` (`#693`, `#710`), `test sweep` result, `graph impact`.
- **Gate 2 extension:** In addition to `no jira actions remaining?`, prompt `Confirm per-item completion for AES-1144?` — list unchecked items. User must explicitly confirm each item or provide correction. Ticket saved to `acers-web/docs/jira/AES-1144.md` must note `Status: Dev Complete — not completed, explicit per-item completion required` (already done).
- **PR correlation:** Even if `PR 1` + `PR 2` would be `MULTI_PR_DEFERRED`, the per-item checklist still applies — e.g., `PR 693` may cover master fields, `PR 710` may cover trade processing. Document which PR covers which item.
- **Merge gate:** No `gh pr merge --rebase` for any PR of a ticket with unchecked items, even if PR technically `mergeable`. Explicit item completion is a pre-merge gate alongside `base==main` etc.

## Explicit Completion Handling — Per-Item Verification (new)

For tickets where `status` is `Dev Complete` but the Jira description contains multi-item Business Requirements / Functional Requirements / Validation sections (e.g., `AES-1144 Trader Mapping`), the plan requires **explicit per-item completion verification** before considering the ticket complete or proceeding to PR merge.

- **Trigger:** `issuetype: Subtask`, `status.name: Dev Complete`, but description still lists open items.
- **Action:** create per-PR item-completion checklists under `acers-web/scratch/<session-id>/pr-<N>/`; each item needs `code location`, `PR evidence`, `test sweep`, `graph impact`.
- **Gate 2 extension:** besides `no jira actions remaining?`, confirm per-item completion explicitly.
- **Merge gate:** no `gh pr merge --rebase` while any item is unchecked.

## Team Jira Rules Extraction & Work-Item Card Correction (new — v6)

### Inputs (locked)

- Team: **`CTRM Build Project`**, Channel: **`Paper Trades`**, Tab: **`Jira Rules`**
- Correction method preference: **`acli jira workitem edit` preferred; automated web-card edit fallback** (only when acli cannot set a field)
- First target ticket: **AES-1144** (still has jira actions remaining); rules will be reused for AES-1227 / AES-1232 Gate 2s
- All Jira doc timestamps in **IST** (`UTC+05:30`) — durable rule recorded in `acers-web/docs/AGENTS.md`

### Phase A — Extract Rules Tab (Chrome Teams automation)

1. Focus existing `teams.cloud.microsoft` tab; navigate: Teams rail → search/open team `CTRM Build Project` → channel `Paper Trades`.
2. Enumerate channel-header tabs (`[role="tab"]`) → click `Jira Rules`.
3. Extract by content type:
   - Wiki canvas → DOM text scrape → markdown
   - Website tab → read iframe `src` → fetch within authenticated session
   - Fallback: pinned posts / tab description
4. Capture raw + normalized atomic rules list to `acers-web/scratch/<session-id>/teams-jira-rules_<ts>.json/.md` via `resolve-scratch-path.py`.

### Phase B — Rule → Correction Mapping (Gate 2)

1. Diff each atomic rule against fresh AES-1144 fields (`view --fields '*all'`).
2. Present corrections table `rule | field | current | proposed | exact acli command` — nothing executed until approval (individual or batch).

### Phase C — Execute Corrections

1. Apply approved edits via `acli jira workitem edit --key AES-1144 …`.
2. Fallback only if acli cannot set a field: automated web-card edit on open AES-1144 Jira tab with post-save verification.
3. Re-pull fields; regenerate `acers-web/docs/jira/AES-51/AES-217/AES-1144.md` per detail-page contract (IST times, full headings, field table incl. Expiry Time/Rank where present).
4. Refresh `acers-web/docs/jira/AES-51/index.md` rows if status/labels change.
5. Save extracted rules as durable reference under `acers-web/docs/jira/team-rules.md` (placement to be confirmed).
6. Re-ask Gate 2 `no jira actions remaining for AES-1144?` → only then PR correlation (693/710, MULTI_PR_DEFERRED) and next ticket.

### Docs Contract Additions (recorded in `acers-web/docs/AGENTS.md`)

- Per-epic folder organisation `docs/jira/<EPIC>/index.md` + `<EPIC>/<STORY>/<SUBTASK>.md` mirroring parentage; children in Jira rank order.
- Detail-page contract: Field table (Type…Votes + extras like Expiry Time/Rank), full Description ADF rendering, Acceptance Criteria checklists, Comments, Children, Linked Issues (issuelinks + PR inlineCards); `Dev Complete` never treated as completed without explicit per-item confirmation.
- IST-only timestamps with conversion note; raw offsets preserved in scratch JSON views only.

## Team Jira Rules Extraction & Work-Item Card Correction (new — v6)

### Inputs (locked)

- Team: **`CTRM Build Project`**, Channel: **`Paper Trades`**, Tab: **`Jira Rules`**
- Correction method preference: **`acli jira workitem edit` preferred; automated web-card edit fallback** (only when acli cannot set a field)
- First target ticket: **AES-1144** (still has jira actions remaining); rules will be reused for AES-1227 / AES-1232 Gate 2s
- All Jira doc timestamps in **IST** (`UTC+05:30`) — durable rule recorded in `acers-web/docs/AGENTS.md`

### Phase A — Extract Rules Tab (Chrome Teams automation)

1. Focus existing `teams.cloud.microsoft` tab; navigate: Teams rail → search/open team `CTRM Build Project` → channel `Paper Trades`.
2. Enumerate channel-header tabs (`[role="tab"]`) → click `Jira Rules`.
3. Extract by content type:
   - Wiki canvas → DOM text scrape → markdown
   - Website tab → read iframe `src` → fetch within authenticated session
   - Fallback: pinned posts / tab description
4. Capture raw + normalized atomic rules list to `acers-web/scratch/<session-id>/teams-jira-rules_<ts>.json/.md` via `resolve-scratch-path.py`.

### Phase B — Rule → Correction Mapping (Gate 2)

1. Diff each atomic rule against fresh AES-1144 fields (`view --fields '*all'`).
2. Present corrections table `rule | field | current | proposed | exact acli command` — nothing executed until approval (individual or batch).

### Phase C — Execute Corrections

1. Apply approved edits via `acli jira workitem edit --key AES-1144 …`.
2. Fallback only if acli cannot set a field: automated web-card edit on open AES-1144 Jira tab with post-save verification.
3. Re-pull fields; regenerate `acers-web/docs/jira/AES-51/AES-217/AES-1144.md` per detail-page contract (IST times, full headings, field table incl. Expiry Time/Rank where present).
4. Refresh `acers-web/docs/jira/AES-51/index.md` rows if status/labels change.
5. Save extracted rules as durable reference under `acers-web/docs/jira/team-rules.md` (placement to be confirmed).
6. Re-ask Gate 2 `no jira actions remaining for AES-1144?` → only then PR correlation (693/710, MULTI_PR_DEFERRED) and next ticket.

### Docs Contract Additions (recorded in `acers-web/docs/AGENTS.md`)

- Per-epic folder organisation `docs/jira/<EPIC>/index.md` + `<EPIC>/<STORY>/<SUBTASK>.md` mirroring parentage; children in Jira rank order.
- Detail-page contract: Field table (Type…Votes + extras like Expiry Time/Rank), full Description ADF rendering, Acceptance Criteria checklists, Comments, Children, Linked Issues (issuelinks + PR inlineCards); `Dev Complete` never treated as completed without explicit per-item confirmation.
- IST-only timestamps with conversion note; raw offsets preserved in scratch JSON views only.

## Dev Complete → Official Workflow Transformation Playbook (new — v7)

Non-official statuses found in the wild (`Dev Complete`, potentially others) are transformed onto the official workflow (**To Do / In Progress / Testing / Done** per `acers-web/docs/jira/team-rules.md`) **without losing information**: the semantic carried by the non-official status is re-encoded into labels + rule fields, and the original value stays archived in the ticket's docs page.

### Transformation Procedure (any ticket)

1. **Detect** non-official status via `acli jira workitem view --fields status`.
2. **Classify actual state** — ask the user when ambiguous; known mappings so far:
   - `Dev Complete` + *waiting mentor review* → `In Progress`, Waiting on `Dev`, label `need-frontend-mentor-support`
   - `Dev Complete` + *needs QA* (team-rules row 3) → `Testing`, Waiting on `QA / Testing`, Release Status `Not ready`
3. **Preserve semantics without loss:**
   - Original status value recorded verbatim in the docs page (`## Corrections Applied` Before column) before any change.
   - The *reason* the dev marked it complete-but-blocked becomes a **label** (added only if absent) so the signal survives in Jira queries even after the status changes.
4. **Transition** to the chosen official status: `acli jira workitem transition --key <KEY> --status <Official> --yes`.
5. **Fill missing field values** per team-rules matrix:
   - Labels: `acli jira workitem edit --key <KEY> --labels "<label>" --yes` (acli supports labels natively).
   - Custom option fields (Waiting on `customfield_10219`, Release Status `customfield_10252`) — acli `edit`/`--from-json` does not support arbitrary custom fields; use **authenticated REST PUT** through the open Jira tab:

     ```js
     PUT /rest/api/3/issue/<KEY>
     {"fields": {"customfield_10219": {"value": "..."}, "customfield_10252": {"value": "..."}}}
     ```

     Expect HTTP `204`. This is the sanctioned fallback per Phase C preference order (acli first, web-session automation second).
6. **Field discovery recipe** (for any unknown card field):
   - Field ID: open ticket web page → find label element → ancestor `[data-testid]` contains `...customfield_XXXXXX`.
   - Allowed values: same-tab XHR `GET /rest/api/3/issue/<KEY>/editmeta` → `fields.customfield_XXXXXX.{name,schema.type,allowedValues[].value}`.
   - Current values: `GET /rest/api/3/issue/<KEY>?fields=customfield_XXXXXX,...`.
7. **Verify** all changed fields via one fresh `GET ?fields=status,labels,customfield_10219,customfield_10252`; every edit must show its new value.
8. **Docs refresh:** update detail page field table + `## Corrections Applied` (Before/After/Rule) + Status Interpretation; IST timestamps; lint.
9. **Gate 2 re-ask:** `no jira actions remaining for <KEY>?` before PR correlation.

### Applied Example — AES-1144 (executed 2026-08-24)

| Field | Before | After | Mechanism |
| ------- | -------- | ------- | ----------- |
| Status | Dev Complete | In Progress | `acli transition` |
| Labels | *(none)* | `need-frontend-mentor-support` | `acli edit --labels` |
| Waiting on (`10219`) | None | Dev | REST PUT `204` |
| Release Status (`10252`) | None | Not ready | REST PUT `204` |

Rationale: developer finished PRs but awaits **mentor review** — a state the official rules do not model yet (official-rules update deferred). Mentor-review signal lives on as label + Waiting on=Dev; nothing lost.

### Scope

Playbook applies to every remaining standup ticket carrying non-rule statuses (next: AES-1227, AES-1232 — both currently `Dev Complete`) and retroactively to any archived ticket flagged during audits.

## PR Metadata Correction Gate — Gate PR-Meta (new — v8)

Mirrors Gate 2 (Jira actions) discipline but for **Pull Request title/body/branch corrections**. Inserted between Phase 3 (PR correlation + validation) and Phase 4 (fresh content / test sweep / review). No Phase 4 work may start until this gate is explicitly cleared by the user.

### Gate Procedure (per ticket, per PR in stack order)

1. **Validate contract** and present results table per PR: `base==main`, head-branch-contains-KEY, title/body-contains-KEY, mergeable state.
2. **Propose metadata corrections** where violated:
   - Literal truncated text (`…` baked into title/body by the author) → reconstruct full sentence grounded in PR commits + changed files (never guess beyond evidence).
   - Missing ticket key → prepend `AES-XXXX:` to title; body gains Jira link + bullet summary of changes + stack notes.
3. **Apply approved corrections** via [`gh-pr-edit`](../../../../.agents/skills/gh-pr-edit/SKILL.md) skill script:

   ```bash
   python3 .agents/skills/gh-pr-edit/scripts/gh-pr-edit.py edit \
     --pr <N> --repo anushadpk/acers-web \
     --title "<corrected>" --body-file <scratch>/pr-<N>/body.md
   ```

   Body files live under `acers-web/scratch/<session-id>/pr-<N>/body.md`.
4. **Surface residual structural items** explicitly with options — these are *not* auto-fixed; user decides:
   - Head/base branch names not containing KEY (e.g., `main_aes-1142` for AES-1144 work) — rename via API would cascade into stacked PRs; default is leave-as-noted.
   - Stacked base ≠ `main` (e.g., #710 base `main_aes-1142`) — re-target only after parent merges.
   - `CONFLICTING` mergeable state — author must resolve; blocks Gate 3 merge later regardless.
5. **Verify** every correction via `gh-pr-edit.py view` (title has KEY, body length meaningful).
6. **GATE PROMPT:** `no PR title/body actions remaining for <KEY>?` — must be answered YES (or supply more corrections) before Phase 4 begins.

### Applied Example — AES-1144 (#693 → #710, executed 2026-08-24)

| PR | Title before | Title after | Body before → after |
| ---- | ------------- | ------------- | --------------------- |
| #693 | `Add Broker and Trader Mapping components with generic mapping functio…` | `AES-1144: Add Broker and Trader Mapping components with generic mapping functionality` | `…nality` (7 chars) → 501 chars w/ Jira link + file bullets + stack note |
| #710 | `Add file upload and export functionality to GenericMappingTable and T…` | `AES-1144: Add file upload and export functionality to GenericMappingTable and TraderMapping components` | `…raderMapping components` (24 chars) → 428 chars w/ Jira link + bullets + ⚠️ stacked-base warning |

Residual (awaiting user decision at gate): branch names still `aes-1142`; #710 base stacked on #693 head; #693 CONFLICTING with `main`.

### Scope

Gate applies to every PR of every ticket in the standup batch (single or stacked), and composes with the v7 Dev Complete transformation playbook (both gates must clear independently before review/merge phases).

## Multi-PR Handling Policy (new — v9, supersedes `MULTI_PR_DEFERRED`)

**Supersession:** earlier plan revisions deferred tickets with >1 PR (`MULTI_PR_DEFERRED`). Per user decision 2026-08-24, **multi-PR tickets are now fully in scope** — reviewed, corrected, and merged like single-PR tickets, with stacking discipline added. Any remaining `MULTI_PR_DEFERRED` markers in artifacts are historical.

### Classification (per ticket, at Phase 3)

| Pattern | Detection | Handling |
| --------- | ----------- | ---------- |
| **Stacked chain** | PR(n+1).base == PR(n).head (e.g., #710 base `main_aes-1142` = #693 head) | Review + merge strictly bottom-up; special merge mechanics below |
| **Independent set** | All PRs share `base == main`, unrelated heads | Review any order; merge any order |
| **Mixed** | Some stacked, some independent | Treat each stack independently |

### Gate Application

- Gate PR-Meta runs **per PR** (each PR validated/corrected independently, in stack order).
- Jira-side: all PRs of the ticket must be listed as PR1..PRn in the Jira comment/description; missing entries → @assignee comment per original contract.

### Review Order (stacked)

1. Review PR1 (#bottom of stack) first — its diff is the foundation.
2. Then PR2 — its diff contains only the *increment* over PR1 (GitHub shows this automatically for stacked bases).
3. Submit reviews separately per PR (`gh pr review <N>`), each with its own findings file under `acers-web/scratch/<session-id>/pr-<N>/`.

### Merge Mechanics (stacked — critical)

1. Merge bottom PR first: `gh pr merge <N> --rebase` — **WITHOUT `--delete-branch`** if its head branch is the base of the next stacked PR (deleting it would orphan the next PR).
2. After bottom PR merges, **re-target** the next PR's base to `main`:

   ```bash
   gh api -X PATCH repos/anushadpk/acers-web/pulls/<N+1> -f base=main
   ```

3. Re-validate mergeable state on the re-targeted PR (conflicts may surface once diff recomputes against main); resolve or return to author before proceeding.
4. Repeat until the top of the stack; the final PR may use `--rebase --delete-branch`.
5. Each merge still passes **Gate 3** (explicit user approval) individually.

### Conflict Handling

- A CONFLICTING bottom PR blocks the whole stack: report to author (review comment REQUEST_CHANGES + optional Jira note), pause that stack, continue other tickets.
- Never force-resolve conflicts ourselves without explicit user instruction.

### Example In Flight — AES-1144

- #693 (bottom, base `main`, CONFLICTING) → #710 (top, base `main_aes-1142`): review 693 → review 710 → Gate 3 approve → merge 693 (no delete) → retarget 710 base=main → validate → Gate 3 → merge 710 (`--rebase --delete-branch`).

### Task Tracking

Per-ticket summary rows gain one line per PR (`PR | stack position | review | gate3 | merge`); `MULTI_PR_DEFERRED` no longer terminates a ticket.

## In-House Stacked PR Flow — Corrected Merge Mechanics (new — v10, supersedes v9 merge-mechanics subsection)

These are **our own stacked-PR conventions**, not official GitHub stacked PRs. Branch naming encodes parts of one ticket's work:

```text
#693:  main_aes-1142   →  main              (part 1)
#710:  main_aes-1142-1 →  main_aes-1142    (part 2)
```

`main_aes-1142-1` is the second part of `main_aes-1142`. The first-part branch is never touched directly — granularity preserved because each part keeps its own branch + PR + commit trail.

### Merge Order (corrected — top-down intra-stack, then base promotion)

1. **Merge part-2 PR into its base branch first:** #710 `main_aes-1142-1` → `main_aes-1142`.

   ```bash
   gh pr merge 710 --rebase --delete-branch   # consumes/deletes main_aes-1142-1
   ```

2. **Then promote via the base PR:** #693 `main_aes-1142` → `main` now carries parts 1+2 combined.

   ```bash
   gh pr merge 693 --rebase --delete-branch   # consumes/deletes main_aes-1142
   ```

3. **No base re-targeting / PATCHing** — the v9 approach (merge bottom → re-target next PR base to `main`) is superseded and must not be used for these in-house stacks.

### Rules

- Gate PR-Meta per PR and Gate 3 per merge still apply, in corrected order (Gate 3 ×2: approve #710 merge, then approve #693 promotion).
- A CONFLICTING base PR (#693 vs `main`) does **not** block step 1 (intra-stack merge); it blocks only final promotion (step 2) until resolved by author.
- After step 1, re-validate #693 mergeable state (its diff now includes part 2).
- Both head branches are deleted after their merges; nothing else renamed — branch-name KEY residuals remain leave-as-noted unless user says otherwise.

### Applied Example — AES-1144 (corrected)

| Step | Action | Command | Gate |
|------|--------|---------|------|
| 1 | #710 `main_aes-1142-1` → `main_aes-1142` | `gh pr merge 710 --rebase --delete-branch` | Gate 3 |
| 2 | #693 `main_aes-1142` → `main` (parts 1+2) | `gh pr merge 693 --rebase --delete-branch` | Gate 3 |

Supersedes the v9 table row "merge 693 (no delete) → retarget 710 base=main → validate → merge 710".

## Path-B Recovery & Pending-Review Migration (new — v11)

### Incident Record (lesson learned 2026-08-24)

Renaming a **head branch of an open PR** via `POST /branches/{branch}/rename` closed both PRs (#693/#710): GitHub auto-updates *base* references on rename but treats the old *head* ref as deleted (`PATCH state=open` → `422 The main_aes-1142 branch has been deleted`). PR head refs are immutable; base refs are patchable. Rule going forward: **never rename a branch that is the HEAD of any open PR**; if KEY-correctness of branches is required, close-and-recreate is the sanctioned flow (this section).

### Recovery Procedure (executed for AES-1144)

Safety order: harvest → create → replay → verify → discard last.

1. **Harvest** author-private PENDING reviews from closed PRs before anything else:

   ```bash
   gh api repos/anushadpk/acers-web/pulls/<OLD>/reviews            # find state=PENDING ids
   gh api repos/anushadpk/acers-web/pulls/<OLD>/reviews/<ID>/comments
   ```

   Persist JSON to `acers-web/scratch/<session-id>/pr-<OLD>/pending-review.json`.
2. **Create replacement PRs** bottom-up (N1 = `main_aes-1144`→`main`; N2 = `main_aes-1144-1`→`main_aes-1144`), corrected titles/bodies per Gate PR-Meta drafts; PATCH N1 body after N2 exists so cross-references are real numbers.
3. **Replay pending reviews unsubmitted**: `POST /pulls/<N>/reviews` with `commit_id` = new-branch head SHA and `comments[]` carrying original `{path, position, body}` — omitting `event` keeps state PENDING (author retains edit rights). Fidelity proof: renamed branches preserve commits, so comment anchor SHAs == new HEAD SHAs ⇒ `position` indices valid verbatim. Fallback: derive `line`+`side` from `/pulls/<N>/files` hunks; unmappable comments are reported to user, never dropped.
4. **Verify replay** 1:1 (review count, PENDING state, path/position/body) before touching the old PRs.
5. **Discard old reviews with proper messages:** post explanatory supersession issue-comment on each closed PR (migration note + pointer to replacement), then `DELETE /pulls/<OLD>/reviews/<ID>`. If DELETE refused on closed PRs, leave inert and note in the comment.
6. **Jira in-place update:** patch only `inlineCard.attrs.url` inside existing comment `id 16846` (GET ADF → surgical swap `pull/693→pull/N1`, `pull/710→pull/N2` → PUT → re-GET verify). Comment format/layout preserved byte-for-byte otherwise.
7. **Docs/task refresh:** detail page PR section re-pointed to N1/N2 with "replaces closed #693/#710" notes; task checklist re-pointed; scratch pr-meta snapshots saved.

### Harvested Data (AES-1144)

| Old PR | Review ID | Comments (path @ position) |
| -------- | ----------- | ----------------------------- |
| #693 | 4990530137 | TableFilter.constants.tsx@1 ("Rename the file…"), SidebarMenuList.tsx@1 ("Use constants…"), ApiSettings/Index.tsx@36 ("Type?") — anchor SHA `9c7b90e9` |
| #710 | 4990887651 | ApiSettings/Index.tsx@25 ("Type?") — anchor SHA `1e9d47b6` |

New-branch heads matched anchors exactly: `main_aes-1144`=9c7b90e9, `main_aes-1144-1`=1e9d47b6.

### Scope

Applies to any future accidental head-branch rename across the batch; complements Gate PR-Meta (metadata gate) and v10 stacked-flow rules (which remain unchanged).

## Path-B Recovery & Pending-Review Migration (new — v11)

### Incident Record (lesson learned 2026-08-24)

Renaming a **head branch of an open PR** via `POST /branches/{branch}/rename` closed both PRs (#693/#710): GitHub auto-updates *base* references on rename but treats the old *head* ref as deleted (`PATCH state=open` → `422 The main_aes-1142 branch has been deleted`). PR head refs are immutable; base refs are patchable. Rule going forward: **never rename a branch that is the HEAD of any open PR**; if KEY-correctness of branches is required, close-and-recreate is the sanctioned flow (this section).

### Recovery Procedure (executed for AES-1144)

Safety order: harvest → create → replay → verify → discard last.

1. **Harvest** author-private PENDING reviews from closed PRs before anything else:

   ```bash
   gh api repos/anushadpk/acers-web/pulls/<OLD>/reviews            # find state=PENDING ids
   gh api repos/anushadpk/acers-web/pulls/<OLD>/reviews/<ID>/comments
   ```

   Persist JSON to `acers-web/scratch/<session-id>/pr-<OLD>/pending-review.json`.
2. **Create replacement PRs** bottom-up (N1 = `main_aes-1144`→`main`; N2 = `main_aes-1144-1`→`main_aes-1144`), corrected titles/bodies per Gate PR-Meta drafts; PATCH N1 body after N2 exists so cross-references are real numbers.
3. **Replay pending reviews unsubmitted**: `POST /pulls/<N>/reviews` with `commit_id` = new-branch head SHA and `comments[]` carrying original `{path, position, body}` — omitting `event` keeps state PENDING (author retains edit rights). Fidelity proof: renamed branches preserve commits, so comment anchor SHAs == new HEAD SHAs ⇒ `position` indices valid verbatim. Fallback: derive `line`+`side` from `/pulls/<N>/files` hunks; unmappable comments are reported to user, never dropped.
4. **Verify replay** 1:1 (review count, PENDING state, path/position/body) before touching the old PRs.
5. **Discard old reviews with proper messages:** post explanatory supersession issue-comment on each closed PR (migration note + pointer to replacement), then `DELETE /pulls/<OLD>/reviews/<ID>`. If DELETE refused on closed PRs, leave inert and note in the comment.
6. **Jira in-place update:** patch only `inlineCard.attrs.url` inside existing comment `id 16846` (GET ADF → surgical swap `pull/693→pull/N1`, `pull/710→pull/N2` → PUT → re-GET verify). Comment format/layout preserved byte-for-byte otherwise.
7. **Docs/task refresh:** detail page PR section re-pointed to N1/N2 with "replaces closed #693/#710" notes; task checklist re-pointed; scratch pr-meta snapshots saved.

### Harvested Data (AES-1144)

| Old PR | Review ID | Comments (path @ position) |
| -------- | ----------- | ----------------------------- |
| #693 | 4990530137 | TableFilter.constants.tsx@1 ("Rename the file…"), SidebarMenuList.tsx@1 ("Use constants…"), ApiSettings/Index.tsx@36 ("Type?") — anchor SHA `9c7b90e9` |
| #710 | 4990887651 | ApiSettings/Index.tsx@25 ("Type?") — anchor SHA `1e9d47b6` |

New-branch heads matched anchors exactly: `main_aes-1144`=9c7b90e9, `main_aes-1144-1`=1e9d47b6.

### Scope

Applies to any future accidental head-branch rename across the batch; complements Gate PR-Meta (metadata gate) and v10 stacked-flow rules (which remain unchanged).

## Post-Recovery Hygiene Rules (new — v12)

Four corrections applied immediately after Path-B recovery; codified here as durable rules.

### 1. Supersession Trail on Closed PRs (executed)

Every closed-by-rename/superseded PR gets, before anything else is forgotten:

- An explanatory issue-comment (migration note, replacement number, reason).
- A `> ⛔ SUPERSEDED — do not use.` banner prepended to its body naming the replacement PR, the rename that caused closure, and the `422` reopen failure.
- Its unsubmitted pending review comments migrated, then the stale PENDING review **deleted** (verified `0 PENDING` remaining).

Executed: #693 (→#713, comment `issuecomment-5402757707`, review `4990530137` deleted), #710 (→#714, `issuecomment-5402757880`, `4990887651` deleted).

### 2. Superseded Description Repair — no stale instructions (executed)

Closed PR bodies must not carry now-false operational instructions:

- Dead branch references (`main_aes-1142*`) struck through with a historical-correction parenthetical.
- Wrong merge-order guidance (e.g., #710's "Merge #693 first", contradicting the v10 in-house flow) replaced with the correct live sequence (#714 → #713).
- Original change summaries retained verbatim below the banner — history preserved, only false instructions neutralised.

Executed: both #693/#710 bodies rewritten under banner; snapshots `pr-*/body-v3-superseded.md`.

### 3. Jira Link Convention in PR Bodies (rule)

Repo convention (verified across #711/#709/#705/#704/#701): the Jira work-item URL appears as a **bare auto-linking URL** (`https://ompventure.atlassian.net/browse/AES-XXXX`), typically at the end of the body — **never** as a markdown link (`[Jira](url)`). Gate PR-Meta body drafting must follow this; fixes are surgical line-only patches (nothing else in the body changes). Executed on all four AES-1144 PRs (#693/#710/#713/#714); snapshots `pr-*/body-v3*.md`.

### 4. Review-Comment Level Fidelity (rule)

When migrating or recreating PR review comments, **preserve the author's intended comment level** (whole-file vs line):

- REST legacy `position` cannot express file-level comments — it silently anchors them at diff position 1 (line-level).
- File-level comments are created via **GraphQL**:

  ```graphql
  mutation($rid: ID!) { addPullRequestReviewThread(input: {
    pullRequestReviewId: $rid, path: "<file>",
    body: "<text>", subjectType: FILE }) { thread { id } } }
  ```

  Verify afterwards via `node(id:) { ... on PullRequestReviewThread { comments { nodes { subjectType } } } }` == `FILE`.
- Line-level comments stay position/line-based as harvested.
- Level intent must be confirmed with the user when harvesting (it is not machine-inferable from `position` data alone).

Executed: #713 comments 1–2 recreated as `FILE` threads (`PRRT_kwDONt4yXs6b5dwx`, `PRRT_kwDONt4yXs6b5d7k`); docs table gained a Level column.

# Code Review Workflow Rules (new — v13)

Rules distilled from the AES-1144/#713/#714 review cycle; binding for every subsequent ticket/PR in this batch.

### 1. Multi-PR Orders Are Separate — Review ≠ Merge

- **REVIEW order:** strictly **bottom-up** — part 1 (#N1) first (its diff is the foundation), then part 2 (#N2 shows only its increment).
- **MERGE order:** in-house stacked flow (plan v10) — **part 2 merges into its base branch first**, then part 1 promotes to `main`.
- These are two different sequences. Never apply merge-order logic during the review phase or vice-versa.

### 2. Review Completes Before Any Test Activity

- Phase ordering per ticket/PR: correlation → metadata gate → **code review (submitted)** → *only then* test-existence sweep / test-related discussion.
- Test findings discovered incidentally during code reading may be noted in the review body, but dedicated test-sweep steps wait until review submission is confirmed.

### 3. Review Result Documents Contain Maximum Detail

Every `review_<ts>.md` follows the depth established in `pr-713/review.md`:

- Per issue: **What** (exact file:line + offending snippet) · **Why** (blocking reason / risk narrative) · **Correct fix** (concrete before/after code or commands) · **Verification** (how to prove fixed).
- Severity grouping: Must fix / Should fix / Consider.
- Plus Summary, Files Changed map, What-Looks-Good, Risk Assessment, Recommendation.

### 4. Fixes Are Worked One by One (after submission)

Once a review is submitted, follow-up sessions address issues sequentially — each fix verified against its Verification clause before moving to the next. Batch-fixing without verification is prohibited.

### 5. Strict Linting Is a Standing Rule of Review

Reviews include whitespace/EOF/formatting-hygiene findings as first-class issues (not nitpicks to skip). This rule triggered the full toolchain evaluation below.

---

## Extended Empirical Parity Evaluation Protocol (new — v13, maximum detail)

**Goal:** run each candidate tool at maximum capability against identical input, capture everything, and produce an evidence-based keep/drop verdict per tool.

### Locked Rulings

| # | Ruling |
| --- | --- |
| Q1 | oxlint max-tier escalation attempted; fallback to wired-config baseline if 1.16 misbehaves — recorded |
| Q2 | Two-tier structure everywhere tiers exist: **headline = recommended tier** (drives decision metrics); **potential artifact = all tiers incl. pedantic/nursery** (capability map, never penalizes adoption FP-rate) |
| Q3 | Full type-aware ESLint pass (`project: true` + tsconfig service + strict-type-checked) despite time cost — also answers whether oxlint's declared TS rules were ever active |
| Q4 | deno/bun installed via **brew** (`brew install deno`, `brew install oven-sh/bun/bun`) |
| Q5 | tsc evaluated at **last possible version on Node 18**: attempt `typescript@7.0.2` (engines ≥16.20 ✅), fallback chain 6.x → 5.x; repo-pinned 4.9.5 runs as realistic baseline alongside |
| Q6 | Everything possible, zero permanent mutation — check/dry-run modes only; fixable counts from reporting metadata (`--fix-dry-run`, summary fields), never applied |

### Standardized Input Contract

- Corpus: `src/**/*.{ts,tsx,js,jsx}` (~3k files) + CSS/config roots
- Exclusions: node_modules/build/coverage/test-results/playwright-report via each tool's ignore mechanism
- Location: review worktree `.git/modules-worktrees/review-main-aes-1144` @ `9c7b90e9` (clean PR-head checkout)
- Timing wrapper (`time -p`) on every run; cold-cache

### Per-Step Lifecycle (persistence discipline — persist before reset)

```text
1. MUTATE   install devDeps / create temp configs (worktree-local only)
2. RUN      check-mode(s); stdout/stderr TEE'D directly into scratch/<sid>/parity/<tool>/
3. ARCHIVE  copy into scratch/<sid>/parity/<tool>/:
              every temp config used (biome.json, eslint.config.js, dprint.json,
              tsconfig probe variants) · exit codes · timing lines · state snapshots
4. RESET    git reset --hard HEAD ; git clean -fd   # NO -x → gitignored node_modules SURVIVES
            verify: git status empty AND HEAD == 9c7b90e9
```

Nothing authoritative lives in the worktree at rest. Install commands recorded verbatim per artifact folder (package.json resets intentionally). `parity-report.md` reaches `docs/tooling/` only after user verdict on the scratch-based report.

### Steps

| # | Tool | Version | Install | Max-capacity invocation (all read-only) |
| --- | ------ | --------- | --------- | ------------------------------------------ |
| 0 | env | — | worktree `npm install`; corpus lock; timing wrapper | — |
| 1 | oxlint | 1.16.0 (present) | none | baseline `oxlint src/` + max-tier attempt (`-D correctness,suspicious,pedantic,style,perf -A none` — record actual accepted flags) |
| 2 | biome | 2.5.10 | worktree devDep pinned exact | temp `biome.json` (lineWidth 120): headline `biome lint ./src --max-diagnostics=500` + potential all-tiers run + `biome format ./src` + `biome check ./src`; rule-catalog snapshot |
| 3 | compare | — | — | TSV-normalize (`file:line:rule:message`), coverage A→B / B→A, FP spot-check ×10/side, perf delta → `parity-oxlint-vs-biome.md` |
| 4 | prettier | 3.9.6 | worktree devDep pinned | `prettier --list-different "src/**/*.{ts,tsx,js,jsx,json,css}"` (+ `--debug-check`) |
| 5 | eslint | 9.39.5 | worktree devDep pinned (10.x Node-blocked) | flat config quickstart (react-hooks + ts-eslint recommended) JSON run + **type-aware strict run** (`project:true`) + `--fix-dry-run --format json` fixable counts |
| 6 | dprint | 0.56.1 | standalone binary | temp config (TS+JSON+CSS, lineWidth 120) → `dprint check "src/**/*"` |
| 7 | standard/ts-standard | 17.1.2 / 12.0.2 | worktree devDeps | `standard "src/**/*.js"` · `ts-standard "src/**/*.ts?(x)"` — style-collision count quantified separately |
| 8 | tsc | dual: 4.9.5 pin + last-on-Node-18 attempt (7.0.2 → fallback 6→5) | pinned present; newest via temp prefix | `tsc --noEmit` ×2 baselines + `--noUnusedLocals --noUnusedParameters` probe |
| 8b | deno | latest via brew | `brew install deno` | `deno lint src/` · `deno fmt --check src/` |
| 8c | bun | latest via brew | `brew install oven-sh/bun/bun` | CLI surface probe — expected outcome: **"no comparable check gate"; excluded from matrix scoring** |

### Cross-Cutting Analysis & Verdicts

- Finding-class taxonomy {whitespace/EOF, style-opinion, correctness-pattern, type-aware, hooks/a11y, import-order}
- Tools × classes matrix; unique-value ranking; FP tables (per tier); performance table
- Deliverable: `docs/tooling/parity-report.md` + close ⚠️ verify entries in `oxlint-vs-biome.md`
- Verdict options per tool: adopt-primary / keep-complementary / retire / hybrid — governed by plan-v12 acceptance criteria (accepted-gaps documented, FP threshold, perf, Node-18 fit)

## Per-Pair Comparison Gate (new — v14, amends Extended Parity Protocol)

Each **"Tool A vs Biome"** comparison in the parity protocol is a **gated unit**, mirroring the per-ticket Gate 2 discipline:

1. A pair may contain **arbitrarily many activities** — baseline run, max run, superset analysis, per-rule location-drift, and any deeper sub-drills the user requests mid-pair. The number of sub-steps is not fixed in advance.
2. A pair is **NOT complete** until the user **explicitly confirms**: `no more activities for <A> vs Biome`.
3. **Only after that explicit confirmation** may the next tool's step begin. Starting the next tool early (as happened once with Prettier on 2026-08-25 — artifacts parked under `parity/prettier/`, not scored) is a protocol violation; such premature artifacts are held, not counted, until the prior pair is gated closed.
4. Each closed pair emits its own `parity-<A>-vs-biome.md` before the gate.

### Gate sequence (revised)

```text
Step 1–3   oxlint vs Biome  → [GATE: no more activities for oxlint vs Biome?]
Step 4     prettier vs Biome → [GATE]
Step 5     eslint vs Biome   → [GATE]
Step 6     dprint vs Biome   → [GATE]
Step 7     standard/ts-standard vs Biome → [GATE]
Step 8     tsc vs Biome      → [GATE]
Step 8b    deno vs Biome     → [GATE]
Step 8c    bun vs Biome      → [GATE]
Step 10–11 cross-cutting matrix + parity-report.md + final verdict
```

The final toolchain verdict (adopt/retire/keep-both per tool) is assembled only after every pair is individually gated closed.

### Current pair status (2026-08-25)

- **oxlint vs Biome:** activities done (baseline X, max A, superset A⊇X / I⊇G / G⊇X / J-vs-B, per-rule location drift 1–98%, decision-record draft). **AWAITING explicit closure.**
- **prettier vs Biome:** `--list-different` ran prematurely (1,742 files differ) — artifacts parked, pair not opened officially until oxlint pair is closed.

## Standard Per-Pair Activity Template (new — v15, formalizes what oxlint↔Biome did)

Every "Tool A vs Biome" pair runs this **fixed activity set** (the exact sequence executed for oxlint↔Biome), adapted by tool-class. This replaces per-pair improvisation.

### Biome side is captured once, reused for all pairs

Biome's runs are constant across every comparison — captured during the oxlint pair, reused thereafter:

- **G** = Biome recommended: 44 rules, 6,164 findings (`parity/biome/json/recommended.json`)
- **I/J** = Biome max (522 schema rules = warn, formatter/assist off): 165 rules, 66,178 findings (`parity/biome/json/max.json`)
- **format drift** = 1,746 files would reformat (`parity/biome/format.*`)

Only **Tool A's** runs are new per pair.

### Activities (linter-class tool: oxlint, eslint, standard, ts-standard, deno lint)

1. **Baseline run** — A at wired/default config → `X_A` rules, `Y_A` findings (JSON reporter, uncapped, timed).
2. **Max run** — A with all rules/tiers/plugins enabled → `A_A` rules, `B_A` findings.
3. **Within-tool superset:** verify `A_A ⊇ X_A` (rules) and `B_A ⊇ Y_A` (findings, exact file:line); record drift.
4. **Cross-tool rule coverage:**
   - `G ⊇ X_A`? (Biome recommended vs A baseline — semantic rule-intent mapping)
   - `J vs B_A`? (Biome max vs A max — semantic coverage %, genuine-gap %)
5. **Semantic rule map** — A's rule names → Biome leaf rule(s); mark covered / assist-domain / formatter-domain / opinion / genuine-gap.
6. **Location-level drift** — for each mappable rule, `same file:line` overlap % (the 1–98% signal).
7. **Finding-quality classification** — actionable-quality vs style-opinion vs formatter-domain.
8. **Timing** — cold-cache, all runs.
9. **Artifacts** — `parity/<A>/json/{baseline,max}.json` + out/err + configs.
10. **Report** — `parity/parity-<A>-vs-biome.md`.
11. **GATE** — explicit `no more activities for <A> vs Biome` before next pair.

### Tool-class adaptations

| Class | Tools | How the template adapts |
| --- | --- | --- |
| **Linter** | oxlint, eslint, standard, ts-standard, deno lint | full template as above (rules + findings + superset + drift) |
| **Formatter** | prettier, dprint, deno fmt, bun | no "rules" — replace steps 1–2 with **files-would-reformat** count + **location diff**; compare against Biome format drift (1,746 files); report per-file agreement % and style-config deltas (quote/semi/width) |
| **Type-checker** | tsc | complementary category — no lint superset; capture type-error baseline (dual-version per v13), and **overlap** with Biome type-aware nursery + `noUnusedLocals`/`noUnusedParameters` intersection |
| **Runtime probe** | bun | if no deterministic check-mode exists → record "no comparable gate", exclude from scoring, still gated closed |

### Per-pair deliverable shape (`parity-<A>-vs-biome.md`)

Fixed sections: Run Stats · Within-tool superset · Cross-tool coverage (G⊇X, J-vs-B) · Semantic map table · Location drift table · Finding-quality split · Timing · Verdict inputs. Same shape as `superset-analysis.md` + `parity-oxlint-vs-biome.md` so pairs are directly comparable in the final matrix.

## oxlint CRA Baseline Hardening + CI Wiring (new — v16)

This workstream hardens the repo's **oxlint** configuration into a
CRA-faithful, industry-standard baseline, arranges the commits for
maximum human legibility (in-place-edit diffs), and wires a GitHub
Actions gate. It is presentational/tooling only — **no application
behavior and no lint outcome changes** (oxlint findings held constant at
**1,394** = 1,393 warnings + 1 error across all steps).

### Rationale — why a CRA-shaped oxlint config

- Create React App (CRA5) has **no official oxlint configuration**; CRA
  lints internally via ESLint using `eslint-config-react-app` (already
  declared in `package.json` `eslintConfig`).
- Goal was **100% resemblance** to `eslint-config-react-app`. That is not
  fully attainable on this repo's toolchain, so the rule was: **match CRA
  exactly where possible, otherwise take the minimum severity/coverage
  that still meets-or-exceeds ESLint** on each mappable rule.
- Result: **1,394 oxlint findings ≥ CRA's 1,361** — at or above CRA on
  every mappable rule (no-unused-vars, exhaustive-deps, eqeqeq,
  rules-of-hooks, anchor-is-valid all exact/superset). The **sole gap** is
  `react/jsx-pascal-case` (33 `MRT_*` components): that rule requires
  oxlint 1.19 → Node ≥20.19, but the repo is pinned to **Node 18.20.8**
  (`mise.toml`), capping oxlint at 1.16. `eslint-config-react-app` remains
  the source of truth for that one rule until a Node upgrade — consistent
  with the `decision-final-toolchain.md` "ESLint react-app is the
  MANDATORY CRA floor" ruling.

### Baseline adoption

- The CRA-aligned `.oxlintrc.json` is adopted as **the oxlint baseline**.
- It was **already wired into npm scripts** — no script change needed for
  wiring: `lint: oxlint`, `lint:fix: oxlint --fix`. Bare `oxlint`
  auto-discovers `.oxlintrc.json` at the project root (no `-c` flag), so
  `npm run lint` → the baseline → 1,394 findings.
- Removed the **redundant oxlint test script** (`lint:tests`, a
  personal-branch-only leftover) — dead wiring, no behavior impact.

### Industrialization

Tuned the config to an industry-standard shape for a CRA project (still
strict JSON, comment-free): rules **grouped by plugin** (core ESLint
first, then `import` / `jsx-a11y` / `react` / `typescript` / `unicorn`,
alphabetical within each group → one deterministic insertion point per
new rule, minimal merge conflicts), `plugins` and `env` sorted, trailing
newline added (kills "No newline at end of file" markers).

### Commit arrangement technique (human-legible in-place diffs)

The changes were arranged into **three commits** purely to make the
change-set easy for a human to read — specifically to render the severity
changes as **in-place edits** instead of split delete/add blocks. **None
of these arrangements change any value or file outcome** (findings
constant at 1,394; identical rule key-set and severities at the end):

1. **`553c7419` — `style(oxlint): add blank-line separators around 4
   rules`** — inserts a blank line immediately above and below the four
   rules whose severity later flips to `off` (`no-unused-vars`,
   `typescript/no-wrapper-object-types`,
   `unicorn/no-useless-fallback-in-spread`, `unicorn/no-useless-spread`).
   +8 blank lines only; oxlint ignores blank lines, findings unchanged.
   This gives each of those rules stable context neighbours.
2. **`d14231dc` — `chore(lint): align oxlint config with CRA
   eslint-config-react-app`** — the actual content change (enable
   react/jsx-a11y/import plugins + env, adopt react-app severities,
   remove non-CRA rules). Because of commit 1's anchors, all four
   `warn→off` severity changes render as clean **in-place** edits.
3. **`8da04d44` — `style(oxlint): group rules by plugin and normalize
   formatting`** — removes the commit-1 blank-line anchors and applies the
   industrial group+sort+trailing-newline normalization. Behavior-neutral.

**Invariants enforced on every commit:** only `.oxlintrc.json` staged
(the parity-eval noise — `package.json`, `package-lock.json`,
`biome.json`, `biome-max.json` — excluded and left in the working tree);
valid JSON; `oxlint` findings = 1,394; no push. Branch
`review/main_aes-1144` is now ahead of `origin/main_aes-1144` by these 3
commits (unpushed).

> Method note: the "blank-line anchor" arrangement is a legitimate
> presentation device (blank lines are semantically inert in JSON). It was
> chosen over a 2-commit add-then-adjust split (rejected earlier) and over
> gaming the diff with fake content. The final normalization commit
> removes the anchors, so the permanent config carries none of the
> scaffolding.

### CI wiring (next — pending failure-policy decision)

Add a GitHub Actions workflow that runs the oxlint baseline:

- **Triggers:** `on: push` (all branches) + `on: pull_request` — the
  CI-side equivalent of "every push / every PR". *"Every commit"* in the
  literal per-commit sense is a **local pre-commit hook** (repo has
  git-hook skills) — offered as an optional companion, not part of the
  Actions workflow.
- **Node provisioning:** **`jdx/mise-action@v2`** (user-selected) — reads
  `mise.toml` and installs `node@18.20.8` exactly, zero version drift,
  faithful to the repo's mise-first setup. (Alternative `actions/setup-node`
  pinned was rejected to avoid duplicating the version SSOT.)
- **Install:** `npm ci` against the committed lockfile (reproducible).
- **Lint step:** `npm run lint` (auto-discovers `.oxlintrc.json`);
  optionally `oxlint -f github` for inline PR-diff annotations.
- **Failure policy — OPEN DECISION.** The baseline is **not green**:
  `npm run lint` exits **1** because of **1 real error**
  (`react-hooks/rules-of-hooks`, `useCallback` in an anonymous function at
  `src/Pages/Trading/PaperTrading/TradeCaptureAPI/IceExhcnageTrades.tsx:855`)
  plus 1,393 warnings. Options presented: (a) block on errors + freeze
  warnings via `--max-warnings=1393` and fix the one error (green,
  ratchet-friendly, touches 1 source file); (b) block on errors only (red
  until the error is fixed); (c) report-only / non-blocking (always green,
  annotations only). oxlint 1.16 supports `--max-warnings`,
  `--deny-warnings`, `--quiet`, and `-f github|gitlab|json|junit|...`.
- **Landing scope:** committing the workflow to `review/main_aes-1144`
  activates it for that branch's pushes and PR #713; **repo-wide** effect
  requires it to reach the default branch (`main`) via merge.

### Relationship to the parity workstream

This baseline hardening is **independent of** the still-open oxlint↔Biome
parity gate. The CRA-aligned oxlint config is the *current wired linter*;
the parity evaluation (and the `decision-final-toolchain.md` architecture:
ESLint react-app floor + Biome + oxlint supplement + tsc) may later change
which tool owns which role. Wiring CI for the present `npm run lint` does
not pre-empt that decision — it just gates on today's baseline.

### Task / gate deltas

- **Done:** oxlint CRA baseline finalized (1,394 findings), industrialized
  (grouped/sorted/trailing-newline), `lint:tests` removed, 3 legibility
  commits landed (`553c7419`, `d14231dc`, `8da04d44`), only
  `.oxlintrc.json` committed each time.
- **Open:** CI failure-policy decision → then author
  `.github/workflows/lint.yml` (mise-action + `npm ci` + `npm run lint`),
  commit to `review/main_aes-1144`; optional local pre-commit hook; the
  3 oxlint commits + workflow remain unpushed pending review.

### Update — CI workflow landed + 3 commits pushed (new — v17)

**CI workflow landed:** `9da79106 ci(lint): run oxlint on push and pull_request via mise` — `.github/workflows/lint.yml` (`on: push` + `pull_request` + `workflow_dispatch`; `jdx/mise-action@v2` reads `mise.toml` → Node `18.20.8`; `npm ci`; `npx oxlint -f github` annotated report `continue-on-error` + gate `npm run lint -- --max-warnings=1393`). Only `.github/workflows/lint.yml` staged (parity noise excluded). Valid YAML, `actionlint` skipped (not installed). Workflow activates for `review/main_aes-1144` and PR #713; repo-wide needs merge to `main`.

**Push status (you pushed):** 3 commits now on `origin/review/main_aes-1144` — `553c7419` (blank-line anchors) → `d14231dc` (CRA align) → `8da04d44` (group+normalize). `9da79106` (lint.yml) remains `0↔1` ahead of `origin/review/main_aes-1144` pending your authorization. Branch still tracks `origin/main_aes-1144` (`[ahead 4]` vs that ref) — push target is `review/`-prefixed.

**Gate still red by design:** `--max-warnings=1393` freezes warnings; the 1 `react-hooks/rules-of-hooks` error at `IceExhcnageTrades.tsx:855` still fails the gate until fixed (or policy relaxed to report-only / block-errors-only). `DECISION: failure policy` remains open in `task.md`.

**Housekeeping:** corrected `v16` title (`v15` → `v16`) after verbatim-superset (title preservation); corrected `task.md` `.github` claim (`NO .github` → `already has .github/workflows`).

**Invariants:** all 4 commits on `review/main_aes-1144` only touch their intended files (`553c7419`/`d14231dc`/`8da04d44`: `.oxlintrc.json` only; `9da79106`: `.github/workflows/lint.yml` only); oxlint findings constant `1394` across the 3 oxlint commits; lint workflow red is intentional ratchet.
