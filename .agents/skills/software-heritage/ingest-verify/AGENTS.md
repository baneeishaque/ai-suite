# SWH Ingest Verify — Companion Bridge

This file is the bridge for non-skill-aware runtimes. The operational SSOT lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You need to verify that Software Heritage has archived a repository's current HEAD.
- A push has been made and you want to confirm the SWH snapshot contains the new revision.
- You are setting up CI to automatically verify SWH ingest on every push.

## Operational Procedure

1. Run locally: `python3 .agents/skills/software-heritage/ingest-verify/scripts/verify-ingest.py --check <origin>,<rev> --check <origin2>,<rev2>`
2. In CI: the `.github/workflows/swh-verify.yml` workflow calls `resolve-heads.bash` + `run-swh-verify.bash` automatically.
3. If verification returns PENDING, wait for the SWH crawler (hours) and recheck.
4. If FAILED (origin unknown), run `swh-save-code-now` to force an immediate save, then recheck.

## Cross-References

- [`SKILL.md`](SKILL.md) — full protocol, verification logic, exit-code mapping.
- [`swh-save-code-now`](../../software-heritage/save-code-now/SKILL.md) — manual save automation for when verification fails.
