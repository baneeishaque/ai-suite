---
name: markdown-generation
description: Industrial protocol for generating lint-compliant, high-fidelity markdown documentation.
category: Documentation-Standards
---

# Markdown Generation Skill (v1)

This skill provides a standardized protocol for generating Markdown that complies with the **Industrial standard**
(120-character line limit) and passes `markdownlint-cli2` (markdown linting CLI tool) audits.

***

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

- **Rules/Skills**: Use the triple-dash block (`---`) as defined in [ai-rule-standardization-rules.md](../../../ai-agent-rules/ai-rule-standardization-rules.md).
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

***

## 2. Verification Workflow

Before finalizing ANY markdown file, the agent MUST:

1. **Config Initialization**: If the project lacks a `.markdownlint.jsonc` file, the agent
   MUST initialize it using rules from the reference config (`../../../.markdownlint.jsonc`
   relative to this skill file), incorporating the `MD013` 120-character line length exception.
2. **Sync Check**: Ensure `.vscode/settings.json` contains `"markdownlint.configFile": ".markdownlint.jsonc"` to
   synchronize the IDE extension with the project's Industrial standard.
3. **Auto-Fix**: Run `markdownlint-cli2 --fix <file_path>` from the project root.
4. **Audit Check**: Run `markdownlint-cli2 <file_path>`.
5. **Manual Correction**: Fix any remaining semantic or structural errors (e.g., heading increments).
6. **Fidelity Verification**: Ensure the "Fidelity Mandate" (no loss of user technical specifics) is upheld during
   formatting.

***

## 3. Companion Scripts

This skill ships seven helper scripts under
[`scripts/`](scripts/) for one-shot lint fixes:

- [`fix-table-separators.py`](scripts/fix-table-separators.py) — scans for
  compact table separators (`|---|---|`) and rewrites them with proper spacing
  (`| --- | --- |`) to satisfy MD060. Use `--check` for dry-run.
- [`wrap-long-lines.py`](scripts/wrap-long-lines.py) — wraps prose lines
  exceeding the configured `--max` width (default 120) while preserving code
  blocks, tables, YAML frontmatter, and list structure. Use `--check` for
  dry-run.
- [`fix-fenced-code-language.py`](scripts/fix-fenced-code-language.py) — adds
  a default language tag (default `text`) to bare opening fenced code blocks
  to satisfy MD040. Properly undoes `markdownlint-cli2 --fix` damage that
  attaches `text` to closing fences. Use `--default <lang>` to override the
  language (default: `text`). Use `--check` for dry-run.
- [`fix-emphasis-as-heading.py`](scripts/fix-emphasis-as-heading.py) — strips
  emphasis markers (`*...*`, `_..._`) from lines that are standalone
  emphasis-as-heading paragraphs to satisfy MD036. Use `--check` for dry-run.
- [`fix-list-style.py`](scripts/fix-list-style.py) — converts asterisk
  unordered list markers (`*`) to dash style (`-`) to satisfy MD004.
  Use `--check` for dry-run.
- [`fix-heading-spacing.py`](scripts/fix-heading-spacing.py) — inserts a blank
  line before headings that lack one to satisfy MD022. Skips YAML frontmatter
  and code blocks. Use `--check` for dry-run.
- [`fix-container-fence.py`](scripts/fix-container-fence.py) — detects fenced
  code blocks whose outer fence uses 4+ backtick markers with content containing
  inner ``` fences (markdown-syntax examples). Adds a `text` language tag to
  the opening fence to satisfy MD040 without breaking the inner fences. Use
  `--check` for dry-run.

All seven scripts operate in-place on a list of file arguments.

```bash
python3 scripts/fix-table-separators.py --check path/to/file.md
python3 scripts/fix-table-separators.py path/to/file.md

python3 scripts/wrap-long-lines.py --max 120 --check path/to/file.md
python3 scripts/wrap-long-lines.py --max 120 path/to/file.md

python3 scripts/fix-fenced-code-language.py --check path/to/file.md
python3 scripts/fix-fenced-code-language.py path/to/file.md

python3 scripts/fix-emphasis-as-heading.py --check path/to/file.md
python3 scripts/fix-emphasis-as-heading.py path/to/file.md

python3 scripts/fix-list-style.py --check path/to/file.md
python3 scripts/fix-list-style.py path/to/file.md

python3 scripts/fix-heading-spacing.py --check path/to/file.md
python3 scripts/fix-heading-spacing.py path/to/file.md

