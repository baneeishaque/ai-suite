# Antigravity App and IDE Cask Guide

## Purpose

Own the independent, source-cited explainer for the Homebrew casks `antigravity` and
`antigravity-ide`, the Google products they install, and the May 2026 product split that changed what
the `antigravity` token means.

## Ownership

- [Root AGENTS.md](../../../AGENTS.md) owns repository-wide operating and documentation rules.
- This folder owns the product comparison, the split timeline, migration guidance, and troubleshooting
  for the two GUI casks.
- Homebrew's cask JSON API and Ruby source own cask facts. Google's product pages and announcement own
  product identity and behavior. This folder records and cross-references those sources; it does not
  override them.
- The CLI cask is owned by [the CLI guide](../antigravity-cli/AGENTS.md); link to it instead of
  duplicating its configuration and usage material.

## Local Contracts

- Documentation only: no scripts, no automation, and no runtime state belong in this folder.
- Record the retrieval date for every external source used in a factual claim.
- Label claims by evidence class: cask source, GitHub record, vendor documentation, inference, or
  locally reproduced.
- Keep `README.md` as the entry point and overview; keep deep tables in their owning topic file.
- `product-history.md` owns the 1.x-to-2.x timeline, the 2026-05-19 announcement, and the 27-hour IDE
  gap.
- `cask-reference.md` owns version encoding, URLs, checksums, artifacts, livecheck, and annotated Ruby
  sources for both GUI casks.
- `installation-and-migration.md` owns install, coexistence, migration, upgrade, pin, and removal.
- `troubleshooting.md` owns failure modes and diagnostic commands.
- `maintainer-discussion.md` owns the PR/issue record, exact quotes, and the maintainer/contributor
  roles.
- `sources.md` owns the source list, retrieval commands, and evidence classification.
- Do not duplicate a full table across files; link to the owning page instead.
- Never include API keys, tokens, account identifiers, or project IDs in examples.
- Use HTTPS for every external link and relative paths for every in-folder link.
- Keep both cask versions consistent everywhere and make every published SHA-256 value match the
  authoritative tables in `cask-reference.md`.
- Preserve the distinction between the App (`Antigravity.app`, `com.google.antigravity`) and the IDE
  (`Antigravity IDE.app`, `com.google.antigravity-ide`). Do not describe them as the same product.
- Preserve the distinction between `agy` (CLI cask), `agy-ide` / `antigravity-ide` (IDE cask), and
  the absence of a binary in the App cask.
- Do not remove the 2026-05-21/22 timeline or the 27-hour gap; they explain the most common user
  complaint.

## Work Guidance

- When either GUI cask changes version, re-read both Ruby sources and update the version, both
  checksums, livecheck details, analytics counts, and recorded tap HEAD together.
- When Google changes product naming or the product split, update `README.md`, `product-history.md`,
  and `cask-reference.md` in the same pass.
- Before changing migration guidance, re-read the pre-split cask history and the current `zap` lists.
  The App's paths overlap the old IDE's paths; the new IDE's paths do not.
- Keep the 1.x `antigravity` IDE identity separate from the current `antigravity` App identity. The
  old token's behavior is historical and must not be presented as current.
- Refresh the vendor pages before making new behavioral claims; the products ship frequently.
- Keep `antigravity-cli` cross-references pointed at the CLI guide rather than copying its content.
- When a claim is an inference from cask paths, say so explicitly. Do not promote an inference to a
  vendor guarantee.

## Verification

- From repository root: `/opt/homebrew/bin/markdownlint-cli2 "docs/guides/antigravity-app-and-ide/*.md"`.
- Inspect fenced code blocks, tables, and relative links after any edit.
- Compare cask facts against the JSON API and Ruby source with the commands in
  [sources.md](sources.md#commands-used).
- If the casks are installed, compare `brew info --cask antigravity` and
  `brew info --cask antigravity-ide` with the app versions and bundle identifiers before asserting
  runtime behavior.
- Verify that every in-folder relative link resolves, including the cross-links to
  `../antigravity-cli/`.

## Child DOX Index

None.
