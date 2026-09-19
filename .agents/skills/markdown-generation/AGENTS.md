# AGENTS.md (Markdown Generation)

Refer to [SKILL.md](./SKILL.md) and [markdown-generation-rules.md](../../../ai-agent-rules/markdown-generation-rules.md)
for the active operational protocol for generating lint-compliant documentation.

## Mandates

- **Line Length**: 120-character limit (MD013).
- **Lint Fix**: Run the full 3-step
  **[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md)** pipeline
  before submission (Step 1: `markdownlint-cli2 --fix`, Step 2: companion scripts
  in execution order, Step 3: manual fix + audit).
- **Zero Angle Brackets**: Escaping all `<` and `>` tags in technical context.
