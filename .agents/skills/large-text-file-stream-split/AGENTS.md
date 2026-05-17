# AGENTS.md — large-text-file-stream-split

This is the companion bridge file for the `large-text-file-stream-split` skill.

For the active operational protocol — **always** consult the SSOT:

→ [`SKILL.md`](./SKILL.md)

## Quick context (passive)

- **Purpose**: Split a > 100 MB text file (build log, SQL dump, CSV, JSONL) into
  N byte-exact, LF-aligned chunks that any editor can open.
- **Artifacts shipped**:
  - [`scripts/split_log.c`](./scripts/split_log.c) — the portable C splitter
  - [`scripts/build_split_log.ps1`](./scripts/build_split_log.ps1) — auto-detects a C compiler and builds the splitter
  - [`scripts/emit_instructions.ps1`](./scripts/emit_instructions.ps1) — renders `INSTRUCTIONS.md` from the template (Phase 4 automation)
  - [`templates/INSTRUCTIONS.md.template`](./templates/INSTRUCTIONS.md.template) — SSOT consumed by `emit_instructions.ps1`
- **Correctness contract**: `cat $(chunks | sort) == source` (byte-for-byte).
  The skill's `§4.5 Phase 5` mandates a SHA-256 round-trip verification.
- **Why C, not PowerShell**: 50–100× speedup on multi-hundred-MB streams; constant
  memory; the per-byte LF scan is awkward in PS. Justified in `SKILL.md` §2.
