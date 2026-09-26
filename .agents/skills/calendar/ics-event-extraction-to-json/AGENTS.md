# ICS Event Extraction To JSON — Companion Bridge

## Purpose

This file is the passive bridge for non-skill-aware agent runtimes. The operational SSOT
(CLI contract, output schema, parsing rules) lives in [`SKILL.md`](SKILL.md). This bridge only
tells you when the skill applies and where to find the procedure.

## When This Skill Applies

Use when you need to **parse an iCalendar (`.ics`) file into structured JSON**:

- Reading an attached `invite.ics` from an event email and normalizing its fields.
- Mapping `.ics` datetimes onto google-workspace MCP `calendar_createEvent` arguments
  (consume `dtstart.iso` / `dtend.iso`).
- Round-trip verification paired with
  [`ics-event-generation-from-json`](../ics-event-generation-from-json/SKILL.md).

Do NOT use this skill to generate `.ics` files, read email, or create calendar events —
those belong to the generation base and the composer layer.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the output schema,
CLI contract, exit codes, and the parsing rules. Do NOT execute any step without first loading
`SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [ics-event-generation-from-json](../ics-event-generation-from-json/SKILL.md) — sibling base;
  the inverse generation operation.
- [gmail-event-email-to-ics](../gmail-event-email-to-ics/SKILL.md) — composer that parses an
  attached `invite.ics` and re-emits a maximum-detail `.ics`.
- [ics-to-google-calendar-event](../ics-to-google-calendar-event/SKILL.md) — composer that maps
  this skill's JSON onto google-workspace MCP calendar arguments.
- [skill-factory](../../skill-factory/SKILL.md) — layering and script authoring mandates.
