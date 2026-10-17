---
name: git-remote-branch-lifecycle
description: Orchestrates the mutating remote-branch lifecycle — convention-aware first
  push to a chosen remote, live post-push verification, refspec rename to the remote's own
  naming scheme, remote deletion with live proof, and deferred upstream-tracking offers —
  behind explicit authorization and worktree-branch guardrails.
category: Git
---

# Git Remote Branch Lifecycle (v1)

> **Skill ID:** `git-remote-branch-lifecycle`<br>
> **Version:** 1.0.0<br>
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)<br>
> **Layer:** Composer (per [skill-factory §2.0 Layering Decision](../../../skill-factory/SKILL.md))

## Description

Owns the ordered, mutating side of taking a local branch to a remote and maintaining it
there: **first push → live verification → rename to convention → remote deletion → prune →
upstream-tracking offer**. Every remote-mutating step passes an authorization gate, and
every remote-mutating step is proven with a live probe rather than a cached ref.

The deterministic read-only probes live in two separate bases —
[`git-remote-ref-reachability-primitives`](../../basic/audit/git-remote-ref-reachability-primitives/SKILL.md)
(reachability) and
[`git-remote-branch-convention-discovery`](../../config/git-remote-branch-convention-discovery/SKILL.md)
(naming-convention inference) — split under decision D1=C. This skill owns only the
sequencing, the naming judgement, and the gates.

## Composition Rationale

This skill is a **composer**: it owns no Git query mechanics of its own. It sequences the
base primitives and already-mandated guardrails into one auditable run:

1. [`git-remote-branch-convention-discovery`](../../config/git-remote-branch-convention-discovery/SKILL.md)
   §2 — discover the target remote's naming/grouping convention BEFORE naming anything.
   Split from the reachability base under decision D1=C: separate question, separate
   reusability, separate consumers.
2. [`git-worktree-state-fingerprint`](../../basic/audit/git-worktree-state-fingerprint/SKILL.md)
   — the pre-push cleanliness gate primitive.
3. [`git-remote-ref-reachability-primitives`](../../basic/audit/git-remote-ref-reachability-primitives/SKILL.md)
   §2.1 — pre-push availability verdict and the tracking tri-signal.
4. [`git-remote-ref-reachability-primitives`](../../basic/audit/git-remote-ref-reachability-primitives/SKILL.md)
   §2.3 — live post-push and post-delete proof.
5. [`git-remote-ref-reachability-primitives`](../../basic/audit/git-remote-ref-reachability-primitives/SKILL.md)
   §2.2 — the pre-rename backup boundary (how far back the remote already holds content).
6. [`is-this-command-safe`](../../../is-this-command-safe/SKILL.md) — destructive-flag
   classification for `push --delete`.
7. [`git-remote-origin-repoint`](../git-remote-origin-repoint/SKILL.md) — the redirect-
   notice remediation when a push reveals a moved repository.

Inlining any of these into this skill is FORBIDDEN — the base's caveat text and the
fingerprint mechanics are reused by other composers and must not fork.

## 1. Environment & Dependencies

| Requirement | Minimum | Verification |
| :--- | :--- | :--- |
| Python | 3.9+ (for the base primitives) | `python3 --version` |
| git | any modern version | `git --version` |
| git credentials | valid for the target remote | `git ls-remote --exit-code <remote>` |
| `markdownlint-cli2` | any | only when this skill's docs are edited |

## 2. Operational Logic

### Phase 0 — Target selection and readiness

**Step 1** — Confirm the target remote name from `git remote -v`. Never infer it from the
last push.

**Step 2** — Run the pre-push cleanliness gate (§3.1). A dirty tree on an ADDITIVE push
does not corrupt the remote, but it silently under-delivers: report dirtiness and let the
user decide, rather than pushing and claiming success.

**Step 3** — Probe the remote is reachable before any mutating step.

### Phase 1 — Convention-aware first push

**Step 1** — Run the convention discovery (§3.2,
[`git-remote-branch-convention-discovery`](../../config/git-remote-branch-convention-discovery/SKILL.md))
to learn the remote's actual grouping scheme. Do NOT hardcode a scheme from memory; the
remote's live heads are the authority.

**Step 2** — Choose the `<purpose>` segment by describing the branch's CONTENT, not the
session or ticket that created it. A worktree branch named `t19` must not become `t19` on
the remote.

**Step 3** — Push the local branch under the convention-resolved name:

```bash
git push <remote> <local-branch>:<remote-name>
```

**Step 4** — Prove it landed with a live probe (§3.4). Do not rely on `branch -r` here; it
only updates after a fetch.

### Phase 2 — Upstream tracking is deferred, not automatic

A plain push leaves the branch with NO upstream. This is a legitimate end state, not a
defect. After a successful push, REPORT the no-upstream fact and OFFER the tracking
command; do not run it unprompted.

```bash
git -C <repo> fetch <remote>
git -C <repo> branch --set-upstream-to=<remote>/<remote-name> <local-branch>
```

Three distinct rationales exist for omitting `-u`, and a caller must know which applies:

| Rationale | Owner |
| :--- | :--- |
| Avoid writing a credential-bearing URL into `.git/config` | [`git-github-auth-fallback`](../../../git-github-auth-fallback/SKILL.md) §3.2.1 |
| Leave tracking as a user decision after a bare first push | This skill §2 |
| Convention route requires fetch before `--set-upstream-to` | [`git-personal-sandbox-remote`](../../../git-personal-sandbox-remote/SKILL.md) §4b |

