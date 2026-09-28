# Task — Document the Skill-Folder Relocation Workflow as Reusable Layered Skills

Session: `ses_f1dd554edffeIjEwbPkY123xx1` · Worktree: `/Users/dk/lab-data/ai-suite-worktrees/migrate-rule-file-into-skill`

## Phase 0 — Planning Artifacts

- [x] Pre-plan context gathering (skills, scripts, rules, taxonomy, registry) `[2026-09-27 16:25]`
- [x] Write implementation-plan v1 `[2026-09-27 16:25]`
- [x] Lint plan + task (markdownlint-cli2) `[2026-09-27 16:28]`
- [x] Present plan for user approval `[2026-09-27 16:28]`

## Phase 1 — C1: NEW base `markdown-relative-link-rebase-on-path-move`

- [ ] Create `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`
- [ ] Create `scripts/rebase-relative-links.py` (Tier 1)
- [ ] Smoke-test: fixture `--check`/`--apply`/re-`--check`; real-map regression `--check`
- [ ] Taxonomy `markdown/` 4 → 5 + Changelog
- [ ] Register row in `AGENTS-legacy.md` (alphabetical)
- [ ] §6 checks + commit C1

## Phase 2 — C2: NEW base `git-linked-worktree-root-resolve`

- [ ] Create `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`
- [ ] Create `scripts/resolve-worktree-roots.py` (Tier 1)
- [ ] Smoke-test: worktree run (`is_linked_worktree: true`) + main-repo run (`false`)
- [ ] Taxonomy `git/repo/` 4 → 5 + Changelog
- [ ] Register row in `AGENTS-legacy.md` (alphabetical)
- [ ] §6 checks + commit C2

## Phase 3 — C3: NEW composer `skill-library-folder-relocation`

- [ ] Create `SKILL.md`, `AGENTS.md`, `CHANGELOG.md`, `TRACEABILITY.md`
- [ ] Create `scripts/relocate-skill-folder.py` (Tier 1)
- [ ] Dry-run composer against scratch fixture skill tree
- [ ] Taxonomy `general/skill-dev/` 6 → 7 + Changelog
- [ ] Register row in `AGENTS-legacy.md` (alphabetical, composer annotation)
- [ ] Cross-references (§3.5): skill-factory §5.1 + §2.4, taxonomy §3.3, dangling-audit, markdown-generation
- [ ] §6 checks + commit C3

## Phase 4 — Enrichments

- [ ] ENRICH-1 `git-commit-preview-verify`: script fix + SKILL.md edge case → commit C4
- [ ] ENRICH-2 `opencode-current-session-id`: worktree fallback + SKILL.md → part of C5
- [ ] ENRICH-3 `scratch-artifact-naming`: worktree-aware discovery + SKILL.md → part of C5
- [ ] ENRICH-4 `markdown-lint-workflow`: custom-rule prerequisite note → commit C6

## Phase 5 — Close-out

- [ ] Full §6 verification matrix
- [ ] `task.md` statuses + timestamps
- [ ] Propose planning-artifact disposition (commit vs trash) — user confirmation
