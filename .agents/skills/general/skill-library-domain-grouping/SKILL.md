---
name: skill-library-domain-grouping
description: >-
  SSOT for the project-specific domain taxonomy and placement rules governing
  the skill library folder structure.
category: General-Domain
---

# Skill Library Domain Grouping (v1)

This skill is the **Single Source of Truth** for the domain-based folder
structure of this project's skill library. Every skill directory belongs in
exactly one leaf group defined below. Adding, removing, or relocating a group
requires an update to this document.

The taxonomy was designed following the
[`human-scanable-organization`](../human-scanable-organization/SKILL.md)
8±2 principle: every folder contains ≤10 items; folders exceeding that
threshold are sub-grouped recursively.

***

## Composition Rationale

This skill is a standalone SSOT — it does NOT compose any base skill. It is
consumed by:

- **[`human-scanable-organization`](../human-scanable-organization/SKILL.md)** —
  as the concrete worked example (§3) of the 8±2 principle.
- **[`skill-factory`](../../skill-factory/SKILL.md)** — whose Post-Drafting
  Checklist (§3) requires compliance with the taxonomy defined here before a
  new skill is considered complete.

***

## 1. Domain Taxonomy

### 1.1 Top-Level Domains

```text
.agents/skills/
├── cli/                          (7 items — flat)
├── database/                     (9 items — flat)
├── eclipse/                      (4 items — flat)
├── general/                      (12 flat + 4 sub-groups)
├── git/                          (7 sub-groups)
├── github/                       (6 flat + 2 sub-groups)
├── java/                         (3 items — flat)
├── jira/                         (4 items — flat)
├── json/                         (3 items — flat)
├── markdown/                     (2 items — flat)
├── maven/                        (1 item — flat)
├── mcp/                          (2 items — flat)
├── media/                        (10 items — flat)
├── mise/                         (3 items — flat)
├── node/                         (2 items — flat)
├── opencode/                     (3 items — flat)
├── php/                          (1 item — flat)
├── project/                      (7 items — flat)
├── python/                       (3 items — flat)
├── testing/                      (4 items — flat)
├── text/                         (4 items — flat)
└── vscode/                       (5 sub-groups)
```

### 1.2 Sub-Groups

