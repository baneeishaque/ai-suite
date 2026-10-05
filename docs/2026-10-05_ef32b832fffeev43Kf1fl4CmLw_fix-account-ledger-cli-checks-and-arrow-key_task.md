# Task — Document the Account-Ledger CLI Fix Workflow as Reusable Layered Skills

Session: `ses_ef32b832fffeev43Kf1fl4CmLw` · Worktree: `/workspaces/ai-suite`

## Phase 0 — Planning Artifacts

- [x] Pre-plan context gathering (workflow report, skills inventory, gap greps, taxonomy, registry) `[2026-10-05 18:57]`
- [x] Write implementation-plan v1 `[2026-10-05 18:57]`
- [x] Lint plan + task (markdownlint-cli2) `[2026-10-05 18:57]`
- [x] Present plan for user approval `[2026-10-05 18:57]`

## Phase 1 — C1: NEW base `cli-smoke-test-piped-eof-pty`

- [ ] Create `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`
- [ ] Create `scripts/run-cli-smoke-test.py` (Tier 1)
- [ ] Smoke-test: scratch fixture interactive command, piped / eof / pty + timeout path
- [ ] Taxonomy `cli/` 7 → 8 + Changelog
- [ ] Register row in `AGENTS-legacy.md` (alphabetical)
- [ ] §6 checks + commit C1

## Phase 2 — C2: NEW composer `jvm-cli-jline-console-history-integration`

- [ ] Create `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`
- [ ] Create `scripts/find-console-read-sites.py` (Tier 1)
- [ ] Fixture run: scratch tree, expected counts
- [ ] Taxonomy `java/` 3 → 4 + Changelog
- [ ] Register row in `AGENTS-legacy.md` (alphabetical, composer annotation)
- [ ] Cross-references (§3.5): android-feature-to-shared-kotlin-lib
- [ ] §6 checks + commit C2

## Phase 3 — C3: NEW skill `git-submodule-detached-head-branch-resolution`

- [ ] Create `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`
- [ ] Create `scripts/resolve-submodule-branches.py` (Tier 1)
- [ ] Fixture run: detached submodule `--check` → `--apply` → re-`--check` (exit 0)
- [ ] Taxonomy `git/submodule/setup/` 4 → 5 + Changelog
- [ ] Register row in `AGENTS-legacy.md` (alphabetical)
- [ ] Cross-references (§3.5): git-atomic-commit-construction, git-submodule-commit-details
- [ ] §6 checks + commit C3

## Phase 4 — C4 (OPTIONAL): NEW composer `session-skill-coverage-audit`

- [ ] User decision: include or defer
- [ ] Create `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`
- [ ] Create `scripts/audit-skill-coverage.py` (Tier 1)
- [ ] Fixture run
- [ ] Taxonomy `general/skill-dev/` 6 → 7 + Changelog
- [ ] Register row in `AGENTS-legacy.md` (alphabetical, composer annotation)
- [ ] §6 checks + commit C4

## Phase 5 — Close-out

- [ ] Full §6 verification matrix
- [ ] `task.md` statuses + timestamps
- [ ] Propose planning-artifact disposition (commit vs trash) — user confirmation
