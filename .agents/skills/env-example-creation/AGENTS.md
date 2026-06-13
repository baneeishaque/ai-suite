# Env Example Creation — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes.
The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- A developer needs a `.env.example` but only a real `.env` exists
- You are onboarding a new team member who needs to know which env vars
  are required
- A project is being prepared for open-source or cross-team publication
- You just fetched a `.env` from a staging server and need a clean
  sanitized template

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full procedure — classifying each
env var by sensitivity tier, replacing values with canonical placeholders,
and writing the `.env.example`. Do NOT execute any step without first
loading `SKILL.md`.

## Cross-References

- [`redaction-portability`](../redaction-portability/SKILL.md) — canonical
  placeholder vocabulary and three-tier classification model
