# Git Submodule Misconfiguration Audit & Revert Bridge

## Overview
Passive context for the `git-submodule-misconfiguration-audit-and-revert` skill — orchestrates the discovery, attribution, and reversal of an incorrect `.gitmodules` URL change for a submodule, then hands off dependent-branch updates to the cascade-restack skill.

## Active Instructions
For full operational protocols, refer to [SKILL.md](./SKILL.md).

## Usage Triggers
- A submodule's `origin` URL does not match the expected upstream.
- The submodule is in detached HEAD and its `origin/<default>` is behind HEAD (suggests pointer drift caused by a wrong-fork URL).
- Author wants to revert the `.gitmodules` URL-change commit cleanly and propagate to dependents.
