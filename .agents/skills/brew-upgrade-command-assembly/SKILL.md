---
name: brew-upgrade-command-assembly
description: Generic primitive for assembling Homebrew upgrade/cleanup command chains from package lists, respecting download concurrency, verbose logging, fetch-only handling, and the required brew cleanup --prune=all ordering.
category: Package-Management
---

# Brew Upgrade Command Assembly Skill (v1) — Base Primitive

Atomic, domain-agnostic primitive that assembles a Homebrew upgrade
command chain from provided package lists. The primitive handles the
mechanical assembly of:

- Sequential `upgrade && cleanup` pairs for each package (formula or cask)
- `HOMEBREW_DOWNLOAD_CONCURRENCY=1` environment export
- `--verbose` flag enforcement on every `brew` subcommand
- Fetch-only mode for specified packages (placed after final `--prune=all`)
- Final `brew cleanup --prune=all --verbose` step
- Correct omission of `--cask`/`--formula` on `brew cleanup` (positional only)

The composer layer
owns the brew-specific discovery logic (identifying outdated leaves vs
dependencies, resolving formula vs cask types, applying priority
ordering) and invokes this primitive to produce the final command.

***

## 1. Composition Rationale

This skill is a **base primitive** — it owns ONLY the generic
command-assembly logic. It accepts package lists via CLI flags or stdin
and produces a deterministic, executable Homebrew command chain.

Composers that invoke this skill:

| Composer | Role |
| :--- | :--- |
The primitive was extracted because multiple future workflows (e.g.,
selective cask upgrades, cache-pruning before fetch, dependency-aware
batching) could reuse the same command-assembly logic without
duplicating the brew-outdated-specific discovery code.

**Anti-Duplication**: If another skill needs a brew command chain, it
MUST invoke this primitive rather than re-implementing the assembly
pattern.

***

## 2. CLI Contract (Stable)

Located at [`scripts/assemble-brew-command.py`](./scripts/assemble-brew-command.py).

```bash
python3 assemble-brew-command.py \
  [--formula-names "pkg1,pkg2"] \
  [--cask-names "pkg1,pkg2"] \
  [--fetch-only "pkg1,pkg2"]
```

| Flag | Required | Meaning |
| :--- | :---: | :--- |
| `--formula-names` | ❌ | Comma-separated formula names to upgrade+cleanup |
| `--cask-names` | ❌ | Comma-separated cask names to upgrade+cleanup |
| `--fetch-only` | ❌ | Comma-separated cask names to fetch-only (appended after `--prune=all`) |

At least one of `--formula-names`, `--cask-names`, or `--fetch-only` must be non-empty.

### Output Semantics

- Always starts with `export HOMEBREW_DOWNLOAD_CONCURRENCY=1;`
- Each package gets a `brew upgrade --verbose --cask/--formula <pkg> && brew cleanup --verbose <pkg>` pair
- The chain is terminated by `brew cleanup --prune=all --verbose`
- `brew fetch --cask --verbose <pkg>` entries are appended AFTER the final cleanup
- All segments are joined with ` && ` producing a single logical line
- Trailing newline is always present

### Exit Codes

| Code | Meaning |
| :---: | :--- |
| 0 | Success (command written to stdout) |
| 1 | No packages specified (all lists empty) |

***

## 2a. Stdin Mode (Alternative Input)

If CLI flags are cumbersome (e.g., when the composer passes a long
list), the script also accepts newline-separated package entries via
stdin with type prefixes:

```bash
echo -e "formula:git\ncask:google-chrome\ncask:onedrive" | python3 assemble-brew-command.py --stdin
```

A `fetch:` prefix moves the entry into fetch-only position:

```bash
echo -e "formula:git\nfetch:antigravity" | python3 assemble-brew-command.py --stdin
```

***

## 3. Generated Command Anatomy

The raw string this primitive produces follows this structure (one logical line after `&&` joining):

```text
export HOMEBREW_DOWNLOAD_CONCURRENCY=1; brew upgrade --verbose --formula <f1> && brew cleanup --verbose <f1> && brew upgrade --verbose --cask <c1> && brew cleanup --verbose <c1> && brew cleanup --prune=all --verbose && brew fetch --cask --verbose <fetch1>
```

Key constraints enforced:

1. `brew cleanup` NEVER receives `--cask` or `--formula` flags (positional args only)
2. `brew fetch` always comes AFTER `brew cleanup --prune=all`
3. Every `brew` subcommand includes `--verbose`

***

## 4. Language Choice (Python)

`ai-rule-standardization-rules.md §4` defaults to PowerShell. Python is chosen here because:

1. The skill operates on macOS (Homebrew's primary platform) where
   `python3` is universally available; PowerShell is not pre-installed.
2. Precedent: existing macOS-focused skills in this repository (e.g.,
   `bash-multiline-to-single-line`, `text-block-indent-override`) use
   Python — keeping the same toolchain reduces cognitive switching.
3. The transformation is a simple string join with no external dependencies.

***

## 5. Manual Usage Examples

Assemble a command for a single cask:

```bash
python3 .agents/skills/brew-upgrade-command-assembly/scripts/assemble-brew-command.py \
  --cask-names "google-chrome"
```

Assemble a mixed upgrade with fetch-only:

```bash
python3 .agents/skills/brew-upgrade-command-assembly/scripts/assemble-brew-command.py \
  --formula-names "git,curl" \
  --cask-names "google-chrome,onedrive" \
  --fetch-only "antigravity,fork"
```

***

## 6. Traceability

- **Source**: `ai-agent-rules/brew-rules.md` Section 3 — Sequential Upgrade and Cleanup Workflow
- **Industrialized via**: `rule-to-skill-industrialization` protocol
- **Constraint source**: `brew-rules.md` §3.5 (fetch-after-cleanup
  ordering), §3.6 (export prefix), §1.3 (no --cask/--formula on cleanup)
