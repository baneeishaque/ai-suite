---
name: skill-factory
description: Industrial protocol for automated creation of "Skill-First" AI Agent skills with high fidelity.
category: Meta-Automation
---

# Skill Factory Skill (v1)

This skill automates the creation of new AI Agent Skills following the **agentskills.io** protocol and the
**Industrial Fidelity** mandates.

***

## 1. Preparation: The Fidelity Scan

The Agent MUST ensure that no operational detail is lost during the skill creation process.

1. **Source Discovery**: Identify all user-provided operational logic, dependencies, and constraints from the
   conversation history.
2. **Anti-Loss Validation**: Create a list of "Must-Include" technical specifics. **Summarization is BLOCKED** for
   these items.
3. **Preservation Check**: Ensure existing content is preserved and blended. **Destructive overwriting is FORBIDDEN**.
4. **Script Audit**: Search the target skill directory and workspace for existing automation scripts. **Consolidation
   is MANDATORY**—Utility duplication is a failure of the Industrial standard.

- **Greater-Than-Before**: The skill MUST be more detailed than the prompt that initiated it, including
  extrapolated context where necessary.

***

## 2. Skill Generation Protocol

### 2.0 Layering Decision (Base vs. Composer)

Before creating any new skill, the Agent MUST decide whether the requested capability is:

1. **Atomic** — a single, indivisible workflow with no reusable primitive. Proceed to §2.1 as one skill.
2. **Layerable** — contains a generic primitive (glob assembly, metadata extraction, path normalization, brace
   expansion, list sort+dedupe, etc.) that other domain-specific tasks could reuse. Split into:
    - A **base skill** owning ONLY the primitive, with a stdin / file / argument CLI contract and deterministic output.
      The base skill MUST be domain-agnostic.
    - One or more **composer skills** owning the domain-specific discovery, piping their output into the base skill.

The layering test: *"Could a different domain ever need the same primitive?"* If yes, layering is **MANDATORY** —
inlining the primitive into a single skill is a violation of the SSOT contract.

Reference exemplar: [vscode-search-exclude-glob](../vscode-search-exclude-glob/SKILL.md) (base) +
[vscode-search-exclude-submodules](../vscode-search-exclude-submodules/SKILL.md) (composer).

### 2.1 Directory Structure

- Create the target folder in `.agents/skills/<skill-name>/` (hyphens required for names).
- Initialize `SKILL.md` (active SSOT) and `AGENTS.md` (companion bridge).
- For **composer skills**: the composer's script MUST resolve the base script via a relative path anchored to its own
  location (`SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"` then `BASE="$SCRIPT_DIR/../../<base-skill>/scripts/..."`),
  so invocation works regardless of the caller's `cwd`. The composer MUST verify the base script exists and exit
  non-zero with a clear error if it is missing.

### 2.2 SKILL.md Composition

The `SKILL.md` MUST include:

1. **YAML Frontmatter**: name, description, category. Skill names MUST use lowercase letters, numbers, and hyphens.
   The frontmatter block (`---` ... `---`) MUST be the FIRST content in the file (line 1 column 1, no BOM, no
   preceding blank lines, **no preceding HTML comments**); any preceding character makes the agentskills.io lint
   validator emit `Skill must provide a name` even when the YAML is otherwise valid. When a workspace tradition
   uses a namespaced Skill ID containing slashes or underscores (e.g., `dgs_ice/foo_bar`), that form is FORBIDDEN
   in `name:` (validator enforces `^[a-z0-9-]+$`) — put the hyphenated single-segment form in `name:` and keep
   the namespaced form in the body under `> **Skill ID:** ...` where it is not lint-validated.
2. **Environment & Dependencies**: Mandated verification logic (`which`, version checks).
3. **Operational Logic**: The EXACT steps provided by the user (**Zero Omission**).
4. **SSOT Compliance**: The skill MUST NOT duplicate technical standards
   defined in the central rule repository. Instead, it MUST link to the
   authoritative rule files using relative links (e.g., to the atomic
   commit rules or commit message rules).
5. **Traceability Section**: Links to permanent conversation logs. All such logs MUST be sanitised through the
   **[Redaction & Portability Skill](../redaction-portability/SKILL.md)** before being committed — see §3 of this
   document for the mandatory audit checklist.

