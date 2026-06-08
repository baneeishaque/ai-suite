# Time Entry Markdown Presentation — Companion Bridge

## Purpose

This companion bridge exposes the `time-entry-markdown-presentation` skill to non-skill-aware agent runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- User provides time entries (start/end times with descriptions) and asks to format them as a markdown table
- User asks to calculate durations from time ranges
- User wants a summary with actual vs targeted time
- Any project or skill needs to present time tracking data in a structured table format

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure, including the JSON input format, script invocation, and summary row configuration. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`work-log-processing`](../work-log-processing/SKILL.md) — upstream skill for rough→formatted TXT transformation
- *(project-specific composer)* — pipes free-form daily log entries into this script; check your organization's internal skill library for this layer if available
- [`skill-factory`](../skill-factory/SKILL.md) — skill generation protocol used to create this skill
