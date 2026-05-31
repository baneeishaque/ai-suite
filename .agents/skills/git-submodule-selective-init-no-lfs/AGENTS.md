# Git Submodule Selective Init (No-LFS) Bridge

## Overview
Passive context for the `git-submodule-selective-init-no-lfs` skill — initialize **exactly** the submodule paths the user names (no `--recursive`) AND guarantee no LFS objects are fetched during the checkout, via `GIT_LFS_SKIP_SMUDGE=1` plus full `filter.lfs.*` neutralization. The "no-LFS" half of the name is a first-class contract, not a side-effect.

## Active Instructions
For full operational protocols, refer to [SKILL.md](./SKILL.md).

## Usage Triggers
- User asks to init ONE (or a few) specific submodules, not all of them, AND wants LFS smudge skipped.
- User has just used `git-lfs-selective-clone` to clone the superproject LFS-free and now needs per-path init that preserves that LFS-free property.
- Any composer (e.g., `git-submodule-misconfiguration-audit-and-revert`) needs a submodule materialized for inspection without paying the LFS bandwidth cost.