python3 scripts/fix-container-fence.py --check path/to/file.md
python3 scripts/fix-container-fence.py path/to/file.md
```

These are convenience tools for the `## 2. Verification Workflow` step 3
(auto-fix) — they target patterns `markdownlint-cli2 --fix` does not resolve.

### 3.1 Execution Order

When running multiple fix scripts, the following order is **REQUIRED** to avoid
re-introducing lint errors:

1. `fix-table-separators.py`
2. `fix-fenced-code-language.py` (MUST run BEFORE `wrap-long-lines.py` — fence
   lines may exceed the width limit and wrapping a fence line before its
   language tag has been added produces a broken fence)
3. `fix-container-fence.py`
4. `wrap-long-lines.py`
5. `fix-emphasis-as-heading.py`
6. `fix-list-style.py`
7. `fix-heading-spacing.py`

> **Indent drift after editing / lint-fix.** After running the §3.1 pipeline,
> verify that continuation-line indent in edited regions matches the original
> file's siblings. `markdownlint-cli2 --fix` and companion scripts can leave
> whitespace drift on adjacent lines. If drift is found, repair it with a
> targeted `pathlib` edit and re-run the `markdownlint-cli2` audit before
> staging. The canonical protocol is in
> [`git-atomic-commit-construction §3g`](../../git-atomic-commit-construction/SKILL.md#3g).

### 3.2 Known `markdownlint-cli2 --fix` Caveats

**`markdownlint-cli2 --fix` corrupts bare closing fences.** When it encounters
a fenced code block without a language tag (\`\`\`), the built-in `MD040` fix
attaches a `text` language tag to **every** \`\`\` line — including the
closing fence — producing a broken construct:

````text
```text
code here
```text
````

**Resolution:** Do NOT use `markdownlint-cli2 --fix` for MD040. Instead, run
`fix-fenced-code-language.py` which correctly tracks open/close fence state
and strips any language tag from closing fences. If `--fix` has already been
applied, `fix-fenced-code-language.py` will repair the damage.

***

## 4. Related Rules

- **SSOT**: [markdown-generation-rules.md](../../../ai-agent-rules/markdown-generation-rules.md)
- **Formatting Protocol**: [ai-rule-standardization-rules.md](../../../ai-agent-rules/ai-rule-standardization-rules.md)

***

## 5. CI Integration

### 5.1 Pipeline Script Execution Order

When automating lint fixing in a CI pipeline or pre-commit hook, run the
companion scripts in the order defined in §3.1. The pipeline MUST NOT use
`markdownlint-cli2 --fix` for MD040 (use `fix-fenced-code-language.py`
instead) per the caveat in §3.2.

Recommended one-shot invocation from the repo root:

```bash
python3 .agents/skills/markdown-generation/scripts/fix-table-separators.py \
  --check file.md
python3 .agents/skills/markdown-generation/scripts/fix-fenced-code-language.py \
  --check file.md
python3 .agents/skills/markdown-generation/scripts/wrap-long-lines.py \
  --max 120 --check file.md
python3 .agents/skills/markdown-generation/scripts/fix-emphasis-as-heading.py \
  --check file.md
python3 .agents/skills/markdown-generation/scripts/fix-list-style.py \
  --check file.md
python3 .agents/skills/markdown-generation/scripts/fix-heading-spacing.py \
  --check file.md
```

Drop `--check` to apply changes in-place.

### 5.2 YAML Frontmatter Validation

YAML frontmatter `description` values that contain colons followed by
YAML-reserved tokens (e.g., `resetMocks: true`) cause downstream parsers
(VS Code preview, `markdownlint-cli2`) to misinterpret the colon as a new
YAML key opening.

**Rule:** If a `description` value contains any colon (`:`) that is not
trailing whitespace or a URL scheme (`https://`), wrap the entire value in
double quotes (`"..."`). Bare unquoted descriptions containing internal
colons are FORBIDDEN.

**Correct:**

```yaml
---
description: "Repository-specific composer that uses the generic ai-suite skill for debugging missing toolbar features"
---
```

**Incorrect:**

```yaml
---
description: Repository-specific composer that uses the generic ai-suite skill for debugging missing toolbar features
---
```

The difference is invisible in most Markdown renderers but causes silent
YAML parse failures in editor preview panes and schema validators.

### 5.3 Lint Gate

Every skill authored via the Skill Factory (`skill-factory`) MUST pass the
full Verification Workflow (§2) including the companion-script pipeline
(§3.1) before it is considered complete. The factory's Post-Drafting
Checklist (§3) is the SSOT for the gating criteria; this section is the
SSOT for the technical execution order.