**No-Parallel-Rule-File Mandate**: When the Factory produces a new skill, it MUST NOT also produce a parallel
rule file (`ai-agent-rules/<topic>-rules.md`) covering the same procedure. Rule / instruction files are
vendor-locked (`.cursor/rules/*.mdc`, `.github/copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`,
`.windsurfrules`, etc.); the `agentskills.io` standard is the open, multi-vendor-portable alternative.
Authoring a sibling rule re-introduces the vendor lock the skill was created to escape and splits the SSOT.
An `AGENTS.md` Permanent Operating Reminder (one-line bullet pointing at the skill) is permitted and
encouraged; a full parallel rule file is FORBIDDEN. Authoritative rationale:
[`ai-rule-standardization-rules.md` §2 Skill-First Architecture](../../../ai-agent-rules/ai-rule-standardization-rules.md)
and [`rule-to-skill-industrialization` §0](../rule-to-skill-industrialization/SKILL.md).

### 2.2.1 Script Authoring Mandates

**No-Embedded-Script Mandate**: Script source code MUST NOT be embedded inside `SKILL.md`, `AGENTS.md`, or any other
markdown document. Markdown MUST link to the separate file under `scripts/` via a **relative** path
(e.g., `[scripts/foo.ps1](scripts/foo.ps1)`) and MAY include a short fenced invocation example (one-liner).
Embedding the full script body is FORBIDDEN — it breaks syntax highlighting, debugging, standalone execution, and
the SSOT contract. See [AI Rule Standardization Rules — No-Embedded-Script Mandate](../../../ai-agent-rules/ai-rule-standardization-rules.md).

**Tier Decomposition Mandate**: Before drafting the `SKILL.md` body, walk every step of the user-provided procedure
and classify each as Tier A (deterministic) or Tier C (judgement) per
[`script-over-instruction-decomposition`](../script-over-instruction-decomposition/SKILL.md). Every Tier-A step MUST
be extracted into a script under `scripts/` and invoked from prose via a one-liner. Prose MUST NOT carry multi-line
bash recipes, Python heredocs, regex-laden `sed`/`awk` chains, or step-by-step file-mutation walkthroughs — those
belong in a script. A skill whose prose still embeds deterministic mechanics has skipped the decomposition step and
fails the Factory's industrial standard.

When the skill ships executable scripts under `scripts/`, every script MUST obey:

1. **Language**: PowerShell (`.ps1`) by default, cross-compatible with Windows PowerShell 5.1+ and PowerShell Core 7+.
   Other languages require an explicit user override or a documented technical justification.
   **Bash Extension Mandate**: When Bash is selected (under user override or documented justification), the script file MUST use the `.bash` extension — never `.sh` — per [Bash Scripting Rules §Naming](../../../ai-agent-rules/bash-scripting-rules.md) and the [GitHub Actions Workflow Rules](../../../ai-agent-rules/github-actions-workflow-rules.md) standalone-script mandate.
   **Tier-Violation Remediation**: When a Factory audit on an EXISTING skill discovers a script that picked the wrong language tier per [`scripting-language-selection-rules`](../../../ai-agent-rules/scripting-language-selection-rules.md) (typically a `.bash` / `.sh` wrapping a `python3 - <<PY` heredoc, or a shell script doing JSON / regex work), DELEGATE the port to [`script-language-tier-port`](../script-language-tier-port/SKILL.md) as its own atomic refactor commit — do NOT inline the port mechanics here.
2. **Documentation Headers**: Comment-based help with `.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER`, `.EXAMPLE`, `.NOTES`
   sections — see the [Script Management Rules](../../../ai-agent-rules/script-management-rules.md).
3. **Execution**: Documented invocations MUST use `pwsh-preview` (preferred) with `pwsh` as fallback.
4. **Common-Utils Dot-Source**: Scripts MUST dot-source `Common-Utils.ps1` from the
   [`powershell-scripts`](../../../ai-agent-rules/powershell-scripts/) submodule of `ai-agent-rules` for shared
   helpers (`Write-Message`, etc.) unless an explicit exemption is justified in the script's `.NOTES` block.
5. **Portable Anchored Paths**: All sibling-artifact lookups (the dot-source above, base-skill scripts under the
   Layered Composition Mandate, config files) MUST be resolved through paths anchored on the script's own location
   via `Split-Path -Parent $MyInvocation.MyCommand.Path` + `Join-Path` — NEVER `$PWD`-relative or hard-coded.
6. **Write-Message Safeguard**: Every `Write-Message` call MUST be guarded with
   `if (-not [string]::IsNullOrWhiteSpace($Message)) { ... }`.
7. **Recursive Submodule Bootstrap**: Any documentation that instructs the user to clone or initialize the
   `powershell-scripts` submodule (or any other submodule) MUST use the recursive form
   (`git submodule update --init --recursive <path>` or `git clone --recurse-submodules <url>`).
