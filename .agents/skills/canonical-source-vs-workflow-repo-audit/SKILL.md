---
name: canonical-source-vs-workflow-repo-audit
description: Classify the enclosing Git repository from an existing file or directory before source edits; reject missing or non-repository inputs.
category: Git-Operations
---

# Canonical-Source vs Workflow-Repo Pre-Edit Audit Skill

> **Skill ID:** `canonical-source-vs-workflow-repo-audit`<br>
> **Version:** 1.0.0<br>
> **Type:** Atomic + script

## Description

Before editing source code under any Git working tree, classify the
enclosing repository as **canonical-source**, **workflow-backup**, or
**mirror**. The audit blocks the "edited the wrong repo" mistake
common in ecosystems where a workflow / backup / CI repo coexists with
the canonical source repo and shares a similar name pattern.

### Typical trigger: related source and workflow repositories

- `<service>-ops` — the **workflow / backup** repo. Hosts
  `.github/workflows/database-backup.yml` and a small `http_API/` snapshot
  of the live production server. Edits here NEVER reach the canonical PHP.
- `<service>-api` — the **canonical source** PHP repo. Every
  HTTP-API edit MUST land here first; the workflow repo only consumes
  what production already serves.

In May 2026 an API edit landed in the workflow repo,
was caught by review, soft-reset, and re-applied in the canonical repo.
This skill exists to **stop that mistake at pre-edit time**.

## Composition Rationale

This standalone read-only classifier owns enclosing-repository discovery
and weighted role signals. Existing file inputs are normalized to their
containing directory before Git resolves the root; callers consume the
same verdict, signals, and notes as directory inputs. Other skills retain
the judgement about whether a particular edit belongs in that repository.

## Input and Output Contract

- Python 3.12+ and Git are required; the script uses the standard library.
- The optional positional input is an existing file or directory and defaults to `.`.
  Relative paths are resolved from the caller's working directory; `~` is expanded.
- Git resolves the closest enclosing repository, including a nested repository.
  For a file symlink, discovery starts at the link's containing directory.
- Missing paths, broken symlinks, unsupported path types, and paths outside Git return exit 2 with stderr diagnostics.
  The script does not create the requested path.
- Exit 0 reports `root`, `verdict`, `signals`, and `notes`; `--json` emits that object.
  Repositories with no role signals report `unknown` rather than failing.
- Path normalization does not change the scoring weights or edit-approval policy.

## When to Apply

- Before the first `cat > <file>` / `edit` call in any repository the
  session has not previously edited.
- Whenever two repository names share a common prefix or suffix that
  hints at related-but-distinct roles.
- Whenever a file's path matches paths already known to exist in another
  cloned-locally repo.

Do NOT apply when:

- Editing files under the audit-tool's own repo (the audit ROOT is itself).
- Editing config / dotfiles that are explicitly the repo's purpose
  (e.g. editing `.github/workflows/*` IN the workflow repo).

## Procedure

### Step 1 — Run the audit

```bash
python3 .agents/skills/canonical-source-vs-workflow-repo-audit/scripts/audit-repo-role.py /path/to/file/or/dir
```

Output:

```text
REPO_ROOT: <repo-root>
VERDICT:   workflow
SIGNALS:   {'workflow': 5, 'canonical': 4, 'mirror': 0}
  - 1/1 workflow files match backup/mirror/sync pattern
  - 17/20 recent commits look like backup/snapshot/mirror
  - manifest(s) at root: composer.json
  - source dirs ['http_API'] contain 24 files

WARNING: editing source code in a workflow repo is almost always wrong.
         Locate the canonical source repo before proceeding.
```

### Step 2 — Decide

| Verdict | Action |
| --- | --- |
| `canonical` | Proceed with the edit. |
| `workflow` | **STOP.** Find the canonical source repo (often a sibling dir; ask user). |
| `mirror` | **STOP.** Never edit a read-only mirror. |
| `unknown` | Ask the user; the audit's heuristics are inconclusive. |

### Step 3 — Soft-Reset Recovery (when wrong repo already edited)

