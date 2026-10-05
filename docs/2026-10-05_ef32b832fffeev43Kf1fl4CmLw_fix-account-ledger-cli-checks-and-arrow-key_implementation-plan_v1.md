# [Document the Account-Ledger CLI Fix Workflow as Reusable Layered Skills] (v1)

## Rule Compliance Reference

- [`ai-agent-planning-rules.md`](../ai-agent-rules/ai-agent-planning-rules.md) — §1 plan versioning + H1
  format, §6 iterative planning, §7 Maximum Literal Detail, §10 artifact location + `task.md`.
- [`ai-rule-standardization-rules.md`](../ai-agent-rules/ai-rule-standardization-rules.md) — §2 Skill-First
  Architecture, Layered Composition Mandate, cross-repository BLOCKING test; §4 Script Delivery /
  Redaction / Artifact Linting mandates.
- [`scripting-language-selection-rules.md`](../ai-agent-rules/scripting-language-selection-rules.md) —
  four-tier language framework (all new scripts: Tier 1 Python 3.12+).
- [`git-submodule-rules.md`](../ai-agent-rules/git-submodule-rules.md) — §1 Never Commit to Detached HEAD,
  §2 branch checkout, §3 recovery (rule SSOT behind §3.3).
- [`git-commit-message-rules.md`](../ai-agent-rules/git-commit-message-rules.md) — §5 submodule sync
  messages.
- [`markdown-generation/SKILL.md`](../.agents/skills/markdown-generation/SKILL.md) — markdown authoring +
  lint standards (markdownlint-cli2 direct binary; no `npx`).
- [`skill-factory/SKILL.md`](../.agents/skills/skill-factory/SKILL.md) — §2.0 layering decision, §2.1–§2.4
  creation/registration, §2.2.2 script delivery, §3 Post-Drafting Checklist, §5.2.2 composer discipline.
- [`skill-library-domain-grouping/SKILL.md`](../.agents/skills/general/skill-library-domain-grouping/SKILL.md)
  — §1 taxonomy placement, §3 change protocol, §4 Changelog discipline.
- [`planning-artifact-naming/SKILL.md`](../.agents/skills/general/planning/planning-artifact-naming/SKILL.md)
  — artifact naming formula + versioning rules.
- [`redaction-portability/SKILL.md`](../.agents/skills/redaction-portability/SKILL.md) — portability/PII
  audit for every produced artifact.
- [`git-atomic-commit-construction/SKILL.md`](../.agents/skills/git-atomic-commit-construction/SKILL.md) —
  atomic commit arrangement + message delivery.
- [`script-over-instruction-decomposition/SKILL.md`](../.agents/skills/script-over-instruction-decomposition/SKILL.md)
  — script-tier extraction mandate + Consumer Discipline.

## User Questions & Answers

### Q1 — "Is this workflow correctly documented?"

A1: PARTIALLY. The workflow-analysis report
(`scratch/ef32b832fffeev43Kf1fl4CmLw/workflow-analysis_2026-10-05_17-54-26.md`) documents WHAT happened,
and several sub-workflows are already owned by existing skills (§2.5), but three gaps exist (§2.1–§2.3):
submodule detached-HEAD resolution, JLine console-history integration, and interactive-CLI smoke testing.
This plan closes them.

### Q2 — "New skills or enrichments?"

A2: New skills only (no enrichment needed — §2.5 lists the already-covered sub-workflows), decided by the
skill-factory §2.0 layering test:

- NEW base `cli-smoke-test-piped-eof-pty` — generic interactive-CLI harness; runtime-agnostic (§3.1).
- NEW composer `jvm-cli-jline-console-history-integration` — composes the base for verification (§3.2).
- NEW skill `git-submodule-detached-head-branch-resolution` — rule-backed routine operation with no
  existing owner (§3.3).
- OPTIONAL composer `session-skill-coverage-audit` — the assessment procedure itself (§3.4).

### Q3 — Commit/push scope

A3: Three atomic commits (§5), one per skill, in dependency order (base first); a fourth only if the
optional §3.4 skill is approved. Push is OUT OF SCOPE.

## 1. Goal & Context

The session `ses_ef32b832fffeev43Kf1fl4CmLw` ("Fix account-ledger CLI: checks and arrow key") fixed three
defects in a Kotlin/JVM CLI application and its shared-library submodules:

