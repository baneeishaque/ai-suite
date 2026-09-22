# AGENTS.md

## ⚠️ Permanent Operating Reminders (read every boot)

1. **Atomize exploration chains.** Never combine multiple unfamiliar-path
   probes into one `&&` / `|` chain with `2>/dev/null` suppression — it
   silently hangs when a path is missing. Issue independent shell calls (use
   parallel tool calls for unrelated probes). See
   [`ai-agent-rules/shell-execution-rules.md` §2.3.1](ai-agent-rules/shell-execution-rules.md).
2. **Never nest heredocs inside heredocs.** When using
   `python3 - <<'PY'` whose body contains a Python triple-quoted string,
   the inner content MUST NOT contain heredoc-sentinel-looking tokens
   (`EOF`, `PY`, `MARKEREOF`, etc.) or fenced code blocks — the outer
   heredoc terminates early and the call silently hangs. Use a
   two-stage `cat > /tmp/payload <<'ZZZ_UNIQUE_ZZZ'` then a separate
   `cat > /tmp/script.py <<'ZZZ_OTHER_ZZZ'` then run the script. Each
   stage carries one heredoc with a body-unique sentinel. See
   [`ai-agent-rules/shell-execution-rules.md` §2.3.3](ai-agent-rules/shell-execution-rules.md).
3. **Bound tool-output size AND cumulative scrollback to protect the IDE renderer.** Large outputs
   streamed into the chat transcript (recursive `grep -r` over many-file
   trees, `cat` on minified bundles, full dumps of files like
   `workbench.desktop.main.js`) can freeze the VS Code renderer; the user's
   only recovery is to force-quit, which reports every in-flight tool call
   back as `interrupted` and drops live shell sessions. Default behavior:
   redirect large commands to `/tmp/out.txt` first, then `head` / `grep` /
   `view` it; prefer the built-in `grep` / `glob` / `view` tools over
   shell-side recursive scans; narrow scope with `glob` before `grep`; and
   never combine "produce a large output" with "read a large file" in the
   same tool-call batch. See
   [`ai-agent-rules/shell-execution-rules.md` §2.3.4](ai-agent-rules/shell-execution-rules.md).
   Single-output size is necessary but not sufficient — long sessions also
   freeze the renderer from cumulative many-small-outputs pressure, so on
   long sessions prefer `view_range` over full-file `view`, prefer
   file-write over stdout for intermediate artifacts, do NOT re-print
   content already in scrollback, skip trailing verification dumps, and
   pause-to-consolidate after ~20 tool calls per user message. See
   [`ai-agent-rules/shell-execution-rules.md` §2.3.4.1](ai-agent-rules/shell-execution-rules.md).
   The full catalogue of freeze patterns, the eleven-item per-call self-audit
   checklist, and the post-freeze recovery protocol — collected across
   reminders §1–§4 above and reified as one skill — are owned by
   [`.agents/skills/ide-renderer-freeze-prevention/SKILL.md`](.agents/skills/ide-renderer-freeze-prevention/SKILL.md).
4. **Prefer scripts over prose instructions — both when authoring AND when
    consuming a skill.** Scripts are more deterministic than rules, skills,
    or sub-agent prompts.
    *Authoring side*: when designing or refactoring a skill/rule/sub-agent,
    decompose its procedure — every deterministic step (parse, transform,
    validate, file-mutate) MUST live in an executable script under the
    skill's `scripts/` directory; prose retains only judgement, branching,
    and human-gates.
    *Consumer side* (fires on EVERY skill invocation): before executing any
    deterministic step described in a skill's prose, FIRST list that skill's
    `scripts/` directory (`ls <skill-dir>/scripts/` or the in-process `glob`
    tool) and invoke the matching script — do NOT re-derive the logic
    ad-hoc from the prose. Re-typing a multi-step recipe inline when the
    skill ships a script for it is a violation even when the inline output
    is correct, because it bypasses the script's idempotency checks,
    env-var validation, and SSOT updates. Fall through to manual recipe
    only if no script matches the step.
    See
    [`.agents/skills/script-over-instruction-decomposition/SKILL.md`](.agents/skills/script-over-instruction-decomposition/SKILL.md)
    `## Consumer Discipline — Always Invoke, Never Re-derive`.
