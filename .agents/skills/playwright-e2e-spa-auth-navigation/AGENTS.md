# Playwright E2E SPA Authentication & Navigation — Companion Bridge

## Purpose

This file is the companion bridge for the base skill. The operational SSOT
(single source of truth) lives in [`SKILL.md`](SKILL.md). This bridge helps
non-skill-aware agent runtimes discover the skill exists and know to read
`SKILL.md` for the full procedure.

## When This Skill Applies

- You are writing Playwright E2E tests for a React SPA that requires
  authentication.
- Tests fail in headless mode with navigation redirects, sub-menu rendering
  differences, or afterEach cleanup issues.
- The app uses `localStorage`-based auth tokens and protected routes
  (e.g., `PrivateRoutes`).
- The login flow involves filling a form, waiting for a redirect, and
  optionally clicking a card/button to initialize encrypted permissions.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including:

- Auth fixture pattern with per-test isolation
- Login flow and token verification
- Navigation strategy decision (UI click-through vs direct `page.goto`)
- AfterEach isolation rules (avoid `page.goto(baseURL)` inside hooks)
- Headless mode workarounds for sub-menus, reload timing, and debugging
- SPA reload pattern for CompanyVerify-like flows

## Cross-References

- [`mrt-configuration-debug`](../mrt-configuration-debug/SKILL.md) — MRT-specific
  E2E verification patterns built on this base
- [`mrt-component-test-strategy`](../mrt-component-test-strategy/SKILL.md) — Jest+RTL
  unit tests for MRT (complementary layer)
- [`project-structure`](../project-structure/SKILL.md) — Project scaffolding
  conventions
