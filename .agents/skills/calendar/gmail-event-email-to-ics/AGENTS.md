# Gmail Event Email To ICS — Companion Bridge

## Purpose

This file is the passive bridge for non-skill-aware agent runtimes. The operational SSOT
(workflow, account preflight, extraction guidance, duration policy) lives in
[`SKILL.md`](SKILL.md). This bridge only tells you when the skill applies and where to find
the procedure.

## When This Skill Applies

Use when the user asks to **turn a Gmail event-invitation email into a calendar (`.ics`)
file**:

- "make an `.ics` from this webinar invitation"
- "download the invite attached to that email and save it as a calendar file"
- "the event details are only in the email body — build the calendar file"

Do NOT use this skill to create the Google Calendar event itself — continue with
[`ics-to-google-calendar-event`](../ics-to-google-calendar-event/SKILL.md) once the `.ics`
deliverable exists.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full workflow, the body-only extraction guidance table,
the duration policy, and the verification step. Do NOT execute any step without first loading
`SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [ics-event-extraction-to-json](../ics-event-extraction-to-json/SKILL.md) — base primitive that
  parses an attached `invite.ics` into JSON.
- [ics-event-generation-from-json](../ics-event-generation-from-json/SKILL.md) — base primitive
  that emits the verified `.ics` deliverable.
- [google-workspace-mcp-account-switch](../../mcp/google-workspace-mcp-account-switch/SKILL.md)
  — conditional account switch before reading another identity's mail.
- [scratch-artifact-naming](../../general/file/scratch-artifact-naming/SKILL.md) — resolves the
  session-scoped landing stem for downloaded attachment intermediates.
- [ics-to-google-calendar-event](../ics-to-google-calendar-event/SKILL.md) — the second half of
  the chain (event creation).
