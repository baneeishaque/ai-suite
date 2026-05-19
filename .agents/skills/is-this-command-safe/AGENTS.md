# Is This Command Safe Skill

This is an Agent Skill for vetting shell commands **before execution** with a deterministic,
auditable verdict (SAFE / SAFE-IF-PIPED / HAS-DESTRUCTIVE-FLAGS / MUTATES).

Refer to the Single Source of Truth [SKILL.md](./SKILL.md) for the active classification protocol,
destructive-flag inventory, lookup procedure, and the mandated 5-line verdict template.

The curated command allowlist is at [`docs/cheatsheet.md`](./docs/cheatsheet.md) (human-readable)
and [`docs/safety-table.csv`](./docs/safety-table.csv) (machine-readable).