1. A "sheet account not configured" error printed multiple times per invocation → deduplicated.
2. Account checks validated only one of the from/to/via accounts → aggregation across all accounts.
3. Up-arrow did not recall command history → JLine console line-reader integration.

Delivery: ten atomic commits across the parent repo and two submodules (C1 `ce8fdab`, L1 `c3ea22d`,
L2 `a9edbb4`, Lsync `9a904d5`, L3 `36dbd60`, P1 `2764495`, P2 `c306991`, P3 `8ba9356`, R1 `1bc0b54`,
R2 `0854fb4`), safety stashes, submodule sync messages, and interactive smoke tests (piped / EOF / pty).
P1–P3 plus both submodule commits were pushed by the user; R1/R2 remain local.

The question: is THIS workflow documented as reusable skills? Audit result: partially (§2). This plan
converts the three undocumented sub-workflows into layered skills.

Worktree: `/workspaces/ai-suite` (HEAD `22eec2a6`). All paths below are relative to it.

## 2. Gap Analysis

### 2.1 G1 — Submodule detached-HEAD resolution: rules exist, no skill

- Rule SSOT: [`git-submodule-rules.md`](../ai-agent-rules/git-submodule-rules.md) §1 (Never Commit to a
  Detached HEAD), §2 (checkout the default branch), §3 (recovery from detached HEAD) mandate the behaviour
  but name no executable procedure.
- No skill owns it. Nearest neighbours operate in different directions:
    - `git-submodule-missing-revision-recovery` — materializes the detached state at the recorded SHA
    (opposite direction).
    - `git-submodule-pointer-repair` — parent-history gitlink repair.
    - `git-atomic-commit-construction` — handles a detached main repo, not submodules.
    - `git-submodule-addition` — taxonomy-listed under `git/submodule/setup/` but absent in this checkout;
    in any case covers addition, not pre-commit branch resolution.
- Session evidence: both submodules sat detached at their pinned SHAs (lib `26554d6`, common-lib
  `fe171ed`) while their `master` branches were ahead (`4f5b63c` / `a041e6e`); the session fetched,
  checked out `master` carrying local edits, and fast-forwarded when behind — then all subsequent commits
  landed on branches and the parent gitlinks were synced.

### 2.2 G2 — JLine console-history integration is undocumented

- No skill in the library mentions JLine (`[Jj]line` → zero matches) or console line-reader integration.
- Session evidence (report + commit P3 `8ba9356`): JLine 3.30.17 integrated into a Kotlin/JVM CLI:
    - self-contained bundle `org.jline:jline:3.30.17` (reader + terminal + providers + native libs) —
    `jline-terminal-jni` NOT needed; JLine 4.x exists but 3.x API stability was chosen;
    - pluggable indirection in the shared JVM library (`ConsoleInputUtils.setLineReader { prompt -> ... }`,
    commit C1 `ce8fdab`) — the shared library carries NO JLine dependency, preventing propagation to
    Android consumers;
    - CLI-side initialization (`TerminalBuilder.builder().system(true).build()` + `LineReaderBuilder`),
    `EndOfFileException` → `EOFException`, `UserInterruptException` → exit 130, dumb-terminal fallback;
    - ~72 console-read sites migrated away from `Scanner(System.in)` (which conflicts with JLine raw mode);
    - GraalVM native-image caveat (the project ships a native-image workflow; JLine may need
    reflection/resource configuration).

### 2.3 G3 — Interactive-CLI smoke testing (piped / EOF / pty) is undocumented

- No skill covers smoke-testing an interactive CLI (`smoke` matches no skill; no pty / `script` usage).
- Session evidence: three modes were exercised and captured under `build/agent/`:
  1. piped: `printf '0\n' | <jar command>` → `smoke-piped.log`;
  2. EOF: empty stdin → `smoke-eof.log`;
  3. pty: `printf '0\n' | script -qec "stty cols 80 rows 24; <jar command>" /dev/null` → `smoke-pty.log`
     (JLine bracketed-paste escape codes prove the line reader is active; a 0x0 pty size caused rendering
     artifacts, hence the explicit `stty` sizing).

### 2.4 G4 (OPTIONAL) — the coverage-assessment procedure itself has no owner

- The procedure that produced §2 (workflow report → tool-call inventory → skill-library matching →
  coverage matrix) is reusable but unowned. A meta composer could automate the deterministic half.
- OPTIONAL: included for user decision at approval; not part of the assessed workflow.