8. **Strict Mode Hygiene**: Scripts SHOULD declare `Set-StrictMode -Version Latest` and `$ErrorActionPreference = 'Stop'`.
   When reading `$LASTEXITCODE` after invoking another script, guard with
   `Test-Path Variable:LASTEXITCODE` to avoid strict-mode failures on first invocation.

### 2.2.2 Script Delivery & Preservation Mandates

Scripts are **first-class deliverables** of a skill — not disposable session artifacts:

1. **Ship It (Delivery Mandate)**: Any automation script developed during a skill session MUST be committed inside
   the skill's `scripts/` directory as part of the skill's canonical form. "The script helped during the session"
   is sufficient and mandatory justification to ship it permanently. Leaving scripts uncommitted is a failure of
   the Industrial standard.
2. **Never Silent Drop (Preservation Mandate)**: Existing scripts in a skill's `scripts/` directory MUST NOT be
   deleted, emptied, or replaced without an explicit user instruction. During skill refactors (e.g., extracting a
   base layer), the original script MUST be migrated or superseded explicitly — not silently removed.
3. **Supersession Documentation**: If a script is superseded by a higher-layer composer (3-layer stack refactor),
   the SKILL.md MUST document: (a) which script replaces it, (b) the new invocation path, and (c) the rationale —
   so no operational knowledge is lost even when the old file is intentionally removed.
4. **Commit Inclusion**: The skill's scripts MUST appear in the same commit as the skill's `SKILL.md` — never
   deferred to a follow-up commit. An uncommitted script that exists only in the working tree is NOT part of the
   skill.

### 2.3 Registration

- Update the root `AGENTS.md` skills table to register the new skill with its absolute path and description.
    Use the shared registration helper instead of hand-editing the table:

    ```bash
    python3 .agents/skills/git-atomic-commit-construction/scripts/agents-md-stage-row.py \
        --mode worktree \
        --row "| Skill Name | [\`.agents/skills/<skill-name>/SKILL.md\`](.agents/skills/<skill-name>/SKILL.md) | One-line description |"
    ```

    `--mode worktree` reads the working-tree `AGENTS.md`, inserts the row at the alphabetically correct position,
    and writes the result back to the working tree for normal `git add` review. The default `--mode staged`
    is reserved for the Atomic Commit Construction §2f Interleaving Mandate when `AGENTS.md` already carries
    unrelated pending hunks.
- **Alphabetical Order Mandate**: The root `AGENTS.md` skills table MUST remain sorted alphabetically (case-insensitive)
  by the **Skill** column. New entries MUST be inserted at the correct sorted position \u2014 NEVER appended to the end.
  After insertion, the Agent MUST visually verify that the row above and below the new entry maintain the sort order.
- For layered pairs: register **both** the base and the composer in the same change at their respective sorted
  positions, with the composer's row explicitly noting *"Composer \u2014 feeds X into the base Y skill"* so the dependency
  is visible at the index level.

***

## 3. Post-Drafting Checklist

Every skill generated via the Factory MUST automatically undergo the final verification:

