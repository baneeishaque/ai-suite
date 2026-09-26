# ICS Event Generation From JSON — Companion Bridge

## Purpose

This file is the passive bridge for non-skill-aware agent runtimes. The operational SSOT
(CLI contract, spec schema, emission order, verification rules) lives in [`SKILL.md`](SKILL.md).
This bridge only tells you when the skill applies and where to find the procedure.

## When This Skill Applies

Use when you need to **generate an RFC 5545 iCalendar (`.ics`) file from structured event
data**:

- Emitting a maximum-detail `.ics` deliverable from a JSON event spec — UTC form (no
  `VTIMEZONE`) or TZID form (with a `VTIMEZONE` block).
- Any workflow that needs RFC 5545 TEXT escaping, 75-octet UTF-8-safe folding, CRLF endings,
  `VALARM` blocks, and structural self-verification.
- Round-trip work paired with [`ics-event-extraction-to-json`](../ics-event-extraction-to-json/SKILL.md).

Do NOT use this skill to parse `.ics` files, read email, or create calendar events — those
belong to the extraction base and the composer layer.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the spec schema,
CLI contract, exit codes, and the built-in verification rules. Do NOT execute any step
without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [gmail-event-email-to-ics](../gmail-event-email-to-ics/SKILL.md) — composer that normalizes a
  Gmail event email into this skill's spec and invokes `scripts/generate-ics.py`.
- [ics-event-extraction-to-json](../ics-event-extraction-to-json/SKILL.md) — sibling base; the
  inverse parse operation.
- [skill-factory](../../skill-factory/SKILL.md) — layering and script authoring mandates.