**general/** (4 sub-groups; 12 flat items remain at general/ level):

```text
general/
├── code-explanation
├── file-glob-sort-by-regex-capture
├── fnmatch-content-guard-pattern
├── harper-linting-suppression
├── ide-renderer-freeze-prevention
├── json-batch-file-move
├── json-group-stats
├── kv-line-parse                  <- NEW
├── macos-screenshots-folder-split
├── onedrive-flat-folder-split-by-size
├── redaction-portability
├── repo-scratch-output-capture
│
├── comparison/               (2)
│   ├── folder-comparison
│   └── near-duplicate-file-comparison
│
├── setup/                    (4)
│   ├── dev-env-private-config-symlink
│   ├── google-oauth-setup
│   ├── tool-config-directory-symlink
│   └── tool-config-schema-probe
│
└── skill-dev/                (6)
    ├── rule-to-skill-industrialization
    ├── script-over-instruction-decomposition
    ├── script-language-tier-port
    ├── script-template-extraction
    ├── skill-cross-reference-audit
    └── skill-factory

└── session-audit/            (12)
    ├── agents-md-recovery-from-session
    ├── edit-application-from-session
    ├── file-recovery-from-session
    ├── opencode-session-bash-block-extractor
    ├── opencode-session-bash-file-ops-classifier
    ├── opencode-session-bash-write-extractor
    ├── opencode-session-diff-extractor
    ├── opencode-session-edit-extractor
    ├── opencode-session-write-extractor
    ├── session-audit-batch-orchestrator
    ├── session-file-ops-audit
    └── session-full-change-audit
```

**git/** (7 sub-groups):

```text
git/
├── basic/
│   ├── edit/                 (5) — atomic-commit-construction, commit-edit,
│   │                              noise-removal-via-commit-edit,
│   │                              separate-content-from-formatting-commits,
│   │                              drop-commit-with-divergent-recreation
│   ├── message/              (4) — commit-message-bulk-reword,
│   │                              commit-message-reword,
│   │                              commit-metadata-extraction,
│   │                              commit-identity-rewrite
│   ├── audit/                (7) — commit-comparison-audit,
│   │                              commit-details-audit,
│   │                              cross-ref-file-parity,
│   │                              divergence-audit,
│   │                              ref-content-audit,
│   │                              deleted-files-audit,
│   │                              git-repository-status
│   └── history/              (2) — history-refinement,
│                                   untracked-scratch-triage
│
├── branch/                   (5) — absorbed-branch-decommission,
│                                  branch-promotion,
│                                  dependent-branch-restack-cascade,
│                                  parallel-branch-decommission,
│                                  rebase-standardization
│
├── config/                   (6) — clean-filter-renormalize-backfill,
│                                  jq-pretty-json-filter,
│                                  post-gitignore-untrack,
│                                  gitignore-rules,
│                                  gitignore-whitelist-pattern,
│                                  gitignored-reference-detection
│
├── repo/                     (4) — canonical-source-vs-workflow-repo-audit,
│                                  cross-repo-cherry-pick,
│                                  lfs-selective-clone,
│                                  repo-storage-minimization
│
├── sandbox/                  (4) — personal-content-extraction,
│                                  personal-sandbox-remote,
│                                  personal-sandbox-restack,
│                                  personal-team-branch-workflow
│
├── stash/                    (3) — pre-execution-safety-stash,
│                                  stash-parent-commit,
│                                  stash-triage
│
└── submodule/
    ├── setup/                (4) — addition, selective-init-no-lfs,
    │                              uninitialized-audit,
    │                              uninitialized-handler
    ├── repair/               (5) — dead-upstream-audit,
    │                              misconfiguration-audit-and-revert,
    │                              missing-revision-recovery,
    │                              orphan-gitlink-recovery,
    │                              pointer-repair
    ├── fork/                 (2) — fork-reconfigure, fork-sync
    └── lifecycle/            (4) — commit-details, commit-reword,
                                   removal, readd
```

**github/** (6 sub-groups; 1 flat item remains at github/ level):

```text
github/
├── copilot/                  (2) — activity-history-split,
│                                  chat-history-analysis
├── actions/                  (2) — run-audit, workflow-dispatch
├── repo/                     (6) — gh-repo-create, gh-repo-edit-metadata,
│                                  pr-edit, repo-commit-fetch,
│                                  rest-api-fallback, secrets-bulk-set
├── community-standards/      (10) — issue-template-bug,
│                                   issue-template-feature,
│                                   issue-template-documentation,
│                                   pr-template, gitignore-template,
│                                   code-of-conduct, contributing-guide,
│                                   security-policy, support-docs,
│                                   readme-template
├── workflows/                (6) — ci-markdown-lint, ci-python-lint,
│                                  sync-description, sync-topics,
│                                  pr-labeler, workflow-creation
├── composer/                 (7) — repo-templates, ci-lint, sync,
│                                  workflows, docs, repo-template,
│                                  repo-publish
│
├── (flat: 1) — auth-fallback
```

**vscode/** (5 sub-groups):

```text
vscode/
├── autoapprove/              (2) — command-autoapprove-onboarding,
│                                  autoapprove-entry-consolidation
├── config/                   (4) — antigravity-version-checker,
│                                  extension-portability,
│                                  nginx-filetype-config,
│                                  state-vscdb-merge
├── search/                   (2) — search-exclude-glob,
│                                  search-exclude-submodules
├── settings/                 (5) — multi-scope-setting-write,
│                                  setting-schema-discovery,
│                                  settings-indent-override,
│                                  settings-promotion,
│                                  user-settings-symlink
└── terminal/                 (2) — terminal-fallback-via-vscode-tasks,
│                                  terminal-autoapprove-audit
```

**database/** (9 items — flat):

```text
database/
├── db-backup-bracketing-protocol
├── mariadb-check-autoincrement-trigger-fallback
├── mysql-capability-probe-pymysql
├── mysql-fk-hardening-workflow
├── pg-cluster-backup-compare
├── pg-cluster-mirror
├── postgres-local-dump-restore
├── remote-mysql-roundtrip-minimization
└── staging-env-fetch
```

**media/** (10 items — flat):

```text
media/
├── ffmpeg-lossless-concat
├── ffmpeg-lossless-split
├── media-audio-language-detect
├── media-timestamp-summary
├── webm-recording-interrupted-recovery
├── webm-recording-merge-with-filler
├── youtube-playlist-list
├── youtube-studio-settings
├── youtube-video-metadata-update
└── youtube-video-upload
```

**opencode/** (2 items — flat):

```text
opencode/
├── opencode-config-preserve
├── opencode-ssot-provider-ext-sync     <- NEW
└── opencode-permission-config
```

***

## 2. Placement Rules

### 2.1 New Skill Placement

1. Match the new skill's topic keyword to a leaf group in §1.2.
2. Place it in that leaf group (e.g., a new `git-commit-signing` skill goes
   under `git/basic/edit/`).
3. If no leaf group matches the topic:
   - Create a new leaf group within the parent domain.
   - Verify the parent folder's item count stays ≤10 after addition (use
     `directory-tree-audit` if uncertain).
   - If the parent exceeds 10, propose and apply sub-grouping before adding.
4. Sub-groups are flat leaves — a leaf group MUST NOT itself be sub-grouped
   unless it reaches ≥10 items.

### 2.2 Cross-Cutting Skills

Skills that span multiple domains (e.g., `redaction-portability` applies to
all files, not just one domain) belong in `general/` — not in a specific
domain folder. If `general/` exceeds 10 flat items, create a sub-group.

***

## 3. Change Protocol

### 3.1 Adding a Group

- Add the new group to the tree in §1.2 with its item count.
- State the rationale in a `## Changelog` entry.
- Update every skill that references §1.2 (cross-reference sweep per
  `skill-factory` §5.1).

### 3.2 Removing a Group

- Move remaining items to sibling groups or `general/` before removing.
- Remove the group listing from §1.2.
- Cross-reference sweep.

### 3.3 Renaming a Group

- Update the name in §1.2.
- If the folder on disk is renamed, cross-reference sweep every skill that
  links to it via relative path.

***

## 4. Changelog

### 2026-07-05 -- general/ flat expanded 11->12, opencode/ expanded 2->3

Added:

- `kv-line-parse` to `general/` flat list -- base key-value line parser script
- `opencode-ssot-provider-ext-sync` to `opencode/` flat list -- composer skill for SSOT->provider-extension sync workflow

Updated Section 1.1 tree counts and Section 1.2 listings.

### 2026-06-20 — github/ expanded: 3 new sub-groups + 1 sub-group promoted from flat

Added 30 new skills:

- **`github/repo/`** (6 items, promoted from flat): `gh-repo-create` (B1),
  `gh-repo-edit-metadata` (B2), plus 4 existing skills moved from flat.
- **`github/community-standards/`** (13 items): docs structure
  (`github-docs-structure`), docs readme (`github-docs-readme`),
  folder structure (`github-folder-structure`), issue/PR templates
  (B3-B6), `.gitignore` (B12), code of conduct (B13), contributing guide
  (B14), security policy (B15), support docs (B16), README template (B17).
- **`github/workflows/`** (6 items): markdown lint (B7), python lint (B8),
  sync description (B9), sync topics (B10), PR labeler (B11),
  workflow-creation (existing, moved from flat).
- **`github/composer/`** (7 items): repo-templates (C1), ci-lint (C2),
  sync (C3), workflows (C4), docs (C5), repo-template (C6),
  repo-publish (C7).

Flat reduced from 6 to 1 (`auth-fallback`). Updated §1.1 tree count.

### 2026-06-20 (batch 2) — post-drafting fix pack: 3 new base skills + 23 template files extracted

Added 3 missing base skills: `github-docs-structure` (docs/ tree),
`github-docs-readme` (docs/README.md), `github-folder-structure`
(repo skeleton). Extracted 23 embedded template strings into
standalone `.template` files. Fixed broken script path in C7
`publish-repo.py`. Added 4 missing See Also links in
`github-workflow-creation`. Removed 5 empty stub directories.

### 2026-06-20 — general/skill-dev/ expanded: 5→6 — skill-cross-reference-audit added

Added `skill-cross-reference-audit` — a base skill that automates auditing
the skill library for cross-reference issues (duplicates in Composition +
Related Skills, missing AGENTS.md, missing frontmatter, empty sections).
Consumed by skill-factory §3 Composition Audit step.

### 2026-06-20 — general/skill-dev/ expanded: 4→5 — script-template-extraction added

Added `script-template-extraction` — a base skill that automates the
Template Extraction Mandate (skill-factory §2.2.1.1 mandate #6) for
existing scripts that embed file content as string constants. Alphabetized
the skill-dev listing.

### 2026-06-20 — opencode/ domain added (1 item)

New domain for opencode tool configuration skills. Initial member:
`opencode-permission-config`. Added `opencode/` to the §1.1 tree
and created the flat listing in §1.2.

### 2026-07-02 — general/setup/ expanded: 3→4 — tool-config-directory-symlink added

Added `tool-config-directory-symlink` — generic base skill for migrating tool
configuration directories (XDG) into a managed companion repo with symlinks.
Placed under `general/setup/` as a cross-cutting infrastructure primitive.
Also added `opencode-config-preserve` to `opencode/` domain (now 2 items).

### 2026-07-04 — general/session-audit/ new sub-group (12 items): session export audit skills

Added 12 session-export audit skills as a new `session-audit/` sub-group under
`general/`:

- `agents-md-recovery-from-session` — AGENTS.md recovery via git diff extraction
- `edit-application-from-session` — replay Tool: edit operations onto disk
- `file-recovery-from-session` — recover files from Tool: write + bash heredocs
- 4 opencode-session extractors (bash-block, bash-file-ops-classifier,
  bash-write, diff, edit, write) — base primitives for session parsing
- `session-audit-batch-orchestrator` — batch audit across multiple session files
- `session-file-ops-audit` — bash-only file operations audit
- `session-full-change-audit` — unified all-source change audit
Updated §1.1 tree from 3 sub-groups to 4; flat count unchanged (11 items).

### 2026-07-01 — fnmatch-content-guard-pattern added to general/ flat list

Added `fnmatch-content-guard-pattern` to general/ flat listing.
Updated count from 10 to 11 in §1.1 tree.

***

### 2026-06-17 — general/ flat expanded from 6→10

Added 4 OneDrive flat-folder split skills that sit at the intersection of
file-management, JSON processing, and macOS domain knowledge — too
cross-cutting for a specific domain folder:

- `json-batch-file-move` — batch file moves keyed by JSON array
- `json-group-stats` — JSON array group-by with count
- `macos-screenshots-folder-split` — domain composer wrapping the below
- `onedrive-flat-folder-split-by-size` — composer for OneDrive threshold splitting

Updated count from 6 to 10 in §1.1 tree; added entries to the flat listing
in §1.2.

***

### 2026-06-16 — database/ expanded from 6→9

Added 3 general database skills from oleovista-acers generalization:

- `pg-cluster-backup-compare` — ClusterSplit backup + dump compare protocol
- `pg-cluster-mirror` — Five-phase cluster mirror with audit-before-act
- `staging-env-fetch` — .env fetch from staging via ssh-staging MCP tool

Updated count from 6 to 9 in §1.1 tree; added detailed flat listing under §1.2.

***

## 5. Related Skills

- [`human-scanable-organization`](../human-scanable-organization/SKILL.md) —
  the 8±2 principle that governed this taxonomy's design.
- [`skill-factory`](../../skill-factory/SKILL.md) — consumer whose Post-Drafting
  Checklist enforces compliance with this taxonomy.
- [`directory-tree-audit`](../directory-tree-audit/SKILL.md) — tool for
  verifying item counts during placement decisions.