5. **Do NOT probe into heavy-filewatcher symlinked trees; address files
   by exact path.** Walking a directory that fans out into symlinked
   private-config / cloud-sync / IDE-indexed subtrees (specifically
   `/Users/dk/Lab_Data/configurations-private/` in this workspace)
   triggers fsevents / Spotlight / IDE-indexer cascades that freeze
   the IDE renderer; the user must force-recover, which reports every
   in-flight tool call as `interrupted`. Read files inside such trees
   by EXACT absolute path (e.g.
   `cat /Users/dk/Lab_Data/configurations-private/Account-Ledger-Server/act.secrets`);
   never `ls`, `find`, or `grep -r` against the tree to discover the
   path first. Use the built-in `glob` / `grep` / `view` tools for any
   necessary tree walk. Note: `/Users/dk/Lab_Data/` (private configs)
   and `/Users/dk/lab-data/` (code repos) are DISTINCT sibling
   directories — case AND punctuation differ — not the same path
   reached through case-folding. Case-insensitive volumes (macOS APFS,
   Windows NTFS) DO add a minor case-folding amplifier when a
   mis-cased path also targets a filewatcher-heavy tree, so the
   secondary "derive canonical casing from `ls` of a known-light
   parent / known-good git artifact / env var / cwd" rule still
   applies. Compounds with reminder #1 — never bundle a heavy-tree
   probe inside a chained call. See
   [`ai-agent-rules/shell-execution-rules.md` §2.3.1.1](ai-agent-rules/shell-execution-rules.md).
   (Re-attributed May 2026 from the original case-folding diagnosis,
   which was incomplete. Further extended May 2026 after a plain
   `bash ls .agents/skills/` froze the renderer — confirming the
   hazard covers ANY directory with wide fan-out under active IDE
   watchers, not only symlinked private-config trees. The same
   incident — and a follow-up `bash grep -r /Users/dk/lab-data/<repo>`
   freeze in the same workspace — also proved that `edit` / `create`
   tool calls issued
   during the post-freeze drain window are themselves reported as
   `interrupted`; recover via `bash` heredoc writes first.)
6. **Prefer the built-in `grep` / `glob` / `view` tools over `bash grep` /
   `find` / `cat`.** The host runtime exposes first-class code-search
   tools that respect tool-output sizing, scrollback hygiene, and the
   §2.3.1 atomization rule. Falling back to `bash grep` (or `rg` inside
   a chained command) reintroduces every freeze hazard those tools
   were built to eliminate — most acutely: passing `-r` / `-R` alongside
   *explicit file paths* is a contradiction that on some ripgrep
   versions degrades into a recursive walk of the current working
   directory, which on a large monorepo with active filewatchers can
   freeze the IDE renderer. Rules:
   - When searching file contents, use the **`grep` tool** with `paths`
     pinned to specific files or directories — never `-r` with explicit
     paths.
   - When finding files by name, use the **`glob` tool**.
   - When reading files, use the **`view` tool** with `view_range` for
     large files.
   - Fall back to `bash` only when the built-in tool cannot express the
     query (e.g. piped post-processing the tool does not support).
   See
   [`ai-agent-rules/shell-execution-rules.md` §2.3.1.2](ai-agent-rules/shell-execution-rules.md).
7. **Always use `trash` instead of `rm` or `rmdir` on macOS.** `trash` moves files and directories to
   `~/.Trash` (recoverable) instead of permanently deleting them. Use `trash` for all file and directory
   deletions unless the user explicitly asks for permanent removal.
8. **Never touch `.DS_Store` files on macOS.** Do not read, write, move, trash, or delete `.DS_Store`
   files by any means. They are Finder metadata files managed by the OS and should be left completely
   untouched.
9. **When the user asks "which skills cover X", answer in ONE pass with, per relevant skill:** the skill
    name, a one-line description, and the skill's file listing with ABSOLUTE paths (tree for a skill folder;
    the absolute path alone for a single-file skill).
