---
name: markdown-generation
description: Industrial protocol for generating lint-compliant, high-fidelity markdown documentation.
category: Documentation-Standards
---

# Markdown Generation Skill (v1)

This skill provides a standardized protocol for generating Markdown that complies with the **Industrial standard**
(120-character line limit) and passes `markdownlint-cli2` (markdown linting CLI tool) audits.

*

## 1. Core Syntax Standards

Every generated file MUST adhere to these absolute constraints:

### 1.1 Line Length (MD013)

- **Limit**: 120 characters per line.
- **Exception**: Long URLs and file paths that cannot be broken. Use **Reference-style links** at the bottom of the
  document to resolve length violations for URLs.
- **Wrapping**: Proactively wrap descriptions and YAML blocks to stay under the limit.

### 1.2 Layout & Tables (MD060)

- **Table Alignment**: Use mathematically perfect aligned pipes (`|`).
- **Cell Spacing**: One mandatory space padding on both sides of every pipe (` | content | `).
- **Blank Lines**: Headers, lists, and code blocks MUST be surrounded by blank lines.

### 1.3 Frontmatter

- **Rules/Skills**: Use the triple-dash block (`---`) as defined in [ai-rule-standardization-rules.md](../../../ai-
agent-rules/ai-rule-standardization-rules.md).
- **General Docs**: Use the HTML comment block (`<!-- title: ... -->`) for indexing.

### 1.4 Cross-Reference Links & Anchors

The `markdownlint-cli2` tool validates anchors via **MD051 - Link fragments should be valid**.

- **Anchor Format**: For header `### Step 1 — Deep Change Analysis`, the anchor is `#step-1-deep-change-analysis`
- **Generation Rule**: Convert header to lowercase, replace spaces and `—` (em dash) with dashes (`-`)
- **Verification**: Run `markdownlint-cli2` - it will catch broken anchor errors (MD051)
- **Best Practice**: Always use anchors when linking to headers within skill/rule files

### 1.5 Path Verification

#### Default (CLI-Only)

- **Anchor**: Enforced by MD051 (built-in)
- **File Path**: NOT enforced - run manual verification:
    - `ls -la <path>` to confirm target exists
    - From `skills/<skill>/`: `ls ../<sibling-skill>/SKILL.md`
    - From `skills/<skill>/`: `ls ../../../ai-agent-rules/<rule>.md`

#### With Node.js Custom Rules (If Available)

Install and configure:

```bash
npm install --save-dev markdownlint-rule-relative-links
```

Add to `.markdownlint-cli2.jsonc` (NOT `.markdownlint.jsonc`):

```jsonc
{
    "customRules": ["markdownlint-rule-relative-links"],
    "config": {
        "relative-links": { "root_path": "." }
    }
}
```

Then both anchors AND file paths validated automatically.

*

## 2. Verification Workflow

Before finalizing ANY markdown file, the agent MUST:

1. **Config Initialization**: If the project lacks a `.markdownlint.jsonc` file, the agent
   MUST initialize it using rules from the reference config (`../../../.markdownlint.jsonc`
   relative to this skill file), incorporating the `MD013` 120-character line length exception.
2. **Sync Check**: Ensure `.vscode/settings.json` contains `"markdownlint.configFile": ".markdownlint.jsonc"` to
   synchronize the IDE extension with the project's Industrial standard.
3. **Run Markdown Lint Workflow**: Execute the full
   **[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md)** 3-step pipeline
   on the file:
   - Step 1: `markdownlint-cli2 --fix`
   - Step 2: Companion scripts in execution order
   - Step 3: Manual fix + final `markdownlint-cli2` audit
4. **Fidelity Verification**: Ensure the "Fidelity Mandate" (no loss of user technical specifics) is upheld during
   formatting.

*

## 3. Lint Fix Protocol

Companion scripts and the full 3-step lint fix pipeline have moved to
**[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md)**.

This skill delegates all lint-fix operations there. See that skill for:

- The 7 companion scripts (with descriptions and usage)
- Required execution order (table separators → fence language → wrap long
  lines → ...)
- Known `markdownlint-cli2 --fix` caveats (MD040 fence corruption)
- The convenience pipeline script `fix-markdown-pipeline.py`

*

## 4. Related Rules

- **SSOT**: [markdown-generation-rules.md](../../../ai-agent-rules/markdown-generation-rules.md)
- **Formatting Protocol**: [ai-rule-standardization-rules.md](../../../ai-agent-rules/ai-rule-standardization-rules.md)

*

## 5. CI Integration

### 5.1 Pipeline Script

When automating lint fixing in a CI pipeline or pre-commit hook, use the
convenience pipeline script from
**[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md#3-convenience-pipeline-script)**:

```bash
python3 .agents/skills/general/markdown-lint-workflow/scripts/fix-markdown-pipeline.py \
  file.md
```

This runs `markdownlint-cli2 --fix`, then all companion scripts in execution
order, then a final audit — all in one invocation. For individual companion
script usage, see the
[Markdown Lint Workflow skill](../general/markdown-lint-workflow/SKILL.md#2-companion-scripts).

### 5.2 YAML Frontmatter Validation

YAML frontmatter `description` values that contain colons followed by
YAML-reserved tokens (e.g., `resetMocks: true`) cause downstream parsers
(VS Code preview, `markdownlint-cli2`) to misinterpret the colon as a new
YAML key opening.

**Rule:** If a `description` value contains any colon (`:`) that is not
trailing whitespace or a URL scheme (`https://`), wrap the entire value in
double quotes (`"..."`). Bare unquoted descriptions containing internal
colons are FORBIDDEN.

*Correct:*

```yaml
---
description: "Repository-specific composer that uses the generic ai-suite skill for debugging missing toolbar features"
---
```

*Incorrect:*

```yaml
---
description: Repository-specific composer that uses the generic ai-suite skill for debugging missing toolbar features
---
```

The difference is invisible in most Markdown renderers but causes silent
YAML parse failures in editor preview panes and schema validators.

### 5.3 Lint Gate

Every skill authored via the Skill Factory (`skill-factory`) MUST pass the
full Verification Workflow (§2) including the
**[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md)** 3-step
pipeline before it is considered complete. The factory's Post-Drafting
Checklist (§3) is the SSOT for the gating criteria.
