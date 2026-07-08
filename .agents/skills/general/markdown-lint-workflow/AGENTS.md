# AGENTS.md (Markdown Lint Workflow)

Refer to [SKILL.md](./SKILL.md) for the active operational protocol for the 3-step markdown lint fix pipeline.

## Mandates

- **Pipeline Steps**: Run the full 3-step pipeline in order — Step 1: `markdownlint-cli2 --fix`, Step 2: companion
scripts in §2.1 execution order, Step 3: manual fix + final `markdownlint-cli2` audit.
- **Script Invocation**: Use the convenience script `scripts/fix-markdown-pipeline.py` for one-shot execution, or call
companion scripts individually with `--check` for dry-run.
- **Execution Order**: Companion scripts MUST run in the order defined in §2.1 to avoid re-introducing lint errors.
- **MD040 Caveat**: Do NOT use `markdownlint-cli2 --fix` for MD040 — use `fix-fenced-code-language.py` which correctly
handles fence state.
- **Post-Fix Check**: After running the pipeline, verify continuation-line indent with `list-indent-consistency` skill.

## Cross-References

- `markdown-generation` — consumes this skill for post-generation linting
- `skill-factory` §3 — consumes this skill for post-drafting linting
- `list-indent-consistency` — detect and repair indent drift after fix scripts
- `markdownlint-cli2` — the underlying lint tool