If the mistake was discovered AFTER an edit + commit in the wrong repo:

```bash
# Repo: wrong (workflow) repo
git -C /path/to/wrong/repo log --oneline -3   # confirm the mistaken commit is HEAD
git -C /path/to/wrong/repo reset --soft HEAD~1
git -C /path/to/wrong/repo restore --staged http_API/<file>.php  # unstage
git -C /path/to/wrong/repo checkout -- http_API/<file>.php       # discard

# Verify clean
git -C /path/to/wrong/repo status

# Re-apply the same change in the canonical repo
# ...then commit per git-atomic-commit-construction
```

CRITICAL: never `git reset --hard` — soft + restore + checkout
preserves any unrelated WIP. See
[`git-operation-rules.md`](../../../ai-agent-rules/git-operation-rules.md).

## Heuristic Signals (consulted by the script)

| Signal | Weight | What it indicates |
| --- | --- | --- |
| `.github/workflows/*.yml` filenames match `backup\|snapshot\|mirror\|sync\|dispatch` for ≥50% of files | +3 workflow | Repo's primary job is CI orchestration / backup. |
| ≥10 of last 20 commit titles match same keywords | +2 workflow | Recent commit history dominated by automated backups. |
| Source manifest at root (`composer.json` / `package.json` / `pom.xml` / `mise.toml` / etc.) | +2 canonical | Repo declares itself as a buildable project. |
| ≥10 files inside `src/` / `lib/` / `http_API/` / `app/` / `kotlin/` / `java/` / `pkg/` / `cmd/` / `internal/` | +2 canonical | Real source tree present. |
| README declares "mirror of X" | +3 mirror | Explicit mirror declaration. |

A verdict requires the top-scoring category to have ≥2 signal weight;
otherwise the verdict is `unknown`.

### Tie-breaker note

A repo can score positive in BOTH `workflow` AND `canonical` (e.g. the
workflow-repository example: it has 1 backup workflow AND a small
`http_API/` source dir for production sync purposes). The script picks
the highest score; equal maxima currently use the score-table order
(`workflow`, `canonical`, `mirror`). Do not mistake that tie-break for
conclusive evidence. **Always present
the verdict + signals to the user — the human breaks ambiguous ties.**

## Composition with Other Skills

This audit is referenced as a **Step 0 / pre-edit** check by:

- [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md) Step 0d — before authoring any new
commit in a previously-unedited repo.
- [`php-mysqli-prepared-statement-modernization`](../php-mysqli-prepared-statement-modernization/SKILL.md) §Pitfalls —
explicitly requires the audit before any PHP modernization edit.

## Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Two repos with `canonical` verdict for same artifact (forks) | Audit is single-repo; cross-repo provenance still requires human verification. |
| Repo recently rebranded from workflow to canonical (commit history misleads) | Manually inspect README + ask user. |
| Monorepo with both workflow and source subtrees | Audit returns one verdict per ROOT; not designed for monorepo subtree classification. |

## Related Skills

- [`git-personal-sandbox-remote`](../git-personal-sandbox-remote/SKILL.md) — distinct concern: routing personal-only
commits.

## Scripts

| Script | Tier | Purpose |
| --- | --- | --- |
| [`scripts/audit-repo-role.py`](scripts/audit-repo-role.py) | Deterministic | Classify enclosing repo via weighted-signal scoring. |
| [`scripts/test-audit-repo-role.py`](scripts/test-audit-repo-role.py) | Tier 1 Python | Regression checks for file/directory parity and invalid-input behavior. |

## Verification

Set `TEST_ARTIFACT_DIR` to an existing session-scratch directory, then run:

```bash
python3 scripts/test-audit-repo-role.py
```

Fixtures stay in that directory. The suite covers absolute and relative files,
directory defaults, spaces, nested repositories, missing/broken paths, non-Git inputs,
zero-signal repositories, and worktree preservation. The separate
[manifest template](scripts/repo-role-manifest.json.template) supplies the fixture contents.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Traceability

See [TRACEABILITY.md](TRACEABILITY.md).
