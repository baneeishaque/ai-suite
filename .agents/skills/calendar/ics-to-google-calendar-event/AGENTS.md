# ICS To Google Calendar Event — Companion Bridge

## Purpose

This file is the passive bridge for non-skill-aware agent runtimes. The operational SSOT
(workflow, field mapping, creation/verification sequence) lives in [`SKILL.md`](SKILL.md).
This bridge only tells you when the skill applies and where to find the procedure.

## When This Skill Applies

Use when the user asks to **create a Google Calendar event from an `.ics` file or JSON event
spec**:

- "add this invite to my calendar"
- "create the calendar event for that webinar from the `.ics`"
- "put these event details on my Google Calendar"

Do NOT use this skill when no `.ics` (or spec) exists yet and the source is a Gmail email —
start with [`gmail-event-email-to-ics`](../gmail-event-email-to-ics/SKILL.md) first.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full workflow, the ICS → MCP field mapping table, and the
verification loop. Do NOT execute any step without first loading `SKILL.md` — this bridge is
intentionally non-actionable.

## Cross-References

- [ics-event-extraction-to-json](../ics-event-extraction-to-json/SKILL.md) — base primitive that
  parses the input `.ics` into JSON (`dtstart.iso` / `dtend.iso`).
- [google-workspace-mcp-account-switch](../../mcp/google-workspace-mcp-account-switch/SKILL.md)
  — conditional account switch before creating on another identity's calendar.
- [gmail-event-email-to-ics](../gmail-event-email-to-ics/SKILL.md) — the first half of the chain
  (email → `.ics`).
