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

## Conventions

- See [README.md](README.md) for project overview
