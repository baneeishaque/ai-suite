# Document the Skill-Folder Relocation Workflow as Reusable Layered Skills (v1)

## Rule Compliance Reference

- [`ai-agent-planning-rules.md`](../ai-agent-rules/ai-agent-planning-rules.md) — §1 plan versioning,
  §6 iterative planning, §7 Maximum Literal Detail, §7.1 CAM/Verbatim-Superset, §9 History Mandate,
  §10 artifact location + `task.md`, §13 Sequential Objective Protocol.
- [`ai-rule-standardization-rules.md`](../ai-agent-rules/ai-rule-standardization-rules.md) — §2 Skill-First
  Architecture, Layered Composition Mandate, Skill-Name Precision Mandate; §4 Script Delivery /
  No-Embedded-Script / Redaction / Artifact Linting mandates.
- [`scripting-language-selection-rules.md`](../ai-agent-rules/scripting-language-selection-rules.md) — four-tier
  language framework (all new scripts: Tier 1 Python 3.12+).
- [`markdown-generation/SKILL.md`](../.agents/skills/markdown-generation/SKILL.md) — markdown authoring + lint
  standards (markdownlint-cli2 direct-binary validation; no `npx`).
- [`skill-factory/SKILL.md`](../.agents/skills/skill-factory/SKILL.md) — §2.0 layering decision, §2.1–§2.4
  creation/registration, §2.2.1.1 script mandates, §3 Post-Drafting Checklist, §5.1 post-rename sweep,
  §5.5–§5.8 skill-doc editing discipline.
- [`skill-library-domain-grouping/SKILL.md`](../.agents/skills/general/skill-library-domain-grouping/SKILL.md) — §2
  placement rules, §3 change protocol, §4 Changelog discipline.
- [`planning-artifact-naming/SKILL.md`](../.agents/skills/general/planning/planning-artifact-naming/SKILL.md) — artifact
  naming formula + versioning rules.
- [`redaction-portability/SKILL.md`](../.agents/skills/redaction-portability/SKILL.md) — portability/PII audit for
  every produced artifact.
- [`git-atomic-commit-construction/SKILL.md`](../.agents/skills/git-atomic-commit-construction/SKILL.md) — atomic
  commit arrangement + message delivery.
- [`script-over-instruction-decomposition/SKILL.md`](../.agents/skills/script-over-instruction-decomposition/SKILL.md)
  — Tier-A extraction mandate + Consumer Discipline (invoke shipped scripts, never re-derive).

## User Questions & Answers

### Q1 — "Is this workflow correctly documented?"

A1: The workflow-analysis report
(`scratch/f1dd554edffeIjEwbPkY123xx1/workflow-analysis_2026-09-27_15-20-31.md`)
documents WHAT happened in the session, but the workflow itself is NOT captured as a reusable,
invocable capability in the skill library. Four gaps exist (§2). Verdict: **NO — not sufficiently
documented**; this plan closes the gaps.

### Q2 — "New skills or enrichments?"

A2: Both, decided by the skill-factory §2.0 layering test:

- NEW base `markdown-relative-link-rebase-on-path-move` — the depth-aware link-rebase primitive is
  generic (any markdown folder move needs it); inlining it would violate the SSOT contract.
- NEW base `git-linked-worktree-root-resolve` — the main-worktree-root resolution primitive is
  consumed by ≥3 existing scripts across 3 domains; layering is mandatory.
- NEW composer `skill-library-folder-relocation` — the domain orchestration (taxonomy + registry +
  audits + atomic commit) has no owner.
- ENRICH 4 existing skills (§3.4) — bug fixes + missing prerequisite documentation.

### Q3 — Commit/push scope

A3: Six atomic commits (§5). Push is OUT OF SCOPE (deferred by the user in the prior session).

## 1. Goal & Context

