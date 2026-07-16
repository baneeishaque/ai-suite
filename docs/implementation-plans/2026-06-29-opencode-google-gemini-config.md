# [Configure and Document Google AI Studio Provider in OpenCode] (v1)

## Rule Compliance Reference

- [Agent Planning Rules](../../ai-suite/ai-agent-rules/ai-agent-planning-rules.md)
- [AI Agent Rule Standardization Rules](../../ai-suite/ai-agent-rules/ai-rule-standardization-rules.md)
- [Skill Factory Skill](../../ai-suite/.agents/skills/skill-factory/SKILL.md)

---

## 1. Original Starting Point & Objectives

The goal of this task is to document the workflow and troubleshooting steps for configuring the Google AI
Studio provider in the OpenCode CLI, with special emphasis on fixing the key-persistence bug across restarts.

### Objectives

- Create a reusable **base skill** (`opencode-provider-persistence-config`) that defines how OpenCode handles
  provider API keys, `auth.json` storage, and config-level registration to ensure key retention.
- Create a **composer skill** (`opencode-google-gemini-config`) that details the Gemini-specific credentials,
  config stanzas, and direct resolution of the key-disappearance issue.
- Register both skills alphabetically in the root `AGENTS.md` skills registry of
  `/Users/dk/lab-data/ai-suite/`.
- Ensure strict compliance with formatting, relative links, and the redaction of all personal information
  (e.g., converting `/Users/dk` to `<user-home>`).

---

## 2. Proposed Changes & File List

### Files to be created

1. **Base Skill `opencode-provider-persistence-config`**:
   - `/Users/dk/lab-data/ai-suite/.agents/skills/opencode-provider-persistence-config/SKILL.md`
   - `/Users/dk/lab-data/ai-suite/.agents/skills/opencode-provider-persistence-config/AGENTS.md`
2. **Composer Skill `opencode-google-gemini-config`**:
   - `/Users/dk/lab-data/ai-suite/.agents/skills/opencode-google-gemini-config/SKILL.md`
   - `/Users/dk/lab-data/ai-suite/.agents/skills/opencode-google-gemini-config/AGENTS.md`

### Files to be modified

1. **Root Registry**:
   - `/Users/dk/lab-data/ai-suite/AGENTS.md`

---

## 3. Step-by-Step Execution Plan

### Phase 1: Context Preparation & Verification

1. Confirm the exact paths and existence of `/Users/dk/lab-data/ai-suite/AGENTS.md`.
2. Inspect directory permissions and structure of
   `/Users/dk/lab-data/ai-suite/.agents/skills/` to ensure correct parent folders are present.

### Phase 2: Implement Base Skill (`opencode-provider-persistence-config`)

1. Create the `.agents/skills/opencode-provider-persistence-config/` directory.
2. Write `SKILL.md` covering the general mechanics of:
   - Storing credentials in `<user-home>/.local/share/opencode/auth.json`.
   - The startup registration process of custom and built-in providers.
   - Why declaring a provider block under `provider` in `opencode.json` is mandatory to auto-load
     credentials on startup.
3. Write `AGENTS.md` companion bridge providing purpose, applicability, and the operational pointer.

### Phase 3: Implement Composer Skill (`opencode-google-gemini-config`)

1. Create the `.agents/skills/opencode-google-gemini-config/` directory.
2. Write `SKILL.md` covering:
   - Connecting Google AI Studio API key.
   - Diagnosing the bug: why restarting OpenCode drops the Gemini connection (the provider fails to
     auto-load unless defined in `opencode.json`).
   - Fixing the bug: the explicit `"google": {}` block in `opencode.json`.
   - Composition Rationale linking back to `opencode-provider-persistence-config`.
3. Write `AGENTS.md` companion bridge providing purpose, applicability, and the operational pointer.

### Phase 4: Bidirectional Cross-Referencing & Registration

1. Insert the bidirectional cross-references in both skills.
2. Add both skills to the root `/Users/dk/lab-data/ai-suite/AGENTS.md` file's skills table in alphabetical order.

### Phase 5: Verification & Linting Check

1. Audit all created files to ensure zero absolute paths exist (all replaced by canonical placeholders like
   `<user-home>` or relative links).
2. Run `markdownlint-cli2` directly to verify all Markdown files are completely clean and conformant.

---

## 4. Verification Plan

### Command-Line Checks

- Verify Markdown linting using the standalone binary on each created `.md` file:

  ```bash
  markdownlint-cli2 "/Users/dk/lab-data/ai-suite/.agents/skills/opencode-provider-persistence-config/SKILL.md"
  markdownlint-cli2 "/Users/dk/lab-data/ai-suite/.agents/skills/opencode-provider-persistence-config/AGENTS.md"
  markdownlint-cli2 "/Users/dk/lab-data/ai-suite/.agents/skills/opencode-google-gemini-config/SKILL.md"
  markdownlint-cli2 "/Users/dk/lab-data/ai-suite/.agents/skills/opencode-google-gemini-config/AGENTS.md"
  ```

- Verify alphabetical order of `AGENTS.md` root file.
