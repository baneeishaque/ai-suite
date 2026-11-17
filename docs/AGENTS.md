# Documentation Guidance

## Purpose

Own local documentation, research reports, and planning artifacts under `docs/`.

## Ownership

- Root instructions in [AGENTS.md](../AGENTS.md) apply.
- This file owns documentation placement and the child index; children own their subject-specific evidence contracts.
- `implementation-plans/` retains session-scoped plans and live task checklists.
- `research/` holds topic-organized research for human readers.

## Local Contracts

- Use descriptive kebab-case names, with conventional `README.md` and `AGENTS.md` filenames where appropriate.
- Keep conclusions distinct from source quotations, author claims, and locally verified results.
- Keep research self-contained and link to primary public evidence where available.
- Follow the root distinction between local-only documentation and public repository content.

## Work Guidance

- Give readers a clear entry point and explain unfamiliar terms before using them in implementation comparisons.
- Preserve earlier planning artifacts; retire them only under the root artifact-retirement contract.
- Commit review previews: show labelled head excerpts for added, modified, and deleted text files; show a full file
  patch only when explicitly requested. Default to 20 diff-content lines and 240 characters per preview line, stating
  omissions and preserving complete reconstruction patches. Place metadata with each commit preview instead of
  duplicating commit-list tables.
- Commit cards: keep scope once rather than repeating an `On master` boolean. Distinguish exact commit-SHA membership,
  stable patch-ID matches, and file/blob coverage; show matching patch and commit IDs and explain retention labels.
  Avoid visible parent headings that repeat the commit ID; preserve navigation with anchors and labelled patch links.
- Do not repeat the ordinal or SHA when the commit heading already contains them. Use compact hard line breaks for
  metadata, colocate literal message blocks and detailed path-level reasons, and link dependents from prerequisite cards.
  Combine each parent descriptor with one size-labelled `preview` link to the complete patch.
- Compute preservation dependencies only after applying explicit exclusions. A removed change must not force its
  prerequisite to stay; recompute dependency links and explain any retained non-excluded portion of a mixed commit.
- Retain historical dependency evidence, including dropped/inactive dependents, in the review. Label inactive edges
  as non-blocking rather than removing the links. Distinguish original file-lifecycle edges from projected dependencies.
- Show exact current source-HEAD content coverage in target HEAD separately from historical transition coverage.
  Evaluate file purpose and individual configuration-rule relevance; a missing historical transition alone does not
  justify retaining an out-of-scope file or an ignore rule targeting excluded files.
- Prefer Markdown review. Generate a PDF only on explicit request and obtain confirmation before retiring an existing
  PDF. Do not infer a universal rendering-size limit from individual successes or failures.
- Analyse shared IDE/configuration files at the individual-setting level against retained files and the active job;
  avoid blanket whole-file retention or exclusion. Show separate projected outcomes for merge-parent comparisons.
- For every fully excluded file, colocate its complete audited history and all parent-relative head previews once under
  the introducing commit. Link other metadata/history/diff occurrences to that lifecycle. This applies to all exclusion
  categories, not only development files. Retain exact original patches and quoted messages; do not infer rename identity
  without proof. Partially retained files keep their per-commit setting review.
- Render each patch-content identity once. The first occurrence is canonical; later identical modifications, copies,
  renames without content change, and permission-only changes link to it instead of repeating the preview. Detect renames
  as same-blob delete/add pairs when rename metadata is absent. Verify every reference resolves to an earlier anchor and
  every original section is still represented exactly once.
- Partially retained shared settings: analyze each setting, keep only the approved atom(s), and project the smallest
  file containing them. Show one setting-level table per changed version; do not treat the path as fully dropped.
- SQL dump refreshes: drop a commit only when its sole change is the dump completion timestamp. Keep server/dump
  version changes (including their completion time) and all content changes. Explain invisible whitespace-only changes
  explicitly instead of leaving the reviewer to infer them from a diff.
- Repeated setting-level tables: consolidate one canonical history with per-block anchors. Every commit card links to
  its anchor instead of repeating the table.

