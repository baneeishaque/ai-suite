# Antigravity CLI Cask Guide

## Purpose

Own the independent, source-cited explainer for the Homebrew cask `antigravity-cli` and the Google
Antigravity CLI it installs.

## Ownership

- [Root AGENTS.md](../../../AGENTS.md) owns repository-wide operating and documentation rules.
- This folder owns cask metadata interpretation, installation and removal procedures, CLI configuration and
  usage notes, and troubleshooting guidance.
- Homebrew's cask JSON API and Ruby source own cask facts. Google's official documentation owns CLI
  behaviour. This folder records and cross-references those sources; it does not override them.

## Local Contracts

- Documentation only: no scripts, no automation, and no runtime state belong in this folder.
- Record the retrieval date for every external source used in a factual claim.
- Label claims by evidence class: cask source, vendor documentation, or locally reproduced.
- Keep `README.md` as the entry point and overview; keep deep tables in their owning topic file.
- `cask-reference.md` owns version encoding, URLs, checksums, artifacts, livecheck, and upgrade semantics.
- `installation.md` owns install, verify, upgrade, pin, and removal procedures.
- `configuration.md` owns settings keys, authentication, permissions, modes, and environment variables.
- `usage.md` owns slash commands, keyboard shortcuts, CLI flags, and headless mode.
- `troubleshooting.md` owns failure modes and diagnostic commands.
- Do not duplicate a full table across files; link to the owning page instead.
- Never include API keys, tokens, account identifiers, or project IDs in examples.
- Use HTTPS for every external link and relative paths for every in-folder link.
- Keep the cask version consistent everywhere and make every published SHA-256 value match the
  authoritative table in `cask-reference.md`.

## Work Guidance

- When the cask version changes, re-read the cask source and update the version, four checksums, livecheck
  details, analytics counts, and recorded tap HEAD together.
- When Google changes a documentation URL, update every referencing page and the source list in
  `README.md`.
- Keep `--print-timeout` documented as a known conflict between Google's CLI reference and headless guide;
  do not silently pick one default.
- Preserve the distinction between the cask install path (`$HOMEBREW_PREFIX/bin/agy`) and the official
  installer path (`~/.local/bin/agy`).
- Refresh vendor documentation before making new behavioural claims; the CLI ships frequently.

## Verification

- From repository root: `/opt/homebrew/bin/markdownlint-cli2 "docs/guides/antigravity-cli/*.md"`.
- Inspect fenced code blocks, tables, and relative links after any edit.
- Compare cask facts against the JSON API and Ruby source with the commands in
  [cask-reference.md](cask-reference.md#verification-commands).
- If `agy` is installed, compare `agy --version` with `brew info --cask antigravity-cli` before asserting
  version behaviour.

## Child DOX Index

None.
