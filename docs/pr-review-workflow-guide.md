<!-- title: PR Review Workflow Guide (gh pr view + github-repo-commit-fetch + git-commit-comparison-audit) -->

# GitHub Pull Request Review Workflow: Complete Practical Guide

## 1. Purpose of This Document

This document is the **single source of truth (SSOT)** for the standard
workflow used to review a colleague's (or associate's) GitHub Pull Request
(PR):

| Stage | Tool / Skill | What it does |
| :--- | :--- | :--- |
| 0 | Pre-flight (rules-mandated) | Auth check, repo context, PR discovery, permission gate |
| 1 | `gh pr view <n>` | Read the PR's metadata, head SHA, base branch, diff stats |
| 1.5 | `gh pr checks <n>` | Verify CI baseline automation + Conventional Commits |
| 2 | `github-repo-commit-fetch` | Pull the PR's commit series and file contents from GitHub **without cloning** |
| 3 | `git-commit-comparison-audit` | Compare base vs. head locally and isolate the **meaningful** diff |
| 4 | Manual testing (when applicable) | Behavioral verification of visual/stateful features |
| 5 | `gh pr review <n>` | Deliver the structured verdict + explicit handoff |

The document is written in four tiers, from plain English to full technical depth:

| Section | Audience | Reading time |
| :--- | :--- | :--- |
| [Section 2](#2-for-non-technical-readers-plain-english) | Non-technical stakeholders | 3 minutes |
| [Section 3](#3-for-complete-beginners-first-run) | First-time users ("noobs") | 10 minutes |
| [Section 4](#4-the-standard-workflow-in-full-technical-detail) | Developers / reviewers | 20 minutes |
| [Section 5](#5-end-to-end-annotated-walkthrough) | Everyone, as reference | 5 minutes |

> **Why this workflow exists:** a raw `git diff` between two branches is a
> firehose. The pipeline filters out rewrite noise (rewording,
> cherry-picks, renames, rebases) mechanically and lands the reviewer exactly
> on the commits that carry real semantic change.
---

## 2. For Non-Technical Readers (Plain English)

### 2.1 What is a Pull Request?

Think of a team working on one shared document (the code repository). A Pull
Request (PR) is a **proposed change** that one person (the author) wants to
merge into the shared copy. Before the change is accepted, other people (the
reviewers) must check it. The PR is the container that holds:

* the proposed change (the **diff**),
* the list of individual changes that make it up (the **commits**),
* the conversation about the change (comments and reviews),
* the final decision: merge (accept) or close (reject).

---

### 2.2 What is a "Review"?

A review is a structured check of the proposed change before it reaches the
shared copy. The reviewer answers four questions:

1. **Is the change correct?** Will it do what the author says it does?
2. **Is the change safe?** Does it break anything else?
3. **Is the change minimal?** Does it do one thing, and only that thing?
4. **Is the change well-explained?** Can the next person understand it?

The workflow in this document helps you answer those questions faster and with
more confidence than reading the change line by line in a browser tab.

### 2.3 What do the stages do, in one sentence each?

| Stage | Plain-English meaning |
| :--- | :--- |
| Pre-flight | "Check the doors are unlocked and pick the one task to work on." |
| `gh pr view` | "Show me the cover page of the change: who, what, when, how big." |
| `gh pr checks` | "Did the automatic quality robots already pass or fail this change?" |
| `github-repo-commit-fetch` | "Download the change's table of contents and read any page of it, without downloading the whole book." |
| `git-commit-comparison-audit` | "Spread the original and the proposed version side by side and mark which parts are truly different." |
| Manual testing | "Actually click through the changed screens to see if they behave as promised." |
| `gh pr review` | "Leave the verdict on the change's cover page for everyone to see." |

### 2.4 The key insight: "same-looking" is not "same"

Git stores changes with metadata (who wrote it, when, a fingerprint). When an
author rewrites history (a normal practice), the metadata changes even though
the *content* is identical. A naive review tool reports a huge difference where
there is none. Stage 3's job is to detect this and tell you: "these two
versions are the same content, only the paperwork differs" — so you spend your
review time only on genuine changes.

---

## 3. For Complete Beginners (First Run)

### 3.1 What you need before you start

| Requirement | How to check | How to install |
| :--- | :--- | :--- |
| `gh` (GitHub CLI) | `gh --version` | `brew install gh` (macOS) |
| GitHub login | `gh auth status` | `gh auth login` |
| `git` | `git --version` | `brew install git` |
| `python3` | `python3 --version` | preinstalled on macOS |
| `pwsh` (PowerShell) | `pwsh -v` | `brew install --cask powershell` |

If any check fails, stop and fix it first — the workflow assumes all five.

> **Tip for this workspace:** skills and scripts live under
> `.agents/skills/`. The scripts we call are pure Python and need no extra
> packages.

### 3.2 Glossary (words you will meet)

| Word | Meaning |
| :--- | :--- |
| **Repository (repo)** | The project's shared folder, versioned by Git, hosted on GitHub. |
| **Clone** | A local copy of a repository on your machine. |
| **Commit** | A single saved change, with a message describing it. |
| **Branch** | A movable label pointing at a commit; branches let work proceed in parallel. |
| **Base branch** | The branch a PR wants to merge *into* (usually `main` or `master`). |
| **Head branch** | The branch that carries the PR's proposed changes. |
| **Head SHA (`headRefOid`)** | The exact fingerprint of the latest commit on the head branch. |
| **Ref** | A named pointer to a commit: a branch name, a tag, or a full 40-char SHA. |
| **Diff** | The added/removed lines between two versions. |
| **Patch-ID** | A fingerprint of the diff *content only*, ignoring metadata. |
| **Tree** | The full byte-level snapshot of all files at a commit. |
| **SHA** | A 40-character hex fingerprint uniquely identifying a commit. |
| **Merge** | Accepting the PR's changes into the base branch. |
| **Rebase / cherry-pick** | History operations that replay changes onto a different base; they keep content but change metadata. |
| **Fork** | A personal copy of someone else's repo; PRs from forks are common. |

### 3.3 Your very first run (copy-paste)

Assume the PR number is `42` and the repo is `acme/awesome-app`:

```bash
gh pr view 42 --repo acme/awesome-app
```

Expected output shape (yours will differ in values):

```text
Pull request #42
  Title: Fix login timeout on slow networks
  Branch: acme/awesome-app:main <- fix-login-timeout
  State: OPEN
  Created: 2 weeks ago
  Updated: 1 day ago
  Author: jane-dev
  +120 -30 in 8 files
```

Three things to note in this output:

1. The **state** is OPEN (still reviewable).
2. The arrow `main <- fix-login-timeout` names the base and head branches.
3. The `+120 -30 in 8 files` line is the **size** — your first review signal.

Then fetch the commit list:

```bash
python3 .agents/skills/github-repo-commit-fetch/scripts/list-commits.py \
    --repo acme/awesome-app --sha <headRefOid> --limit 10
```

You will get a JSON list where each entry has `sha`, `short`, `date`,
`author`, and `message`. If you see **one** commit: the PR is a single lump of
change (harder to review). If you see **several** meaningful commits: the PR is
well-structured (easier to review one at a time).

### 3.4 Common beginner errors

| Error | What happened | Fix |
| :--- | :--- | :--- |
| `gh: not found` | `gh` not installed | `brew install gh` |
| `Please re-authenticate` | Login expired | `gh auth login` |
| `404` from `gh api` | Wrong repo name, or you lack access | Confirm `owner/name`; check `gh repo view owner/name` |
| `file not found` for scripts | Wrong working directory | Run from the repo root: `/Users/dk/lab-data/ai-suite` |
| JSON "no such key" | The ref you passed has no commits (e.g., a raw file ref) | Pass a branch name or commit SHA, not a file path |

### 3.5 When you are stuck, ask the machine

```bash
gh pr view --help
gh api --help
python3 .agents/skills/github-repo-commit-fetch/scripts/list-commits.py --help
```

---

## 4. The Standard Workflow in Full Technical Detail

### 4.0 Pre-flight (Phases -1 and 0, per `git-operation-rules.md`)

#### 4.0.1 Phase -1: environment validation

Before ANY `gh`/`git` command, verify authentication and tooling:

```bash
gh auth status       # must show authenticated; else gh auth login
git status           # understand the working tree before any fetch
```

> **Multi-account note (personal account → company private repo):**
> If `gh auth status` shows a personal account but the PR is in a company
> private repo, you will hit 403 (wrong identity). The
> `git-github-auth-fallback` skill provides these paths:
>
> * **Path F (macOS, recommended)**: `git config --global credential.useHttpPath true`,
>   flush keychain, push → macOS prompts for company PAT per-repo-path.
> * **Path D**: `gh auth login` (sign in as company account) +
>   `gh auth setup-git` — `gh` manages credentials for both API and git.
> * **Path B (non-TTY)**: Temporarily embed PAT in remote URL,
>   push, immediately revert (never commit the URL).
> * **Path C**: Switch remote to SSH (`git@github.com:org/repo.git`).
>
> See `git-github-auth-fallback` skill §2–§3 for diagnosis + remediation.
> **Passing PAT to `gh` CLI (non-interactive):**
> `gh` reads auth from these sources in precedence order:
>
> 1. `GH_TOKEN` (preferred for fine-grained PATs)
> 2. `GITHUB_TOKEN`
> 3. Stored credentials (`gh auth login` / `gh auth setup-git`)
>
> **Usage:**
>
> ```bash
> # Env var (session-only, no disk write):
> export GH_TOKEN=<company-pat>
> gh pr list --repo owner/name
>
> # Or inline per command:
> GH_TOKEN=<company-pat> gh pr view 42 --repo owner/name
>
> # Or pipe to `gh auth login --with-token` (stores in credential helper):
> echo <company-pat> | gh auth login --with-token
> ```
>
> > **⛔ Never** pass PAT directly on CLI as argument — it leaks to shell history.
> > Use env vars or `--with-token` stdin only.
> **Fallback ladder** (per `github-cli-permission-rules.md` §4 — the approval
> gate applies to every fallback equally):
>
> | Failure | Defer to |
> | :--- | :--- |
> | `gh` not installed / not on PATH | `github-rest-api-fallback` skill §3 |
> | `gh auth status` → 401/403/Bad credentials | `git-github-auth-fallback` skill §2 (classify error before retry) |
> | Terminal tool unavailable — **GitHub Copilot (VS Code) only**: `run_in_terminal` is a Copilot agent-mode tool, not an opencode tool; opencode always has a native `bash` tool, so this fallback applies only when reviewing under Copilot | `terminal-fallback-via-vscode-tasks` skill §3 |
>
> #### 4.0.2 Git Mutation Gate (mandatory for ALL mutating git operations)
>
> **Rule:** Any git command that mutates local refs or the object database
> requires explicit user authorization. Dry-run inspection commands are
> auto-allowed (no gate).
>
> **Mutating operations (require gate):**
>
> > * `git clone` (full fetch + checkout)
> > * `git fetch` / `git fetch --prune` (moves/deletes `refs/remotes/*`)
> > * `git pull` (fetch + merge/rebase — touches local branches)
> > * `git merge` / `git rebase` / `git cherry-pick` (rewrite local history)
> > * `git push` (remote mutation — gated by `github-cli-permission-rules.md`)
> > * `git gc --prune` / `git prune` (object DB cleanup)
>
> **Inspection commands (auto-allowed, no gate):**
>
> > * `git fetch --dry-run` / `git fetch --dry-run --prune`
> > * `git ls-remote <remote>`
> > * `git remote show <remote>`
> > * `git for-each-ref refs/remotes/<remote>/`
> > * `git merge --dry-run` / `git rebase --dry-run` /
> >   `git cherry-pick --dry-run`
> > * `git diff` / `git log` / `git status` / `git branch -r` /
> >   `git symbolic-ref`
>
> **Gate workflow:**
>
> > 1. Run the dry-run inspection first (auto-allowed).
> > 2. Present the output to the user.
> > 3. Ask: "Do you approve this mutating command? Yes/No."
> > 4. Only on explicit "Yes", execute the real command.
>
> **Reference:** `git-operation-rules.md` §3 — fetch/clone/pull are mutating;
> `--dry-run` is read-only.
>
#### 4.0.3 Phase 0: establish repository context

> **⛔ Most common mistake.** The PR may be filed against a **different**
> repository than the code you expect. A PR is always filed against exactly
> one repo; confirm which one before running anything. `gh pr view` without
> `--repo` uses the current directory's remote, which may be wrong.

```bash
gh repo view --json nameWithOwner --jq .nameWithOwner
```

* **Nested repositories**: if the PR lives in a nested repo (e.g., `acers-web`
  is a separate git repo inside the `oleovista-acers` workspace), `cd` into
  that sub-directory BEFORE any `git`/`gh` command.
* **Repos outside the assistant workspace**: the repo may live outside the
  ai-assistant's working directory entirely (e.g., a sibling workspace). Do
  NOT `cd` out of the assistant workspace — use `git -C <path> <cmd>` to run
  git against the external repo from where you are (e.g.
  `git -C ~/lab-data/oleovista-acers/acers-web status`), and pass
  `--repo owner/name` to `gh` instead of relying on the current directory.
* **Ambiguity**: if multiple repos are candidates, ask the user which one
  ("`project-a/` or `project-b/`?") before proceeding.
* **Default branch**: NEVER assume `main`. Discover it:

```bash
git branch -r                    # list remote branches
git symbolic-ref refs/remotes/origin/HEAD   # authoritative default
```

* **Always fetch/pull with care**: Before any review, ensure local refs are
  current — run the gated fetch/pull (Stage 3 precondition §4.4.1):
  `git fetch --dry-run` → user approval → `git fetch` / `git pull`.
  Stale refs = stale review.

If the PR lives elsewhere, pass `--repo owner/name` to every command in this
document.

#### 4.0.4 Discovery: one PR at a time (per `github-pr-management-rules.md`)

Review PRs strictly SEQUENTIALLY — never multitask across PRs:

```bash
# Default: open PRs only
gh pr list --repo owner/name

# Include closed/merged PRs
gh pr list --repo owner/name --state all
# Or specific states:
gh pr list --repo owner/name --state closed
gh pr list --repo owner/name --state merged
```

1. Pick exactly **ONE** PR from the list.
2. Review it to completion.
3. **Explicit handoff**: notify the user and STOP — do not proceed to the
   next PR until the user explicitly confirms ("done", "next", "approved").

#### 4.0.5 Mandatory permission gate (per `github-cli-permission-rules.md`)

The rule (§2–§3) requires explicit approval for **every** `gh` command. In
practice the assistant (opencode/Copilot) auto-allows **non-destructive**
`gh` commands (read-only: `gh pr view`, `gh repo view`, `gh api GET`, etc.)
but **requires explicit confirmation for destructive/write commands**
(`gh pr create`, `gh pr review`, `gh api PATCH/POST/DELETE`, `gh secret set`,
`gh repo edit`, etc.). This is a pragmatic relaxation — the rule is the
strict baseline; the assistant's behavior is the operational norm.

**Protocol for every `gh` command:**

1. State the exact command and its rationale.
2. If destructive → ask: "Do you approve this command? Yes/No."
   If non-destructive → proceed (auto-allowed), but still state the command
   and rationale for transparency.
3. On "Yes" (destructive) or auto-proceed (non-destructive), execute.

**Security SSOT** (per `github-pr-management-rules.md` §1): the `gh` CLI is
the ONLY single source of truth for PR metadata. NEVER use web search or URL
content readers for PR links/branch details, and NEVER embed a Personal
Access Token in any artifact, log, or transcript.

### 4.1 Stage 1 — `gh pr view <n>`: orient on the PR

#### 4.1.1 Human-readable view

```bash
gh pr view <n> [--repo owner/name]
gh pr view <n> --comments              # include the comment thread
gh pr view <n> --repo owner/name --json ...   # machine-readable
```

#### 4.1.2 Machine-readable view (the one reviewers script against)

```bash
gh pr view 42 --repo acme/awesome-app --json \
    number,title,state,baseRefName,headRefName,headRefOid,isCrossRepository, \
    mergeable,additions,deletions,changedFiles,author,createdAt,updatedAt,url
```

| JSON field | Type | Why you need it |
| :--- | :--- | :--- |
| `number` | int | The PR id used everywhere else |
| `title` | string | First comprehension check |
| `state` | string | `OPEN`, `DRAFT`, `MERGED`, or `CLOSED`; skip non-OPEN PRs |
| `baseRefName` | string | Branch the PR merges into (default `main`) |
| `headRefName` | string | Branch carrying the changes |
| `headRefOid` | SHA | **The exact commit under review** — pin all later fetches to this |
| `isCrossRepository` | bool | True = head lives in a **fork**; clone strategy changes |
| `mergeable` | string | `MERGEABLE`, `CONFLICTING`, or `UNKNOWN` — base may have drifted |
| `additions` / `deletions` | int | Diff size signals |
| `changedFiles` | int | Scope signal |
| `author` | object | Who wrote it (login) |
| `createdAt` / `updatedAt` | ISO date | Age and recency of activity |
| `url` | string | For browser handoff |

#### 4.1.3 Decision points after Stage 1

| Observation | Verdict | Action |
| :--- | :--- | :--- |
| `state == OPEN` | Review normally | Continue to Stage 1.5 |
| `state == MERGED` | Post-merge review | Use `gh pr comment` + `gh api /repos/owner/repo/pulls/N/reviews` for line comments; document findings in follow-up issue |
| `state == CLOSED` (unmerged) | Do not review | Stop, or read as history |
| `changedFiles > ~25` and one commit | Large unbroken change | Plan per-file review; consider asking author to split |
| `additions + deletions > ~2000` | Large diff | Triage by file before reading hunks |
| `mergeable == CONFLICTING` | Base drifted | Note it in review; still review content |
| `isCrossRepository == true` | Fork head | Use Stage 2 (no-clone) heavily; clone needs extra fetch |

#### 4.1.4 Reviewer assignment check (per `ci-cd-rules.md` §239, `github-actions-workflow-rules.md` §10.6)

The pipeline auto-assigns reviewers via `.github/CODEOWNERS` (path-based)
and/or a GHA round-robin action. Verify in Stage 1:

```bash
gh pr view <n> --repo owner/name --json reviewRequests --jq '.reviewRequests[].login'
```

| Observation | Action |
| :--- | :--- |
| No reviewers assigned | **We are reviewing → add ourselves**: `gh pr edit <n> --repo owner/name --add-reviewer @me` |
| Wrong team assigned | Check CODEOWNERS patterns; flag in review comment |
| Reviewers assigned correctly | Proceed |

### 4.2 Stage 1.5 — CI status verification (per `ci-cd-rules.md`)

Every PR is expected to pass the org's **baseline automation**: linting,
formatting, unit tests, type checks, and security scans (`npm audit`, Snyk),
with coverage uploaded to Codecov/Coveralls. Verify the PR's checks BEFORE
reading the diff — a PR with failing checks is blocked regardless of content
quality:

```bash
gh pr checks <n> --repo owner/name
```

| Observation | Verdict | Action |
| :--- | :--- | :--- |
| Any check failing / pending | Do not approve | Report the failing check + link in review; wait for re-run |
| All checks passed | Proceed | Continue to Stage 2 |
| No checks configured | Proceed, note it | Flag missing CI coverage in the review comment |

**Build failure handling protocol (per `ci-cd-rules.md` §181-189):**
When a check fails, the CI/CD pipeline **automatically**:

1. Sends a WhatsApp message to the committer and team.
2. Creates a GitHub issue with the full build logs, commit SHA,
   branch name, and error context; assigns the committer.
3. Comments on the PR with a link to the issue and logs.

As a reviewer, you will see the failure in `gh pr checks`,
the PR comment with the issue link, and the auto-created issue.
Do **not** approve until the author re-runs and all checks pass.

**Unit tests / Code coverage / Regression tests — review checklist:**

| Category | What to verify | How to check |
| :--- | :--- | :--- |
| **Unit tests** | New/changed code has tests; all tests pass | `gh pr checks` → unit test job; look for test count, pass rate |
| **Code coverage** | Coverage meets threshold; no significant drop | Codecov/Coveralls badge on PR; `gh api /repos/owner/repo/pulls/N/checks` for coverage %; flag drops >1-2% |
| **Regression tests** | Existing test suite passes (no regressions) | `gh pr checks` → all test jobs green; if flaky tests exist, note in review |
| **Type checks** | `tsc` / `mypy` / `flutter analyze` pass | Part of CI; verify in `gh pr checks` |
| **Linting/formatting** | `ruff` / `eslint` / `prettier` / `dart format` pass | Part of CI; verify in `gh pr checks` |

**Coverage drop protocol:**

* If coverage drops >2% on changed files → request author to add tests
* If overall coverage drops >1% → flag as review finding
* If no coverage tool configured → flag "Missing coverage integration" in review

**Flaky test protocol:**

* If tests pass on re-run → note as flaky in review; author should fix
* If tests consistently fail → block approval until fixed

Also verify the PR's commits follow **Conventional Commits** (org-wide
adoption per `ci-cd-rules.md`): subject shape `type(scope): description`,
imperative mood. Non-compliant subjects (e.g., GitHub Web UI's `Create X.md`)
are a review finding — see the `git-commit-message-bulk-reword` skill for the
remediation path.

### 4.3 Stage 2 — `github-repo-commit-fetch`: pull commits and files without cloning

**Skill:** `.agents/skills/github-repo-commit-fetch/SKILL.md`

**Why not clone?** The skill is built for the *no-clone* case: PR heads in
forks, repos you do not work in daily, or quick triage. All reads go through
`gh api` wrapped in pure-stdlib Python (UTF-8 safe, JSON out, exit codes
0/1/2), so there is no `curl`/`jq` quoting hell and no disk bloat.

#### 4.2.1 Script catalogue

| Script | Purpose | Required args |
| :--- | :--- | :--- |
| `list-commits.py` | N most recent commits on a branch/ref, optional path filter | `--repo`, optional `--sha`, `--limit`, `--path` |
| `commit-details.py` | One commit's metadata + changed files with +/- counts | `--repo`, `--sha` (`--files-only` for bare names) |
| `fetch-file-at-ref.py` | Stream one file's exact content at a ref to disk | `--repo`, `--ref`, `--path`, `--out` |

Convenience variable used in all examples below:

```bash
SCRIPTS_DIR=.agents/skills/github-repo-commit-fetch/scripts
```

#### 4.2.2 Pull the commit series

```bash
python3 "$SCRIPTS_DIR"/list-commits.py \
    --repo acme/awesome-app --sha <headRefOid> --limit 20
```

Output (abridged, actual is JSON):

```json
[
  {"sha": "9f3c2a1...", "short": "9f3c2a1", "date": "2026-07-30T09:12:00Z",
   "author": "jane-dev", "message": "fix: retry login when network stalls"},
  {"sha": "b7e90d4...", "short": "b7e90d4", "date": "2026-07-30T08:55:00Z",
   "author": "jane-dev", "message": "test: add login timeout integration tests"}
]
```

**Review use:** decide the review granularity. One commit = review the whole
PR as a unit. Multiple commits = review each commit individually (and Stage 3
can walk them pairwise).

#### 4.2.3 Pull the file surface of a single commit

```bash
python3 "$SCRIPTS_DIR"/commit-details.py \
    --repo acme/awesome-app --sha 9f3c2a1 --files-only
```

Output:

```text
src/auth/login.ts
src/auth/timeout.ts
tests/login-timeout.test.ts
```

**Review use:** spot scope creep immediately — a PR titled "fix login timeout"
should not touch `docs/`, `infra/`, or unrelated modules.

#### 4.2.4 Pull an actual file's content at the reviewed SHA

```bash
python3 "$SCRIPTS_DIR"/fetch-file-at-ref.py \
    --repo acme/awesome-app --ref <headRefOid> \
    --path src/auth/login.ts --out scratch/pr-42-login.ts
```

Output:

```text
OK: src/auth/login.ts (4821 bytes) from https://api.github.com/...
```

**Review use:** read files that do not exist in your local checkout, or
inspect the *exact reviewed version* even after the branch moved on. The
script handles redirects, parent-dir creation, and byte-safe writes.

#### 4.2.5 Why Stage 2 alone is not enough

Stage 2 answers "what changed and what does it look like" but not "is this
change equivalent to something I have seen before". Detecting rewrite-mirrors
(content-equal commits with different metadata) requires local Git object
comparison — that is Stage 3's job.

### 4.4 Stage 3 — `git-commit-comparison-audit`: the meaningful diff

**Skill:** `.agents/skills/git-commit-comparison-audit/SKILL.md`

#### 4.3.1 Precondition: local objects (with mandatory gates)

Stage 3 needs Git objects **on disk**. Bringing the PR head into your local
clone is a `git fetch` — which per `git-operation-rules.md` §3 requires
explicit user confirmation. Protocol:

1. `git status` first (understand the working tree).
2. Check for remote changes WITHOUT fetching, then confirm with the user:

   ```bash
   git fetch --dry-run origin          # or: git ls-remote origin
   ```

3. Only after explicit confirmation, bring the PR head local:

   ```bash
   # Option A (recommended): checkout the PR into a local branch
   gh pr checkout 42

   # Option B: fetch the pull-request ref without a checkout
   git fetch origin refs/pull/42/head

   # Option C: fork head — first add the fork as a remote
   git remote add jane git@github.com:jane-dev/awesome-app.git
   git fetch jane fix-login-timeout
   ```

After any of these, you have both SHAs locally. Discover the base SHA
programmatically — never assume `main`:

```bash
BASE_REF=$(git symbolic-ref --short refs/remotes/origin/HEAD | sed 's#origin/##')
git rev-parse "origin/$BASE_REF"    # base SHA
git rev-parse HEAD                  # head SHA (after checkout)
```

#### 4.3.2 Level 1: the comparison orchestrator

```bash
python3 .agents/skills/git-commit-comparison-audit/scripts/compare.py <baseSHA> <headSHA>
```

This orchestrates the detail-audit script for each SHA and produces:

1. **Side-by-side metadata table** — Author + AuthorDate shown separately from
   Committer + CommitDate, so rebases, cherry-picks, and `filter-repo`
   rewrites are visible.
2. **Reachability audit** — which branches/tags contain each commit.
3. **Submodule pointer audit** — mismatched submodule pointers, with a
   recursive detail-audit *inside* the submodule when they differ.

#### 4.3.3 Level 2: content-equivalence check (the heart of the skill)

When the two commits have **different SHAs but identical author identity and
dates** — the signature of a rewrite-mirror, cherry-pick, or filter-repo run —
you must run the equivalence check to decide content-equal vs. divergent:

```bash
pwsh -File .agents/skills/git-commit-comparison-audit/scripts/equivalence-check.ps1 \
    -Sha1 <baseSHA> -Sha2 <headSHA>
```

The primitive runs five analyses:

| # | Analysis | Command | What it proves |
| :--- | :--- | :--- | :--- |
| 1 | **Patch-ID** | `git show <sha> \| git patch-id --stable` | Diff content fingerprint, independent of SHA, parent, author, dates |
| 2 | **Tree SHA** | `git rev-parse <sha>^{tree}` | Byte-level tree identity |
| 3 | **Tree diff** | `git diff --stat <sha1> <sha2>` | File-level delta (only when trees differ) |
| 4 | **Subjects & bodies** | `git log -1 --format='%s%n%n%b'` | Message-level delta |
| 5 | **Refinement check** | normalised line diff | Detects deterministic kebab-case rewrites |

#### 4.3.4 The interpretation matrix

| Patch-ID | Tree SHA | Refinement | Verdict | Action |
| :--- | :--- | :--- | :--- | :--- |
| = | = | n/a | **CONTENT-EQUIVALENT** | Pure reword; no code review needed on this pair |
| = | != | n/a | **PATCH-EQUIVALENT BUT TREES DIFFER** | Cherry-pick across disjoint histories; equivalent only on the diff axis |
| != | = | n/a | (rare) | Trees match but patches differ — inspect parents |
| != | != | MATCH | **REFINED EQUIVALENT** | Intentional kebab-case normalisation |
| != | != | NO MATCH | **DIVERGENT** | True semantic delta — **the pair you actually review** |

The refinement check is intentionally conservative: it triggers only when
removed/added line counts are equal AND every pair matches after
normalisation. Any mixed delta falls through to DIVERGENT and needs human
review.

#### 4.3.4b Equivalence Findings Documentation (maximum detail)

For **every** equivalence verdict, document the following in the comparison
report. Do NOT skip any field — this is the forensic record.

| Finding | Required Documentation |
| :--- | :--- |
| **CONTENT-EQUIVALENT** (Patch-ID match, Tree match) | • Patch-ID value (both commits) • Tree SHA (both commits) • File list with per-file byte counts • Commit messages (subject + body) side-by-side • Author/Committer identity + timestamps table • Reachability: branches/tags containing each commit • Submodule pointers (if any) • Verdict rationale: "Pure reword — identical diff content, identical tree" |
| **PATCH-EQUIVALENT BUT TREES DIFFER** (Patch-ID match, Tree mismatch) | • Patch-ID value • Tree SHA (both — show they differ) • `git diff --stat` output • File list showing what files differ in tree but not in patch • Identify the cherry-pick source/target history divergence • Per-file byte comparison for files that exist in both trees • Verdict rationale: "Same patch applied to different base trees" |
| **REFINED EQUIVALENT** (Patch-ID mismatch, Tree mismatch, Refinement MATCH) | • Patch-ID values (show they differ) • Tree SHAs (show they differ) • Refinement normalisation rules applied (list each: kebab-case, file mode, permissions, etc.) • Line-by-line normalised diff showing every matched pair • Count of lines removed/added before vs. after normalisation • Files affected by normalisation • Verdict rationale: "Deterministic normalisation — no semantic change" |
| **SPLIT EQUIVALENT** (One legacy commit → two atomic commits) | • Original commit SHA + tree • Two new commit SHAs + trees • Tree equality proof: combined tree of two new = original tree • Per-file allocation: which files went to which new commit • Patch-ID comparison for each new commit vs. relevant subset of original • Verdict rationale: "Atomic split — no content added/removed" |
| **SPLIT REFINED EQUIVALENT** (Split + normalisation) | • All of SPLIT EQUIVALENT fields + REFINED EQUIVALENT normalisation details • Show normalisation applied within each split commit • Verdict rationale: "Atomic split with deterministic normalisation" |
| **DIVERGENT** (True semantic delta) | • Patch-ID values (mismatch) • Tree SHAs (mismatch) • Refinement result: NO MATCH + reason (line count diff / non-matching pair) • Full `git diff` output with context • Semantic classification: bug fix / feature / refactor / test / docs / config • Impact assessment: what behavior changed, what risks • Verdict rationale: "True semantic delta — requires human review" |
| **File mode / permissions changes** | • `git diff --summary` output showing mode changes (100644→100755 etc.) • Files affected • Whether mode change was intentional (executable bit for scripts) or accidental (Windows/macOS line-ending / umask drift) • Verdict: mode-only change = CONTENT-EQUIVALENT if no content delta; else DIVERGENT |
| **Kebab-case / naming normalisation** | • Original names vs. normalised names (full path list) • Files renamed, directories renamed • Whether normalisation was applied to tracked files only or includes ignored files • Cross-reference with `.gitattributes` / `git config core.ignoreCase` • Verdict: deterministic rename = REFINED EQUIVALENT |
| **Line ending normalisation (CRLF ↔ LF)** | • Files affected (from `git diff --check` or `git ls-files --eol`) • Whether `.gitattributes` / `core.autocrlf` config explains it • Byte-level comparison showing only line-ending bytes differ • Verdict: line-ending-only = REFINED EQUIVALENT (if config-consistent) |

**Mandatory report appendices** (always include):

1. **Raw data dumps** — full `git show --patch` for both commits, tree listings, patch-IDs.
2. **Normalisation rule set** — exact regex/transform rules used in refinement check.
3. **Tool version** — git version, skill script versions, OS.
4. **Reproducibility** — exact commands to re-run the equivalence check.

#### 4.3.5 Level 3: sequence-aware pair walker (branch vs. branch)

For a whole-PR audit (head branch vs. base branch), walk every positional
commit pair instead of one pair at a time:

```bash
pwsh -File .agents/skills/git-commit-comparison-audit/scripts/pair-walker.ps1 \
    -LocalBranch <base_branch> -RemoteBranch <head_branch>
```

The walker enumerates both branches oldest-first, runs the equivalence check
per pair, advances on non-DIVERGENT verdicts, probes **split commits** (one
legacy commit split into two atomic ones — verified via tree equality of the
adjacent commit), and **stops at the first true DIVERGENT**. The result is a
short list of commit pairs carrying real content — your actual review surface.

Six verdicts possible: CONTENT-EQUIVALENT, PATCH-EQUIVALENT, REFINED
EQUIVALENT, SPLIT EQUIVALENT, SPLIT REFINED EQUIVALENT, DIVERGENT.

#### 4.3.6 Mandatory report shape: "Why vs. What"

Every comparison report MUST end with a two-part narrative:

1. **The What** — the technical delta (pre-populated by `compare.py`).
2. **The Why** — the historical rationale (you supply it from session
   context: e.g., "SHA1 was preserved in the 2026-04-04 backup branches during
   the industrialization rebase").

### 4.5 Stage 4 — behavioral verification (per `manual-testing-rules.md`)

Static diff analysis is NOT sufficient for visual, stateful, or cross-session
features (UI persistence, multi-tab interactions). If the PR touches such
features, execute a **manual verification plan** before writing the verdict:

* **Plan first, then approve**: present the full manual test plan to the user
  (exact UI labels, login-first flow, environment pre-check) and wait for the
  approval token **"Proceed"** before executing.
* **Deep verification**: do not trust UI side-effects alone — verify
  `localStorage`/`sessionStorage` contains the expected keys; JS execution in
  the browser console is authorized for state injection/clearing.
* **Self-contained plan**: a non-technical person must be able to run it —
  relative paths only, copy-paste code blocks, no hardcoded UUIDs (use
  dynamic lookup like `Object.keys(...).find(...)`).
* **Dual-purpose documentation**: record Expected vs Actual with ✅/❌ markers;
  broken behavior links to a co-located `KNOWN_BUGS.md`.
* **Co-location**: save the approved plan permanently (e.g.,
  `src/Features/Profile/__tests__/profile-manual-verification.md`), never in
  ephemeral artifacts.

### 4.6 Stage 5 — deliver the review (per `github-pr-management-rules.md`)

Post the verdict as a **structured comment** on the PR (per the org's
AI-assisted review standard: concise summary + flagged risks + concerns):

```bash
gh pr review <n> --repo owner/name --comment --body-file /tmp/review.md
# or: --approve / --request-changes
```

The review comment MUST contain:

1. **Summary** — one-paragraph "What" (the change does X) + "Why" context.
2. **Findings** — each with severity (blocking / non-blocking), file:line, and
   the expected behavior; Conventional-Commit violations and CI failures go
   here.
3. **Manual-test results** — if Stage 4 ran, the ✅/❌ matrix.
4. **Verdict** — Approve / Request changes / Comment.

After posting, follow the **explicit handoff**: notify the user and STOP. Do
not proceed to any other PR until the user confirms ("done", "next",
"approved").

### 4.7 Review Failure Handling (post-verdict lifecycle)

When the verdict is **Request changes** or **Comment with blocking findings**,
the PR enters a remediation cycle:

| Event | Trigger | Reviewer action | Author action |
| :--- | :--- | :--- | :--- |
| **Request changes posted** | `gh pr review --request-changes` | Wait for author push | Address each finding; push new commits to same branch |
| **New commits pushed** | Any push to PR head branch | Re-evaluate **only changed files** (diff since last review) | — |
| **Re-review** | Author signals ready (or auto on push) | Run Stage 1.5 (CI) → Stage 2/3 (diff) → Stage 4 if needed → new verdict | — |
| **All blocking findings resolved** | Re-review passes | `gh pr review --approve` | — |
| **Blocking findings remain** | Re-review finds same issues | `gh pr review --request-changes` (reference prior comment) | — |
| **Reviewer rejects outright** | Fundamental design flaw / out of scope | `gh pr review --comment` with "Reject" + rationale; notify user for escalation | Escalate to tech lead / product owner |

**Re-review protocol (mandatory):**

1. Run `gh pr checks` (Stage 1.5) — CI must pass fresh.
2. Compute diff since last review: `gh pr view <n> --json commits
   --jq '.commits[-1].oid'` then `git diff <last-review-sha>..<new-sha>`.
3. Only re-verify **changed files** — unchanged files keep prior ✅.
4. Update manual test results (Stage 4) only for affected scenarios.
5. Post new structured review comment with updated verdict.

**Escalation** (per `github-pr-management-rules.md` §3): if reviewer and
author disagree on a blocking finding after two rounds, **notify the user**
(project architect) for a decision. Do not auto-approve to unblock.

---

## 5. End-to-End Annotated Walkthrough

**Scenario:** associate `jane-dev` opened PR #42 (`fix login timeout`) on
`acme/awesome-app`, base `main`. You review it.

### Step 1 — Pre-flight and orient

```bash
gh auth status                        # Phase -1: auth valid?
gh pr list --repo acme/awesome-app    # Phase 0: discover active PRs, pick ONE
gh pr view 42 --repo acme/awesome-app --json \
    number,title,state,baseRefName,headRefName,headRefOid,mergeable,changedFiles
```

Output:

```json
{
  "number": 42,
  "title": "Fix login timeout on slow networks",
  "state": "OPEN",
  "baseRefName": "main",
  "headRefName": "fix-login-timeout",
  "headRefOid": "9f3c2a1deadbeef...",
  "mergeable": "MERGEABLE",
  "changedFiles": 3
}
```

**Read:** open PR, small scope (3 files), mergeable. Proceed.

### Step 2 — Pull the commit series and file surface

```bash
python3 .agents/skills/github-repo-commit-fetch/scripts/list-commits.py \
    --repo acme/awesome-app --sha 9f3c2a1deadbeef --limit 5
```

Output: two commits (`fix: retry login...`, `test: add login timeout...`) —
nice, atomic structure. File surface:

```bash
python3 .agents/skills/github-repo-commit-fetch/scripts/commit-details.py \
    --repo acme/awesome-app --sha 9f3c2a1deadbeef --files-only
```

Output: `src/auth/login.ts`, `src/auth/timeout.ts`,
`tests/login-timeout.test.ts`. **Scope check passed** — all three files
belong to the login feature.

### Step 3 — Pull one suspicious file at the reviewed SHA

```bash
python3 .agents/skills/github-repo-commit-fetch/scripts/fetch-file-at-ref.py \
    --repo acme/awesome-app --ref 9f3c2a1deadbeef \
    --path src/auth/timeout.ts --out scratch/pr42-timeout.ts
```

### Step 4 — Verify CI status and commit-message compliance

```bash
gh pr checks 42 --repo acme/awesome-app   # baseline automation: lint/type/unit/security
git log origin/main..HEAD --oneline       # review commit subjects for Conventional Commits
```

### Step 5 — Bring objects local and run the equivalence audit

```bash
gh pr checkout 42
BASE_REF=$(git symbolic-ref --short refs/remotes/origin/HEAD | sed 's#origin/##')
python3 .agents/skills/git-commit-comparison-audit/scripts/compare.py \
    "origin/$BASE_REF" HEAD
```

### Step 6 — Walk the pair sequence

```bash
pwsh -File .agents/skills/git-commit-comparison-audit/scripts/pair-walker.ps1 \
    -LocalBranch "$BASE_REF" -RemoteBranch fix-login-timeout
```

If the walker reports DIVERGENT on the first commit pair, that is your review
focus: read `git diff` for those two commits only, file by file.

### Step 7 — Behavioral verification (if UI/stateful)

If the PR touches visual or persistence features, run the manual-testing
protocol (§4.4): present the plan, wait for "Proceed", execute, document
✅/❌ actual results.

### Step 8 — Write the "Why vs. What" verdict and post it

* **The What:** PR #42 adds retry-with-backoff to the login flow, plus tests.
* **The Why:** previous sessions identified flaky network timeouts as the top
  login failure; this change directly addresses that defect.

```bash
cat > /tmp/pr42-review.md <<'EOF'
## Review: PR #42
**Summary:** retry-with-backoff for login; 2 commits, 3 files, tests included.
**Findings:** none blocking; timeout constant could be configurable (non-blocking).
**CI:** all checks passed. **Commits:** Conventional-Commits compliant.
**Verdict:** Approve
EOF
gh pr review 42 --repo acme/awesome-app --comment --body-file /tmp/pr42-review.md
```

Then notify the user and STOP — do not start the next PR until they confirm.

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| `gh: not found` | `gh` not installed | `brew install gh`, or fall back to `github-rest-api-fallback` (§4.0.1) |
| `gh auth status` → 401/403 | Credentials stale/wrong identity | `git-github-auth-fallback` §2 classification before retry |
| Stage 3 scripts say "commit not found" | Objects not fetched locally | `gh pr checkout 42` first (with user confirmation) |
| `pwsh` missing | PowerShell not installed | `brew install --cask powershell`; or use `pwsh-preview` |
| `gh api` rate limit | Too many rapid calls | Wait; reduce `--limit` values |
| Fork PR shows empty commit list | Head ref not resolvable via API default | Use `--sha <headRefOid>` explicitly (from Stage 1) |
| compare.py output looks noisy | SHAs differ but identity matches | Run equivalence-check.ps1 (§4.3.3) for the verdict |
| DIVERGENT everywhere | Genuine divergence, or mixed rename+edit | Review the flagged pairs manually |
| Weird line endings in fetched file | `.gitattributes` filters | Inspect bytes; compare against local checkout |
| `gh pr checks` shows failing checks | PR does not pass baseline automation | Do not approve; report the failing check in review |

---

## 7. SSOT Note and Future Skill Build

This document is the **SSOT** for the PR review workflow. A future skill (to
be built under `.agents/skills/pr-review-workflow/`) MUST consume this
document as its authoritative source rather than re-deriving the workflow,
per the
[script-over-instruction-decomposition skill](../.agents/skills/script-over-instruction-decomposition/SKILL.md).

Authoritative skill documents referenced by this guide:

| Skill | Path | Role |
| :--- | :--- | :--- |
| GitHub Repo Commit Fetch | `.agents/skills/github-repo-commit-fetch/SKILL.md` | Stage 2 primitives |
| Git Commit Comparison Audit | `.agents/skills/git-commit-comparison-audit/SKILL.md` | Stage 3 orchestration |
| GitHub Actions Run Audit | `.agents/skills/github-actions-run-audit/SKILL.md` | Compose pattern reference |
| GitHub Repo Commit Fetch scripts | `.agents/skills/github-repo-commit-fetch/scripts/` | `list-commits.py`, `commit-details.py`, `fetch-file-at-ref.py` |
| Git Commit Comparison Audit scripts | `.agents/skills/git-commit-comparison-audit/scripts/` | `compare.py`, `equivalence-check.ps1`, `pair-walker.ps1` |

Governing rules (SSOT for the mandates below — this guide does not duplicate
their full text):

| Rule | Governs |
| :--- | :--- |
| `ai-agent-rules/github-pr-management-rules.md` | One-PR-at-a-time, gh-only SSOT, explicit handoff (§4.0.4, §4.6) |
| `ai-agent-rules/github-cli-permission-rules.md` | Approval gate on every gh command, fallback ladder, PAT protection (§4.0.5) |
| `ai-agent-rules/git-operation-rules.md` | Phase -1/0 validation, fetch gates, default-branch discovery (§4.0, §4.4.1) |
| `ai-agent-rules/ci-cd-rules.md` | Baseline automation checks, Conventional Commits (§4.2) |
| `ai-agent-rules/manual-testing-rules.md` | Behavioral verification plans, ✅/❌ documentation (§4.5) |

---

## 8. Quick Reference Card (copy-paste)

```bash
# Stage 0 — pre-flight (permission gate on EVERY command)
gh auth status
gh pr list --repo owner/name

# Stage 1 — orient
gh pr view 42 --repo owner/name --json number,title,state,baseRefName,headRefName,headRefOid,mergeable,additions,deletions,changedFiles

# Stage 1.5 — CI status + Conventional Commits
gh pr checks 42 --repo owner/name

# Stage 2 — no-clone commit/file pull
SCRIPTS_DIR=.agents/skills/github-repo-commit-fetch/scripts
python3 "$SCRIPTS_DIR"/list-commits.py --repo owner/name --sha <headRefOid> --limit 20
python3 "$SCRIPTS_DIR"/commit-details.py --repo owner/name --sha <sha> --files-only
python3 "$SCRIPTS_DIR"/fetch-file-at-ref.py --repo owner/name --ref <headRefOid> --path <path> --out scratch/out.ts

# Stage 3 — local equivalence audit (fetch requires user confirmation)
gh pr checkout 42
BASE_REF=$(git symbolic-ref --short refs/remotes/origin/HEAD | sed 's#origin/##')
python3 .agents/skills/git-commit-comparison-audit/scripts/compare.py "origin/$BASE_REF" HEAD
pwsh -File .agents/skills/git-commit-comparison-audit/scripts/pair-walker.ps1 -LocalBranch "$BASE_REF" -RemoteBranch fix-login-timeout

# Stage 5 — deliver (after "Why vs. What" verdict; handoff: STOP after posting)
gh pr review 42 --repo owner/name --comment --body-file /tmp/pr42-review.md
```
