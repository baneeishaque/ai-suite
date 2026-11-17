# Android Emulator AVD Multiple Instances Research

## Purpose

Maintain the investigation of the Android Emulator error
`Running multiple emulators with the same AVD is an experimental feature. Please use -read-only flag to enable this feature.`,
including the official `-read-only` contract, observed local failure evidence,
maintainer/community responses, prior implementations, and caveats for running
multiple instances of one AVD.

## Ownership

- Parent guidance: [documentation contract](../../../AGENTS.md).
- [README.md](README.md) is the reader entry point.
- Narrative reports own interpretation; reference documents own captured evidence.

## Local Contracts

- Keep conclusions distinct from source quotations, author claims, and locally verified results.
- Keep research self-contained and link to primary public evidence where available.
- Label upstream documentation, installed-build evidence, static tests, inferences, and unresolved behavior explicitly.
- Treat search results as discovery leads; an open PR or author claim is not evidence of an installed fix.
- Write for a beginner: explain terms, concrete consequences, prerequisites, and how to verify behavior.
- Do not use, modify, or launch the commissioned-for-deletion AVD
  `Android_API_36_ARM64_Phone_PlayStore_2`; rely on captured logs and CLI help instead.

## Verification

- Run the repository's standalone Markdown linter on changed Markdown files.
- Confirm that local document links resolve and that quoted sources support the stated conclusions.

## Child DOX Index

No child contracts.