The session `ses_f1dd554edffeIjEwbPkY123xx1` ("Move planning-artifact-naming into planning
subdirectory") relocated the skill folder
`.agents/skills/general/planning-artifact-naming/` → `.agents/skills/general/planning/planning-artifact-naming/`
via `git mv`, manually rebased 5 relative links across `SKILL.md` + `AGENTS.md` for the new depth,
verified with markdownlint + the dangling-link audit, and committed as `3463c36b`
(`refactor(skills): move planning-artifact-naming to general/planning`). The move completed the
`general/planning/` grouping already documented in the taxonomy SSOT (as-designed vs as-built).

During that session, four workflow gaps surfaced (script worktree failures + manual link rebasing +
ad-hoc orchestration). This plan converts that one-off workflow into reusable layered skills and
fixes the tooling defects — so the NEXT relocation is a scripted, verifiable procedure.

Worktree: `/Users/dk/lab-data/ai-suite-worktrees/migrate-rule-file-into-skill` (branch `t1`,
HEAD `3463c36b`). All paths below are relative to this worktree.

## 2. Gap Analysis

### 2.1 G1 — No owner for "folder move + relative-link rebase"

- [`skill-factory` §5.1](../.agents/skills/skill-factory/SKILL.md) covers **literal token renames**
  (`post-rename-sweep.py`, literal string replacement). A path move changes link **depth** —
  e.g. `../../../ai-agent-rules/` → `../../../../ai-agent-rules/` — which literal replacement
  cannot compute.
- [`markdown-section-to-companion-doc`](../.agents/skills/markdown/markdown-section-to-companion-doc/SKILL.md)
  moves sections between **same-directory** files (no depth change; no rebase logic).
- [`git-commit-dangling-link-audit`](../.agents/skills/git-commit-dangling-link-audit/SKILL.md)
  **detects** dangling links but does not **fix** them.
- No `rebase-relative-links` script exists anywhere in `.agents/skills/` (audited: only
  `detect-dangling-links.py`, `detect-cross-repo-links.py`, and VS Code-specific
  `refactor_links.py` exist — all detection or other-domain).

### 2.2 G2 — No worktree-root resolution primitive; 3 scripts fail in linked worktrees

A linked worktree has a `.git` **file** (gitdir pointer), and repo-shared state (`.opencode/logs/`,
`node_modules/`) lives in the **main** worktree. Three shipped scripts break:

1. `git/basic/edit/git-commit-preview-verify/scripts/verify-commit-preview.py` —
   lines 46 and 167 use `os.path.isdir(<path>/.git)`, false for worktrees AND submodule checkouts
   (both have `.git` as a file) → exit 3 "not a git repository".
   (Contrast: `agents-md-stage-row.py` line 78 correctly uses `os.path.exists`.)
2. `opencode/opencode-current-session-id/scripts/find-current-session.py` —
   `find_repo_root()` returns the worktree root (via `git rev-parse --show-toplevel`), where
   `.opencode/logs/` does not exist → "ERROR: .opencode/logs not found"; the session was forced to
   pass `--repo-root` manually.
3. `general/file/scratch-artifact-naming/scripts/resolve-scratch-path.py` —
   `discover_session_id()` shells out to `find-current-session.py` with no repo-root hint; in a
   worktree the discovery fails → "ERROR: could not discover session id; pass `--session-id`".

### 2.3 G3 — markdownlint custom-rule prerequisite undocumented

`.markdownlint-cli2.jsonc` declares `"customRules": ["markdownlint-rule-relative-links"]`.
`markdownlint-cli2` resolves custom rules from `node_modules/`; a fresh worktree/clone lacks it and
linting fails until `mise x node -- npm install --no-save --no-package-lock` is run once. No skill
documents this prerequisite (the session rediscovered it by trial).

### 2.4 G4 — The relocation workflow has no composer

The end-to-end procedure (git mv → rebase links → taxonomy SSOT update → `AGENTS-legacy.md` row
update → markdownlint + dangling/cross-ref audits → atomic refactor commit) exists only as
scattered rules (skill-factory §2.4/§3/§5.1, taxonomy §3.3). No skill orchestrates it; the session
improvised it.

### 2.5 Flagged pre-existing drift (OUT OF SCOPE — do not fix in this plan)

- `planning-version-coverage-audit` and `versioned-artifact-superset-build` (SKILL.md + AGENTS.md)
  link `../planning-artifact-lifecycle/SKILL.md` and `../planning-superseded-version-retirement/SKILL.md`
  — both folders are absent on branch `t1` (they exist only in the taxonomy SSOT's as-designed tree).
  Pre-existing; not introduced by the move commit (verified: the move touched only the 2 moved files).
- Dirty submodule pointer (`M ai-agent-rules` in `git status --porcelain`; pre-existing;
  excluded from all commits).

## 3. Deliverables

### 3.1 NEW-BASE-1 — `markdown-relative-link-rebase-on-path-move`

Placement: `.agents/skills/markdown/markdown-relative-link-rebase-on-path-move/`
(taxonomy: `markdown/` flat group, 4 → 5 items; ≤10 OK).

Files:

- `SKILL.md` — frontmatter (name / description / category `Text-Manipulation`), Scope & Intent,
  Environment & Dependencies, CLI contract, link-rebase semantics, exit codes, edge cases,
  Prohibited Actions, Script Reference, `## Composition by Higher-Level Skills` (lists the new
  composer §3.3), Related Skills, pointer-only `## Changelog` / `## Traceability`.
- `AGENTS.md` — companion bridge (5 required sections per skill-factory §2.3.2, no frontmatter).
- `CHANGELOG.md` — creation entry.
- `TRACEABILITY.md` — source session `ses_f1dd554edffeIjEwbPkY123xx1`, evidence (manual rebase of 5
  links in commit `3463c36b`), extraction rationale.
- `scripts/rebase-relative-links.py` — Tier 1 Python 3.12+, stdlib only.

CLI contract:

```bash
python3 scripts/rebase-relative-links.py --root <repo-root>
    --move <old-rel-path>:<new-rel-path> [--move ...]   # file or dir, repeatable
    [--file <rel-path>]...                              # explicit files; default: auto-collect
    [--scan <rel-dir>]...                               # extra inbound-scan dirs
    (--check | --apply) [--json]
```

Semantics (per markdown link / image target):

1. Skip: external schemes (`https:`, `mailto:`, …), protocol-relative `//`, pure anchors `#…`,
   absolute `/…`.
2. Resolve the link's INTENDED target against the file's OLD location (reverse-mapped via `--move`
   when the file itself moved).
3. Remap the target through the `--move` map (prefix match, file or directory).
4. Re-relativize from the file's NEW location; preserve link text, fragments (`#…`), query, and
   angle-bracket form; no-op when the link is unchanged.
5. `--check`: exit 0 clean / exit 1 changes-pending (greppable per-line `OLD -> NEW` output);
   `--apply` rewrites files; idempotent (immediate re-run exits 0).

### 3.2 NEW-BASE-2 — `git-linked-worktree-root-resolve`

Placement: `.agents/skills/git/repo/git-linked-worktree-root-resolve/`
(taxonomy: `git/repo/`, 4 → 5 items).

Files: `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`,
`scripts/resolve-worktree-roots.py` (Tier 1 Python 3.12+, stdlib only).

CLI contract:

```bash
python3 scripts/resolve-worktree-roots.py [--start <path>] [--field <name>] [--json]
```

- `worktree_root` = `git rev-parse --show-toplevel`; `common_dir` =
  `git rev-parse --path-format=absolute --git-common-dir`; `main_root` = `common_dir` parent when
  its basename is `.git`, else falls back to `worktree_root`; `is_linked_worktree` =
  `main_root != worktree_root`.
- Output: JSON `{start, worktree_root, main_root, git_dir, common_dir, is_linked_worktree}`;
  `--field <name>` prints one bare value for shell substitution.
- Exit codes: 0 success / 1 not a git repo / 2 usage.
- Documented scope limit: main-root semantics are defined for linked worktrees; submodule
  common-dirs (`<parent>/.git/modules/…`) fall back to `worktree_root` (flag stays false).

### 3.3 NEW-COMPOSER — `skill-library-folder-relocation`

Placement: `.agents/skills/general/skill-dev/skill-library-folder-relocation/`
(taxonomy: `general/skill-dev/`, 6 → 7 items).

Files: `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`,
`scripts/relocate-skill-folder.py` (Tier 1 Python 3.12+, stdlib only).

Composition Rationale (in `SKILL.md`): composes

- `markdown-relative-link-rebase-on-path-move` (base §3.1) — both self-rebase of moved files and
  inbound rebase across `.agents/skills/**`;
- `git-linked-worktree-root-resolve` (base §3.2) — worktree-safe repo-root detection;
- `skill-factory/scripts/post-rename-sweep.py` — literal old-path-token sweep (root-relative
  mentions, e.g. the `AGENTS-legacy.md` row link `.agents/skills/...`);
- verification consumers: `detect-dangling-links.py`, `audit-cross-refs.py`, markdownlint-cli2.

Composer script contract:

```bash
python3 scripts/relocate-skill-folder.py --skill <name> --from <rel-dir> --to <rel-dir> [--apply] [--json]
```

- Preflight: both paths under `.agents/skills/`; `--from` exists; `--to` absent; skill name ==
  folder basename; those paths clean in `git status --porcelain`.
- Dry-run (default): prints the `git mv` command, moved-file list, inbound scan roots, and the
  sweep preview command; exits 0.
- `--apply`: runs `git mv`; invokes base §3.1 (`--move <from>:<to>`, moved files + inbound scan);
  runs `post-rename-sweep.py` dry-run for the old path token; prints remaining judgement steps.
- Exit codes: 0 success / 1 preflight failure / 2 usage.

Composer prose steps (gates preserved):

1. Preflight dry-run → user confirmation.
2. `--apply` (git mv + link rebase + sweep preview).
3. Taxonomy SSOT update (`skill-library-domain-grouping` §1.1/§1.2 + §4 Changelog) — judgement.
4. `AGENTS-legacy.md` row path update (sweep `--apply`, scoped; verify alphabetical order).
5. Verification: markdownlint-cli2 (direct binary), `detect-dangling-links.py`,
   `audit-cross-refs.py`, `verify-doc-invocations.py`.
6. Atomic refactor commit (delegates to `git-atomic-commit-construction`; message convention
   `refactor(skills): move <skill> to <dest>`) → user confirmation.

### 3.4 Enrichments

**ENRICH-1 — `git-commit-preview-verify` (worktree/submodule repo detection fix).**

- `scripts/verify-commit-preview.py`: `find_repo_root()` line 46 `os.path.isdir` →
  `os.path.exists`; line 167 replace the `.git`-directory check with an authoritative
  `git -C <repo> rev-parse --git-dir` probe (covers `.git`-file worktrees and submodules).
- `SKILL.md`: add Edge-Cases bullet "Linked worktree / submodule checkouts (`.git` is a file)".
- Inline `## Traceability` retained as-is (pre-convention skill; metadata separation is a separate
  library-wide sweep — out of scope §7).

**ENRICH-2 — `opencode-current-session-id` (worktree fallback in repo-root resolution).**

- `scripts/find-current-session.py` `find_repo_root()`: after the `git rev-parse --show-toplevel`
  candidate, if `<candidate>/.opencode/logs` is not a directory, resolve the main worktree root via
  base §3.2 (`SCRIPT_DIR`-relative path per skill-factory §2.1) and return it when it has
  `.opencode/logs`; else keep the candidate. Env overrides unchanged.
- `SKILL.md`: update Script Reference step 1 + add Edge-Cases bullet (linked worktree → main-repo
  logs).

**ENRICH-3 — `scratch-artifact-naming` (worktree-aware session discovery).**

- `scripts/resolve-scratch-path.py` `discover_session_id(repo)`: resolve the main worktree root of
  `--repo` via base §3.2; when it differs, pass `--repo-root <main-root>` to
  `find-current-session.py`; else call as today. Scratch stays under the GIVEN `--repo` (worktree
  local) — unchanged.
- `SKILL.md`: update Script Reference step 3 + Edge-Cases bullet.

**ENRICH-4 — `markdown-lint-workflow` (custom-rule prerequisite).**

- `SKILL.md`: add a short subsection "Custom-rule prerequisite (fresh worktree / clean clone)":
  `.markdownlint-cli2.jsonc` declares `markdownlint-rule-relative-links`, resolved from
  `node_modules/`; install once per worktree with
  `mise x node -- npm install --no-save --no-package-lock` (repo root); `npx` remains forbidden
  (link to [`markdown-generation`](../.agents/skills/markdown-generation/SKILL.md) as SSOT).

### 3.5 Cross-reference sweep ("refer the new skill wherever applicable")

- [`skill-factory` §5.1](../.agents/skills/skill-factory/SKILL.md): append a pointer paragraph —
  folder MOVES need depth-aware rebase (not literal sweep) → new base §3.1 + composer §3.3.
- [`skill-factory` §2.4](../.agents/skills/skill-factory/SKILL.md): one sentence — relocating an
  existing skill = composer §3.3.
- [`skill-library-domain-grouping` §3.3](../.agents/skills/general/skill-library-domain-grouping/SKILL.md):
  point the "cross-reference sweep" bullet at composer §3.3 as the executor.
- [`git-commit-dangling-link-audit`](../.agents/skills/git-commit-dangling-link-audit/SKILL.md):
  Related Skills — base §3.1 is the FIX counterpart of its DETECT role.
- [`markdown-generation`](../.agents/skills/markdown-generation/SKILL.md): Related Skills — base §3.1.
- Taxonomy §1.1/§1.2 + §4 Changelog entries for all three new skills (per-skill, in-commit).
- `AGENTS-legacy.md`: register all three new skills at alphabetically correct positions via
  `agents-md-stage-row.py --mode worktree` (composer row notes "Composer — feeds … into the base
  … skill").

### 3.6 Script Tier Declaration (skill-factory §2.2.1.1 mandate #4)

| Script | Tier-1 (Python) evaluation | Chosen tier | Citation | Deviation reason |
| :--- | :--- | :--- | :--- | :--- |
| `rebase-relative-links.py` | Text/path manipulation + file mutation + JSON output — canonical Tier 1 | Tier 1 — Python 3.12+ | `scripting-language-selection-rules` §3 Tier-1 default | none |
| `resolve-worktree-roots.py` | Cross-platform git probing + JSON emission; not Windows shell glue | Tier 1 — Python 3.12+ | `scripting-language-selection-rules` §3 | none |
| `relocate-skill-folder.py` | Orchestration (git mv + subprocess base calls + reporting) | Tier 1 — Python 3.12+ | `scripting-language-selection-rules` §3 | none |

## 4. Execution Phases

- **Phase 0 — planning artifacts (this step).** Create this plan + `task.md`; lint both with
  markdownlint-cli2; present for approval. No skill mutation before approval.
- **Phase 1 — C1 (base §3.1).** Create the 5 files; smoke-test the script (fixture under
  `scratch/<session>/link-rebase-fixture/`: build a mini tree, `--check` exit 1 → `--apply` →
  re-`--check` exit 0); regression-check on the real move mapping (expect exit 0, links already
  correct); update taxonomy + `AGENTS-legacy.md`; run §6 checks; commit C1.
- **Phase 2 — C2 (base §3.2).** Create the 5 files; run the script in the worktree (expect
  `is_linked_worktree: true`, `main_root: /Users/dk/lab-data/ai-suite`) and in the main repo
  (expect `false`); update taxonomy + `AGENTS-legacy.md`; run §6 checks; commit C2.
- **Phase 3 — C3 (composer §3.3).** Create the 5 files; dry-run the composer against a scratch
  fixture skill tree; update taxonomy + `AGENTS-legacy.md`; apply §3.5 cross-references; run §6
  checks; commit C3.
- **Phase 4 — C4/C5/C6 (enrichments §3.4).** ENRICH-1 → C4; ENRICH-2 + ENRICH-3 (one logical unit:
  worktree-aware session discovery) → C5; ENRICH-4 → C6. Each with its smoke test (§6) and doc
  update in the same commit.
- **Phase 5 — close-out.** Full §6 matrix; `task.md` statuses `[x]` + timestamps; propose
  disposition of the planning artifacts (commit vs trash) per planning-rules §10 (explicit user
  confirmation required).

## 5. Commit Strategy

All commits in the worktree (`git -C <worktree>`), Conventional Commits, no push:

| # | Message | Scope |
| :--- | :--- | :--- |
| C1 | `feat(skills): add markdown-relative-link-rebase-on-path-move base skill` | §3.1 files + taxonomy + AGENTS-legacy row |
| C2 | `feat(skills): add git-linked-worktree-root-resolve base skill` | §3.2 files + taxonomy + AGENTS-legacy row |
| C3 | `feat(skills): add skill-library-folder-relocation composer` | §3.3 files + taxonomy + AGENTS-legacy row + §3.5 cross-refs |
| C4 | `fix(skills): detect git repos via .git file in commit-preview verify` | ENRICH-1 |
| C5 | `fix(skills): resolve session logs from main worktree in linked worktrees` | ENRICH-2 + ENRICH-3 |
| C6 | `docs(skills): document markdownlint custom-rule node_modules prerequisite` | ENRICH-4 |

Multi-line bodies via the `git-commit-message-delivery` convention; scripts ship in the same commit
as their `SKILL.md` (skill-factory §2.2.2 #4). The `ai-agent-rules` submodule pointer stays
excluded.

## 6. Verification Matrix

| Check | Command (from worktree root) | Expectation |
| :--- | :--- | :--- |
| Markdown lint | `markdownlint-cli2 --fix <paths>` then `markdownlint-cli2 <paths>` (direct binary, no npx) | 0 issues |
| Cross-reference audit | `python3 .agents/skills/general/skill-cross-reference-audit/scripts/audit-cross-refs.py` | 0 issues |
| Dangling links | `python3 .agents/skills/git-commit-dangling-link-audit/scripts/detect-dangling-links.py <changed md>` | all EXISTS (pre-existing §2.5 DANGLES excepted) |
| Invocation audit | `python3 .agents/skills/skill-factory/scripts/verify-doc-invocations.py` | exit 0 |
| Old-path sweep | `python3 .agents/skills/skill-factory/scripts/post-rename-sweep.py --old ".agents/skills/general/planning-artifact-naming" --new ".agents/skills/general/planning/planning-artifact-naming"` | 0 hits in live files |
| Rebase script smoke | fixture: `--check` (exit 1) → `--apply` → `--check` (exit 0); real-map `--check` (exit 0) | as stated |
| Worktree-roots smoke | run in worktree + main repo | `is_linked_worktree` true/false; `main_root` correct |
| Commit-preview smoke | `verify-commit-preview.py --preview <fixture> --repo .` in the worktree | exit 0 (was exit 3) |
| Session discovery smoke | `find-current-session.py` (no args, cwd=worktree) | exit 0, session found from main logs |
| Scratch-path smoke | `resolve-scratch-path.py --repo . --purpose smoke-test --no-mkdir` (no `--session-id`) | stem printed, exit 0 |
| Redaction scan | Redaction §8 regex inventory over all new/edited files | empty / Tier-C only |

## 7. Out of Scope

- `git push` (deferred by user).
- Pre-existing drift §2.5 (absent sibling skills; submodule pointer).
- Library-wide metadata-separation sweep of pre-convention skills.
- Any relocation of further skill folders.
- Committing the planning artifacts (Phase 5 user gate).

## 8. Guardrails

- All deterministic mechanics run through shipped scripts (Consumer Discipline) — no inline
  re-derivation.
- markdownlint-cli2 invoked as the direct binary; `npx` forbidden.
- `trash` over `rm`; no `.DS_Store` touches; no `/tmp` writes — scratch under
  `scratch/f1dd554edffeIjEwbPkY123xx1/`; command output captured per `repo-scratch-output-capture`.
- All git operations via `git -C <worktree>`; one command per bash call; no chained probes.
- Stop and report if any verification in §6 fails — no silent workarounds.