### Phase 3 — Rename a remote branch to match the remote's scheme

Trigger: the user reports the remote branch name is wrong, or a convention probe shows the
existing name is an outlier.

**Step 1** — Probe the current remote name live (§3.4) and the target name live (§3.4).
Refuse to proceed if the target already exists.

**Step 2** — Establish the backup boundary (§3.5): the newest ancestor already resident in
a remote. If the boundary is `NO_REMOTE_RESIDENT_ANCESTOR`, the branch's entire history is
local-only, so pushing the rename is the FIRST backup. Say so explicitly.

**Step 3** — Push the SAME content to the new name using the refspec form:

```bash
git push <remote> <local-branch>:<new-remote-name>
```

**Step 4** — Delete the old remote name:

```bash
git push <remote> --delete <old-remote-name>
```

**Step 5** — Prove the deletion landed with a live probe (§3.4, `--expect absent`).

**Step 6** — Run `git fetch <remote> --prune`, then re-verify the surviving remote refs.

**Guardrail — remote rename does not authorize a local rename.** The two names serve
different purposes and are changed for different reasons. Renaming a local branch is a
separate decision requiring its own authorization.

**Guardrail — worktree branches are not renamed locally.** A branch checked out in a
`git worktree` is a long-lived workspace anchor (it is reused across unrelated pieces of
work). Renaming it breaks the worktree association and every muscle memory built on the
name. Leave it alone unless the user explicitly asks.

**Guardrail — explicit user refusal is binding.** If the user said not to rename the local
branch, do not rename it, do not offer it again later in the session, and do not treat a
later push request as retracting that instruction.

### Phase 4 — Delete a remote branch

`git push <remote> --delete <branch>` is a remote mutation with no undo. Require:

**Gate 1** — An explicit authorization naming the remote and the branch.

**Gate 2** — A live existence probe first (§3.4).

**Gate 3** — A live absence proof after (§3.4, `--expect absent`).

**Gate 4** — Never delete a remote's default branch. Determine it with
`git remote show <remote>` or the symbolic ref `refs/remotes/<remote>/HEAD` before
proposing deletion.

### Phase 5 — Redirect-notice handling

If a push or probe returns `repository moved` (GitHub 301 after an owner transfer, or a
case-only rename such as `Baneeishaque` → `baneeishaque`), the push may still succeed via
redirect. Surface the notice, then delegate remediation to
[`git-remote-origin-repoint`](../git-remote-origin-repoint/SKILL.md). Do not silently
ignore the notice — the next push may fail once the redirect is retired.

## 3. Scripts (via the base primitives)

| Step | Command |
| :--- | :--- |
| §3.1 cleanliness gate | `python3 <worktree-fingerprint>/scripts/…` per that skill's CLI |
| §3.2 convention discovery | `python3 <convention>/scripts/discover-remote-branch-convention.py --repo <repo> --remote <remote>` |
| §3.3 availability + tracking | `python3 <reachability>/scripts/commit-remote-availability.py --repo <repo> --sha <sha> --branch <branch>` |
| §3.4 live ref proof | `python3 <reachability>/scripts/verify-remote-ref-live.py --repo <repo> --remote <remote> --branch <branch> --expect present\|absent` |
| §3.5 backup boundary | `python3 <reachability>/scripts/newest-remote-resident-ancestor.py --repo <repo> --branch <branch>` |

`<reachability>` = `.agents/skills/git/basic/audit/git-remote-ref-reachability-primitives`
(§2.3 supplies the live ref proof; the script name is unchanged by the D1=C split).
`<convention>` = `.agents/skills/git/config/git-remote-branch-convention-discovery`.

## 4. Guardrails

- The agent MUST NOT execute any `git push` (plain, `--delete`, or `--force*`) without
  explicit user authorization in the current conversation.
- Every remote mutation is proven with a LIVE probe, never a cached remote-tracking ref.
- Never push `--all` or `--mirror`; push one named branch per operation.
- Never delete a remote's default branch.
- Never rename a local worktree branch without an explicit, branch-specific request.
- A cached-ref verdict is never reported as an absolute negative.

## 5. Composition by Higher-Level Skills

| Composer | Composition Mechanism |
| :--- | :--- |
| `(none yet)` | — |

## Related Skills

- [`git-remote-ref-reachability-primitives`](../../basic/audit/git-remote-ref-reachability-primitives/SKILL.md)
  — the read-only base this skill sequences.
- [`git-personal-sandbox-remote`](../../../git-personal-sandbox-remote/SKILL.md) — owns
  the `personal/` grouping convention and the personal-remote push route.
- [`git-branch-promotion`](../../../git-branch-promotion/SKILL.md) — the force-push
  promotion route, for when the remote tip must be replaced rather than added.
- [`git-parallel-branch-decommission`](../../../git-parallel-branch-decommission/SKILL.md) —
  remote deletion after content has been fanned out; this skill owns deletion when it does not.
- [`git-remote-origin-repoint`](../git-remote-origin-repoint/SKILL.md) — remediation for a
  redirect notice surfaced by a push in §2 Phase 5.
- [`is-this-command-safe`](../../../is-this-command-safe/SKILL.md) — destructive-flag
  classification.

## 6. Traceability

See [TRACEABILITY.md](TRACEABILITY.md).

## 7. Changelog

See [CHANGELOG.md](CHANGELOG.md).