- **Portability, Redaction & PII Audit (MANDATORY — SSOT delegation)**: Every file produced by the Factory MUST be
  put through the full **[Redaction & Portability Skill](../redaction-portability/SKILL.md)** protocol before the
  skill is considered complete. The Factory MUST NOT inline its own redaction rules — the redaction skill is the SSOT.
  Specifically, the Factory MUST execute, in order:
    1. **Tier Classification** (Redaction §1): Walk every string in every generated artifact (`SKILL.md`,
       `AGENTS.md`, every `docs/conversations/*.md`, every `docs/cases/*.md`, every script header) and classify
       each candidate string as Tier A (identity/credentials), Tier B (machine/org topology), or Tier C
       (public/universal).
    2. **Canonical Placeholder Substitution** (Redaction §2): Replace every Tier-A and Tier-B match with the
       canonical placeholder vocabulary (`<workspace-root>`, `<user-home>`, `<toolbase>`, `<author>`, `<user>`,
       `<corp-proxy-host>`, `<corp-domain>`, `<internal-vcs>`, `<ticket-system>`, `<customer>`,
       `<product-codename>`, etc.). Ad-hoc placeholder invention is FORBIDDEN — extend Redaction §2 first.
    3. **Path Handling** (Redaction §3): All absolute Windows / POSIX paths are converted to workspace-relative,
       user-home-relative (`~`), or placeholder form. Angle-bracket placeholders in `[text](target)` link targets
       are converted to inline-code symbolic references per Redaction §3.3 to avoid broken navigation.
    4. **Identity Handling** (Redaction §4): Author trailers, reviewer names, OS usernames, and email addresses are
       redacted. Commit SHAs are preserved.
    5. **Network & Org Handling** (Redaction §5): Internal proxy hosts, internal domains, internal repository URLs,
       ticket IDs, customer names, and product codenames are redacted; the `nonProxyHosts` and analogous wildcards
       use `<corp-domain>` / `<corp-cloud-domain>` placeholders.
    6. **File Naming Hygiene** (Redaction §6): Conversation and case-study filenames MUST encode topics, never
       organization or identity strings.
    7. **Verification Scan** (Redaction §8 Step 4): Re-run the regex inventory scans for absolute paths, emails,
       IPv4, and internal hostnames. The terminal output MUST be empty (or contain only Tier-C universally-true
       matches) before the audit passes.
    8. **Encoding Sanity Check** (Redaction §8 Step 5): Scan for mojibake markers (`Ã`, `â€`, `Â`, `ï¿½`) that
       redaction edits frequently introduce, and fix them before considering the audit complete.
    9. **Directory Depth Audit**: Verify the correct directory depth (e.g., `../../../` from a 3-level deep skill).
   10. **Repository Independence Audit** (Redaction §1.0 + §1.4): When the new skill mentions ANY other repository
       (whether by Markdown link or by prose), run the Pre-Commit Checklist from Redaction §1.4 and apply the
       Standalone-Clone Test from §1.0 — "if I clone ONLY the enclosing repo into a fresh empty directory, does
       every relative link resolve and does every prose reference still make sense?" Reject any relative-path link
       whose target escapes the enclosing repo (count `../` segments) regardless of how it resolves on the author's
       disk. Multi-root VS Code layouts are inadmissible defences. The Worked Example in Redaction §1.5
       (a public-skill ↔ org-private-skill pair) is the reference pattern.
- **Prohibited Behavior**: The Factory MUST NOT publish a skill that has not passed the Redaction & Portability audit.
  Half-redacted strings (e.g., `<corp-proxy-host>.<real-corp>.com`) and over-redacted public identifiers
  (e.g., redacting `Apache Commons`, `Eclipse`, `Maven Central`) are both audit failures per Redaction §10.
- **Contextual Hosting**: Documentation (logs, artifacts) MUST reside in the component's `docs/` folder.
- **Fidelity Check**: Verify that no technical details from the source conversation were summarized or lost.
- **Markdown Audit**: Run the **Markdown Generation** protocol to ensure 100% lint compliance. The agent MUST re-read
  every generated/edited markdown file and fix any stray tool-output tags (`</content>`, `<parameter ...>`), duplicated
  lines, broken or multi-line links, unclosed fences, and embedded absolute paths BEFORE presenting the artifact.
  Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly
  (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is
  **FORBIDDEN** per
  **[Markdown Generation Rules §5](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.
- **Registration Audit**: Confirm the new skill row was inserted into the root `AGENTS.md` skills table at the correct
  alphabetical (case-insensitive) position by the **Skill** column, NOT appended to the end. Spot-check the rows
  immediately above and below to verify the sort order holds.
- **Composition Audit** (when layering applies):
    1. **No Inlining**: Confirm the composer script does NOT reimplement the base primitive — it MUST shell out to
       the base script.
    2. **End-to-End Pipeline Validation**: Execute the composer against a real input and confirm the output matches
       the base skill's expected format (deterministic, sorted, deduped, correctly framed).
    3. **Bidirectional Discoverability**: Confirm the base skill lists the new composer in its
       `## Composition by Higher-Level Skills` table, and the composer links back to the base in its
       `## Composition Rationale` and `## Related Skills` sections.
- **Script Authoring Audit** (when scripts are shipped):
    1. **Cross-Version Smoke Test**: Execute the script with `pwsh-preview` (and, where feasible, `pwsh`) on a real
       input and confirm exit code 0 on the success path and exit code 1 with a `Write-Message`-rendered diagnostic on
       the failure path.
    2. **Pipeline Cleanliness**: Capture the script's stdout into a variable (`$out = & ./script.ps1 ...`) and confirm
       it contains exactly the expected payload — no diagnostic noise leaking onto the success stream.
    3. **Common-Utils Dependency**: Confirm the documented `git submodule update --init --recursive` snippet for the
       `powershell-scripts` submodule appears in the skill's Environment & Dependencies section.
    4. **Path Portability**: Run the script from at least two different working directories (e.g., the repo root and
       `/tmp`) to prove the `$MyInvocation`-anchored relative paths still resolve.
