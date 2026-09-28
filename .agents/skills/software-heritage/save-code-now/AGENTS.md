# SWH Save Code Now — Companion Bridge

This file is the bridge for non-skill-aware runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to force an immediate SWH "Save code now" request for a public origin.
- The origin is not yet archived, or you need to refresh a stale snapshot after a push.
- You are on macOS and can use JXA + Chrome (the only workaround for SWH's Anubis PoW protection).

## Operational Procedure

1. Ensure Chrome has a cleared Anubis challenge on `archive.softwareheritage.org/save/` (visit once in-browser if needed).
2. Run: `osascript -l JavaScript .agents/skills/software-heritage/save-code-now/scripts/swh-save.jxa`
3. Capture the JSON output (contains `id`, `snapshot_swhid`, `request_url`) to `ai-session-exports/` for the audit trail.
4. Verify ingest with `swh-ingest-verify` once the save task completes.

## Cross-References

- [`SKILL.md`](SKILL.md) — full protocol, output contract, edge cases.
- [`swh-ingest-verify`](../../software-heritage/ingest-verify/SKILL.md) — per-push verification (checks the snapshot this skill helped create).
