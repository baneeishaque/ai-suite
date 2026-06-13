# MRT Configuration Debug — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- An MRT table page has a missing toolbar button or feature
  (density toggle, fullscreen, filters, columns menu, etc.)
- A user reports that an `enable*` config option is not working
- You need to verify an MRT config fix on a running dev server using
  playwright-cli

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full debugging workflow, including
the mapping of MRT features to their controlling `enable*` props, the fix
procedure, playwright-cli verification, and Playwright E2E test verification
patterns. Do NOT execute any step without first loading `SKILL.md`.

## Cross-References

- [`playwright-e2e-spa-auth-navigation`](../playwright-e2e-spa-auth-navigation/SKILL.md)
  — base skill for Playwright E2E fixture setup, login, and navigation
- [`table-persistence-implementation`](../table-persistence-implementation/SKILL.md)
- [`playwright-cli`](https://github.com/microsoft/playwright-cli/tree/main/skills/playwright-cli)
  — browser automation for verifying UI fixes
- [`gitignored-reference-detection`](../gitignored-reference-detection/SKILL.md)
  — documents the gitignored-path → public-URL substitution pattern used for
  playwright-cli
- [`scripts/find-mrt-config-issues.py`](scripts/find-mrt-config-issues.py)
  — automated cross-file enable* prop scanner
- Distribution-unit-specific composer — repo-specific composer with table
  file paths, routes, and test assertions (in the org's internal skill library)