### 2.5 Already documented (no action)

- Atomic commit arrangement / safety stash / hunk staging — `git-atomic-commit-construction`,
  `git-pre-execution-safety-stash`, `git-hunk-staging-primitives`.
- Submodule sync-message metadata — `git-submodule-commit-details` (v2.1.0; composes
  `git-commit-metadata-extraction`; consumed by `git-submodule-commit-reword` and
  `git-atomic-commit-construction`).
- Workflow analysis — `opencode-session-problem-solution-workflow-analysis`.

### 2.6 Flagged pre-existing drift (OUT OF SCOPE — do not fix in this plan)

- Taxonomy §1.1/§1.2 is as-designed for several groups whose folders are absent in this checkout
  (`cli/`, `java/`, `general/skill-dev/`, `git/submodule/setup/` items); pre-grouping skills live at
  `.agents/skills/` top level. New skills follow their taxonomy slots (precedent: `email/`, `calendar/`,
  `docker/` groups were created for new skills; pre-grouping skills are never moved).
- Dirty submodule pointers plus modified `.opencode/package*.json` in the ai-suite working tree; excluded
  from all commits.

## 3. Deliverables

### 3.1 NEW-BASE-1 — `cli-smoke-test-piped-eof-pty`

Placement: `.agents/skills/cli/cli-smoke-test-piped-eof-pty/` (taxonomy: `cli/` flat group, 7 → 8 items).

Files:

- `SKILL.md` — frontmatter, Scope & Intent, Environment & Dependencies, CLI contract, mode semantics,
  exit codes, Prohibited Actions, Script Reference, `## Composition by Higher-Level Skills` (lists §3.2),
  Related Skills, pointer-only `## Changelog` / `## Traceability`.
- `AGENTS.md` — companion bridge (5 required sections per skill-factory §2.3.2, no frontmatter).
- `CHANGELOG.md` — creation entry.
- `TRACEABILITY.md` — source session `ses_ef32b832fffeev43Kf1fl4CmLw`, evidence (three smoke logs),
  extraction rationale.
- `scripts/run-cli-smoke-test.py` — Tier 1 Python 3.12+, stdlib only.

CLI contract:

```bash
python3 scripts/run-cli-smoke-test.py --command "<shell command>" [--input "<stdin text>"]
    [--out-dir <dir>] [--mode piped|eof|pty|all] [--rows 24] [--cols 80]
    [--timeout <sec>] [--json]
```

Semantics:

1. `piped` — `printf '<input>' | <command>`; log `<out-dir>/smoke-piped.log`.
2. `eof` — empty stdin; log `smoke-eof.log`.
3. `pty` — `script -qec "stty cols <cols> rows <rows>; <command>" /dev/null`; log `smoke-pty.log`;
   document the util-linux vs BSD/macOS `script` invocation difference.
4. `--timeout` mandatory (default 60s) — kills hung interactive commands; per-mode exit code + log path
   reported; `--json` summary; harness exit 0 when all requested modes complete, 1 when any mode times out.

### 3.2 NEW-COMPOSER-1 — `jvm-cli-jline-console-history-integration`

Placement: `.agents/skills/java/jvm-cli-jline-console-history-integration/` (taxonomy: `java/` flat group,
3 → 4 items).

Files: `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`,
`scripts/find-console-read-sites.py` (Tier 1 Python 3.12+, stdlib only).

Composition Rationale (in `SKILL.md`): composes

- `cli-smoke-test-piped-eof-pty` (base §3.1) — piped / EOF / pty verification of the integrated CLI;
- `find-console-read-sites.py` — deterministic inventory of `readLine` / `Scanner(System.in)` / `readln`
  sites to migrate;
- consumer cross-reference:
  [`android-feature-to-shared-kotlin-lib`](../.agents/skills/android-feature-to-shared-kotlin-lib/SKILL.md)
  (shared-JVM-library discipline).

Script contract:

```bash
python3 scripts/find-console-read-sites.py --root <dir> [--json]
```

Prose steps (gates preserved): dependency selection (self-contained bundle, version catalog entry,
CLI module only) → shared-library pluggable reader with NO JLine dependency → CLI-side initialization +
exception mapping (`EndOfFileException` → `EOFException`, `UserInterruptException` → exit 130) →
site migration → smoke test (delegates to base §3.1) → GraalVM native-image caveat note.