10. **Pre-commit, run the dangling-link audit** via the `git-commit-dangling-link-audit` composer
    (`detect-dangling-links.py` over the commit's SKILL.md/AGENTS.md/changelog files) — flag DANGLES
    for user disposition (FOLD / RESOLVE-NOW / KEEP-AS-IS) rather than silently fixing stale links;
    also sweep `/tmp` scans for session-evidence drift before reporting final verdicts.

## Conventions

- See [README.md](README.md) for project overview

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes_tool` or `query_graph_tool` instead of Grep
- **Understanding impact**: `get_impact_radius_tool` instead of manually tracing imports
- **Code review**: `detect_changes_tool` + `get_review_context_tool` instead of reading entire files
- **Finding relationships**: `query_graph_tool` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview_tool` + `list_communities_tool`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
| ------ | ---------- |
| `detect_changes_tool` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context_tool` | Need source snippets for review — token-efficient |
| `get_impact_radius_tool` | Understanding blast radius of a change |
| `get_affected_flows_tool` | Finding which execution paths are impacted |
| `query_graph_tool` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes_tool` | Finding functions/classes by name or keyword |
| `get_architecture_overview_tool` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes_tool` for code review.
3. Use `get_affected_flows_tool` to understand impact.
4. Use `query_graph_tool` pattern="tests_for" to check coverage.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **ai-suite** (18776 symbols, 19715 relationships, 32 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({search_query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.
- For security review, `explain({target: "fileOrSymbol"})` lists taint findings (source→sink flows; needs `analyze --pdg`).

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/ai-suite/context` | Codebase overview, check index freshness |
| `gitnexus://repo/ai-suite/clusters` | All functional areas |
| `gitnexus://repo/ai-suite/processes` | All execution flows |
| `gitnexus://repo/ai-suite/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

<!-- REPOWISE_AGENTS:START — Do not edit below this line. Auto-generated by Repowise. -->
## Codebase Intelligence for ai-suite (Repowise)

Indexed by [Repowise](https://repowise.dev). Last indexed: 2026-09-15 (commit eaedbc3). Confidence: 95%.
### How to work in this repo

- **Trust the index.** `verified: true` and `_meta.complete` mean the bytes were checked against the live tree, so never re-read them. Re-read only what `bounds: "approximate"` or `_meta.stale_warning` names. `confidence` rates the prose, not the evidence: on `low` read the `fallback_targets` or `best_guesses` the reply names, and run `repowise update` and ask again if `_meta.hint` says the index is behind HEAD. `index_behind: true` alone is informational.
- **A zero carries its basis.** An empty `callers`/`callees`/`used_by` comes with a `*_basis` saying how much of that language's calls the graph resolved, so read it before concluding nothing calls a symbol. `_meta.scope_hint` names the areas the answer did not touch.
- **Pre-edit, not instead-of-edit.** These tools decide *which* files to read and edit. Reading a file before you edit it is correct and expected.
- **Noisy commands** (tests, builds, `git log`/`diff`, searches, listings): prefer `repowise distill <cmd>`, the same command with its exit code preserved and errors-first output. A `[repowise#<ref>: N lines omitted]` marker is recoverable via `repowise expand <ref>` (add `-q <regex>` to filter); never re-run the command to see omitted output.
- **Recording a decision** you had to reason out: `repowise decision add --title T --decision D` records it without prompting and prints the id (`--format json` to parse it back). It lands `proposed`, for a person to confirm.

### Tools

| Tool | When and why |
|------|--------------|
| `get_answer(question)` | First call for any how/where/why question. Cite `confidence: "high"` or `grounding: "extracted"` directly; `degraded` means judge by `retrieval_quality`. `symbol_bodies` has live bodies. |
| `get_context(targets=[...])` | Triage card for files/modules/symbols: docs, signatures, hotspot, fix history. No source bytes — `include=["skeleton"]` for the whole file verified, `["callers"|"decisions"]` for depth. Batch targets. |
| `get_symbol(id, depth?)` | **Follow-up, not an entry point** — one verified body for an id a prior response named (`path.py::Name`, `path.py:140-180`, `repowise#<hex>`). Never walk a file symbol by symbol; Read it. |
| `search_codebase(query)` | Hybrid search, auto-routed by query shape; force with `mode=symbol|path|concept|hybrid`. A hit whose `sources` are `[fts]` only has no semantic agreement, so verify it. |
| `get_why(query, targets?)` | Why the code is shaped this way: decision records, git archaeology, rationale comments. Call before a refactor or a pattern divergence. |
| `get_risk(targets, changed_files?, include?)` | File history and structural reach. PR mode leads with `directive`; its 0-10 structural heuristic is uncalibrated, not a probability. Read typed test recommendations and coverage state first. |
| `get_change_risk(revspec?, extensions?, exclude_patterns?)` | Deterministic live-diff review signal for a commit or range. Lead with benchmarked percentile/classification; the 0-10 diff-shape score is supporting, not a probability. `get_risk` scores paths. |
| `get_health(targets?, include?)` | Defect / maintainability / performance scores and findings. Self-check the files you touched before finishing. |
| `get_dead_code(tier?, min_confidence?, safe_only?)` | Confidence-tiered unreachable files / unused exports / zombie packages. For cleanup sweeps, not targeted fixes. |
| `get_overview()` | Architecture map. Call once, first, in an unfamiliar repo; skip it after that. |

### Architecture
**Files:** 6220 | **Lines:** 5594003 | **Monorepo:** 2 packages
ai-suite is a multi-package yaml codebase of 6220 files, split across 2 packages. Execution starts at ai-agent-rules/architectures/sync/samples/cra-project/src/App.tsx, ai-agent-rules/architectures/sync/samples/vite-project/src/App.tsx, ai-agent-rules/architectures/sync/samples/vite-project/src/main.tsx. Start here when reading the codebase. Ranked by PageRank over the import graph: the files most of the codebase ultimately depends on.

### Key modules
- `root` — ai-agent-rules/architectures/sync/packages/core/src · ai-agent-rules/architectures/sync/samples/shared/src ·…

### Entry points
- `ai-agent-rules/architectures/sync/samples/vite-project/src/main.tsx`
- `ai-agent-rules/architectures/sync/samples/vite-project/src/App.tsx`
- `ai-agent-rules/architectures/sync/samples/cra-project/src/App.tsx`
- `scripts/teams-chat-nav/teams-chat-nav-inject.js`
- `scripts/teams-chat-nav/teams-read-messages-inject.js`
- `scripts/wa-chat-read/wa-chat-read-inject.js`

### Files that need care (bug-fix history first, then churn — check `get_risk` before editing)
- `copilot-plugins/copilot-session-logger/lib/copilot-transcript.js` — 2 bug fixes, last fix today; 3 commits/90d
- `copilot-plugins/copilot-session-logger/lib/router.js` — 2 bug fixes, last fix today; 3 commits/90d
- `copilot-plugins/copilot-session-logger/lib/core.js` — 2 bug fixes, last fix today; 3 commits/90d
- `.agents/skills/brew-upgrade-workflow/scripts/run-brew-upgrade.py` — 1 bug fix, last fix 6 weeks ago; 3 commits/90d
- `session-tracker.yaml` — 67 commits/90d

### Code health
Three co-equal signals: code health 7.26/10 avg (Good), hotspot health 4.74/10 (improving), worst `cline-plugins/cline-session-logger/lib/router.js` at 2.13/10 · maintainability 6.37/10 · performance risk 30 open static I/O-in-loop / N+1 findings. Detail: `get_health()`.

Critical files:
- `cline-plugins/cline-session-logger/lib/router.js` — change entropy — impact −3.0
- `cline-plugins/cline-session-logger/lib/core.js` — change entropy — impact −3.0
- `cline-plugins/cline-session-logger/lib/router.js` — brain method (handle) — impact −0.7
- `cline-plugins/cline-session-logger/lib/router.js` — complex method (handle) — impact −0.5
- `copilot-plugins/copilot-session-logger/lib/router.js` — complex method (handle) — impact −0.5

<!-- REPOWISE_AGENTS:END -->