- Planning-document updates follow the root document-versioning preference; append-only additions preserve
  the existing document's information rather than forcing a successor version.
- For planned files carrying pre-existing changes, include per-entry comparisons of HEAD to the pre-existing state,
  pre-existing state to the proposed merged result, and HEAD to the task-only result excluding unrelated changes.
  Analyze all three and recommend how to preserve existing work. Label absent-HEAD prerequisites explicitly.
- Show correct fenced Markdown previews and complete reconstruction links. Expose relevant space, indentation,
  newline, and other non-printable changes explicitly; do not expand unrelated whitespace noise.

## Verification

- Run the standalone `/opt/homebrew/bin/markdownlint-cli2` from the repository root on changed Markdown files.
- Confirm that local document links resolve and that quoted sources support the stated conclusions.

## Child DOX Index

- [`coderabbit-review-queue/AGENTS.md`](coderabbit-review-queue/AGENTS.md) owns local queue configuration,
  persistent review-request state, deployment records, and cron monitoring.
- [`research/development-environments/code-server-vs-vscode-insiders/AGENTS.md`][settings-comparison-dox]
  owns the exhaustive settings comparison, installed-version evidence, endpoint and permission audits,
  and beginner-oriented configuration explanations.
- [`research/vscode/editor-tab-compare-extensions/AGENTS.md`][vscode-tab-compare-dox]
  owns the VS Code editor-tab compare extensions research, including the comparison of
  in4margaret.compareit, moshfeu.diff-merge, DavidKol.fastcompare, and outofsync42.select-compare-tabs,
  with maintainer evidence and candidate recommendations.
- [`research/code-review/github-pr-audit-signals/AGENTS.md`][pr-audit-signals-dox]
  owns ECC Tools audit meanings, GitHub check permissions, Sonar/SemanticDiff/CodeRabbit comment lifecycle,
  and the distinction between workflow runs, jobs, checks, and coverage evidence.
- [`research/code-review/coderabbit-bot-pull-requests/AGENTS.md`][coderabbit-bot-dox]
  owns bot-authored PR review research, maintainer evidence, and reproducible PR conversation/workflow evidence exports.
- [`research/browser-automation/chrome-password-autofill/AGENTS.md`][autofill-dox]
  owns Chrome password-autofill research, maintainer evidence, background-operation requirements, and candidate routes.
- [`research/browser-automation/cloudflare-refuseless/AGENTS.md`][refuseless-dox]
  owns Refuseless access research, Cloudflare tooling comparisons, maintainer evidence, and new-account onboarding gates.
- [`research/opencode/providers/experiential-labs/AGENTS.md`][experiential-research-dox]
  owns Experiential Labs catalog/access/billing research and the durable evidence bundle.
- [`research/opencode/providers/bailu-ai/AGENTS.md`][bailu-research-dox]
  owns Bailu exact-ID catalogs, verified-free visibility/naming, OpenCode compatibility, input-length context,
  and portable sanitized audit evidence.
- [`guides/opencode/AGENTS.md`][opencode-guides-dox]
  owns local OpenCode setup guides, provider operations, and dated investigations.

[autofill-dox]: research/browser-automation/chrome-password-autofill/AGENTS.md
[refuseless-dox]: research/browser-automation/cloudflare-refuseless/AGENTS.md
[experiential-research-dox]: research/opencode/providers/experiential-labs/AGENTS.md
[bailu-research-dox]: research/opencode/providers/bailu-ai/AGENTS.md
[opencode-guides-dox]: guides/opencode/AGENTS.md
[coderabbit-bot-dox]: research/code-review/coderabbit-bot-pull-requests/AGENTS.md
[pr-audit-signals-dox]: research/code-review/github-pr-audit-signals/AGENTS.md
[settings-comparison-dox]: research/development-environments/code-server-vs-vscode-insiders/AGENTS.md
[vscode-tab-compare-dox]: research/vscode/editor-tab-compare-extensions/AGENTS.md