### 3.3 NEW-1 — `git-submodule-detached-head-branch-resolution`

Placement: `.agents/skills/git/submodule/setup/git-submodule-detached-head-branch-resolution/`
(taxonomy: `git/submodule/setup/`, 4 → 5 items).

Files: `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`,
`scripts/resolve-submodule-branches.py` (Tier 1 Python 3.12+, stdlib only).

CLI contract:

```bash
python3 scripts/resolve-submodule-branches.py [--root <parent-repo>] [--submodule <name>]...
    [--default-branch master] (--check | --apply) [--json]
```

Semantics:

1. Enumerate submodules via `git submodule status`; classify each: detached at recorded SHA / on branch /
   uninitialized.
2. `--check` — report submodules needing resolution; exit 1 when any found (greppable).
3. `--apply` — per submodule: `git fetch origin`; `git checkout <default-branch>` (carries local edits);
   `git pull --ff-only` when behind; never discards work; never commits; idempotent re-run exits 0.
4. Refuses to run when the submodule has uncommitted changes that would conflict with checkout; reports
   the conflict for judgement.

Rule linkage: implements `git-submodule-rules.md` §1–§3.

### 3.4 OPTIONAL-1 — `session-skill-coverage-audit` (user decides)

Placement: `.agents/skills/general/skill-dev/session-skill-coverage-audit/` (taxonomy:
`general/skill-dev/`, 6 → 7 items).

Files: `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`, `scripts/audit-skill-coverage.py`
(Tier 1 Python 3.12+, stdlib only). Composes `opencode-session-yaml-tool-call-extractor` (tool-call
inventory) and `opencode-session-problem-solution-workflow-analysis` (report), plus a skill-inventory
scanner (frontmatter name + description); emits a coverage-matrix draft (covered / partial / gap) for
agent judgement.

### 3.5 Cross-reference sweep ("refer the new skill wherever applicable")

- [`git-atomic-commit-construction`](../.agents/skills/git-atomic-commit-construction/SKILL.md) —
  submodule detached-HEAD handling section: pointer to §3.3.
- [`git-submodule-commit-details`](../.agents/skills/git-submodule-commit-details/SKILL.md) — Related
  Skills: §3.3 as the prerequisite branch-resolution step before sync-message extraction.
- [`android-feature-to-shared-kotlin-lib`](../.agents/skills/android-feature-to-shared-kotlin-lib/SKILL.md)
  — Related Skills: §3.2 for console-reader integration in the shared-library + CLI split.
- Taxonomy §1.1/§1.2 + §4 Changelog entries for every new skill (per-skill, in-commit).
- `AGENTS-legacy.md`: register every new skill at alphabetically correct positions; composer rows note
  "Composer — composes ...".
- The `ai-agent-rules` submodule is NOT edited (rules remain the SSOT; out of scope §7).

### 3.6 Script Tier Declaration (skill-factory §2.2.1.1 mandate #4)

| Script | Tier-1 (Python) evaluation | Chosen tier | Citation | Deviation reason |
| :--- | :--- | :--- | :--- | :--- |
| `run-cli-smoke-test.py` | Process spawning + stdio/pty orchestration + log capture + JSON output | Tier 1 — Python 3.12+ | `scripting-language-selection-rules` §3 | none |
| `find-console-read-sites.py` | Text scan + JSON emission; cross-platform | Tier 1 — Python 3.12+ | `scripting-language-selection-rules` §3 | none |
| `resolve-submodule-branches.py` | Git probing/mutation orchestration + JSON reporting | Tier 1 — Python 3.12+ | `scripting-language-selection-rules` §3 | none |
| `audit-skill-coverage.py` (optional) | YAML/JSONL parsing + set matching + report emission | Tier 1 — Python 3.12+ | `scripting-language-selection-rules` §3 | none |

## 4. Execution Phases

- **Phase 0 — planning artifacts (this step).** Create this plan + `task.md`; lint both with
  markdownlint-cli2 (direct binary); present for approval. No skill mutation before approval.
- **Phase 1 — C1 (base §3.1).** Create the 5 files; smoke-test the script against a scratch fixture
  interactive command (piped / EOF / pty modes produce logs; timeout path exercised); taxonomy `cli/`
  7 → 8 + Changelog; `AGENTS-legacy.md` row; §6 checks; commit C1.
