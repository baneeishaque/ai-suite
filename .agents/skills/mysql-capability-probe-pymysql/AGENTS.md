# MySQL Capability Probe (PyMySQL)

> **Skill:** [`mysql-capability-probe-pymysql`](SKILL.md)

## Summary

Probes a live MySQL server for capability flags (e.g., `CLIENT_MULTI_STATEMENTS`)
via a tiny PyMySQL script before adopting the capability in production code.

## When the Agent Should Invoke This Skill

- Before adopting `mysqli::multi_query` or any other capability flag whose presence
  varies across MySQL/MariaDB vintages or managed hosts.
- When the user asks "does my server support X?" for any MySQL feature.

## Quick Reference

```bash
python3 .agents/skills/mysql-capability-probe-pymysql/scripts/probe-runner.py \
    --probe   .agents/skills/mysql-capability-probe-pymysql/scripts/probe-multi-statement.py \
    --secrets ~/Lab_Data/configurations-private/<project>/act.secrets
```

Exit 0 = supported, 1 = not supported, 2 = config error.

## Key Rules

1. PyMySQL only (Homebrew mysql 9.x dropped `mysql_native_password`).
2. Resolve python via direct mise install path; never `mise exec` (cascade pitfall).
3. Stdout/stderr → `scratch/<name>.{out,err}`; never `/tmp`, never `2>/dev/null`.
4. Probes MUST be idempotent and side-effect-free.

## Adding a New Probe

Copy `scripts/probe-multi-statement.py`, replace the test query, emit a single
`<CAPABILITY>: True|False  <evidence>` verdict line on stdout.