- **Phase 2 — C2 (composer §3.2).** Create the 5 files; run `find-console-read-sites.py` on a scratch
  fixture tree (expected counts); taxonomy `java/` 3 → 4; `AGENTS-legacy.md` row; §3.5 cross-refs
  (android skill); §6 checks; commit C2.
- **Phase 3 — C3 (§3.3).** Create the 5 files; run `resolve-submodule-branches.py --check` on a scratch
  fixture with a detached submodule; taxonomy `git/submodule/setup/` 4 → 5; `AGENTS-legacy.md` row;
  §3.5 cross-refs (git-atomic-commit-construction, git-submodule-commit-details); §6 checks; commit C3.
- **Phase 4 — C4 (optional §3.4, only if approved).** Create the 5 files; fixture run; taxonomy
  `general/skill-dev/` 6 → 7; `AGENTS-legacy.md` row; §6 checks; commit C4.
- **Phase 5 — close-out.** Full §6 matrix; `task.md` statuses `[x]` + timestamps; propose disposition
  of the planning artifacts (commit vs trash) per planning-rules §10 — explicit user confirmation.

## 5. Commit Strategy

All commits in `/workspaces/ai-suite`, Conventional Commits, no push:

| # | Message | Scope |
| :--- | :--- | :--- |
| C1 | `feat(skills): add cli-smoke-test-piped-eof-pty base skill` | §3.1 files + taxonomy + AGENTS-legacy row |
| C2 | `feat(skills): add jvm-cli-jline-console-history-integration composer` | §3.2 files + taxonomy + AGENTS-legacy row + §3.5 cross-refs |
| C3 | `feat(skills): add git-submodule-detached-head-branch-resolution skill` | §3.3 files + taxonomy + AGENTS-legacy row + §3.5 cross-refs |
| C4 | `feat(skills): add session-skill-coverage-audit composer` | §3.4 files + taxonomy + AGENTS-legacy row (optional) |

Multi-line bodies via the `git-commit-message-delivery` convention; scripts ship in the same commit as
their `SKILL.md` (skill-factory §2.2.2). Only planned paths are staged — pre-existing dirty submodule
pointers and `.opencode/package*.json` stay excluded.

## 6. Verification Matrix

| Check | Command (from repo root) | Expectation |
| :--- | :--- | :--- |
| Markdown lint | `mise x node -- markdownlint-cli2 --fix <paths>` then `mise x node -- markdownlint-cli2 <paths>` (direct binary, no npx) | 0 issues |
| Cross-reference audit | `python3 .agents/skills/general/skill-cross-reference-audit/scripts/audit-cross-refs.py` | 0 issues |
| Dangling links | `python3 .agents/skills/git-commit-dangling-link-audit/scripts/detect-dangling-links.py <changed md>` | all EXISTS |
| Invocation audit | `python3 .agents/skills/skill-factory/scripts/verify-doc-invocations.py` | exit 0 |
| Smoke-test fixture | base §3.1 script on a scratch fixture: piped / eof / pty + timeout | logs + expected exits |
| Read-site scanner fixture | §3.2 script on a scratch fixture tree | expected counts |
| Submodule resolver fixture | §3.3 script `--check` (detached found) → `--apply` → re-`--check` (exit 0) | idempotent |
| Redaction scan | Redaction §8 regex inventory over all new/edited files | empty / Tier-C only |
| Standalone-clone test | no session IDs, local paths, or external repo names in committed skill files | pass |

## 7. Out of Scope

- `git push`.
- Editing the `ai-agent-rules` submodule (rule SSOT stays as-is).
- Pre-existing drift §2.6 (taxonomy as-designed vs as-built; dirty working-tree entries).
- Library-wide metadata-separation sweep of pre-convention skills.
- Moving pre-grouping skills into taxonomy groups.
- Committing the planning artifacts (Phase 5 user gate).

## 8. Guardrails

- All deterministic mechanics run through shipped scripts (Consumer Discipline) — no inline re-derivation.
- markdownlint-cli2 invoked as the direct binary; `npx` forbidden.
- `trash` over `rm`; no `.DS_Store` touches; no `/tmp` writes — scratch under
  `scratch/ef32b832fffeev43Kf1fl4CmLw/`; command output captured per `repo-scratch-output-capture`.
- One command per bash call; no chained probes.
- Committed skill files carry no session IDs, local paths, or external repository names.
- Stop and report if any verification in §6 fails — no silent workarounds.
