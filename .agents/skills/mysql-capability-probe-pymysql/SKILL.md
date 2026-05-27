---
name: mysql-capability-probe-pymysql
description: Probe a live MySQL server for capability flags such as `CLIENT_MULTI_STATEMENTS` using a tiny Python + PyMySQL script, before adopting the capability in production code. Avoids both Homebrew `mysql` 9.x (which dropped `mysql_native_password`) and a full MariaDB server install.
category: Database
---

# MySQL Capability Probe (PyMySQL) Skill (v1)

> **Skill ID:** `mysql-capability-probe-pymysql`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## 1. When to Apply

Apply this skill whenever production code is about to depend on a MySQL server capability
whose presence is NOT guaranteed across MySQL/MariaDB/managed-host vintages — for example:

- `CLIENT_MULTI_STATEMENTS` (the only capability fully implemented in v1).
- Specific authentication plugin (`mysql_native_password`, `caching_sha2_password`).
- Storage-engine availability (`InnoDB`, `Aria`).
- Server SQL mode flags (`ONLY_FULL_GROUP_BY`, `STRICT_TRANS_TABLES`).
- JSON / window-function / CTE support across legacy hosts.

**Anti-trigger:** Do NOT use for routine `SELECT VERSION()` reads — those go through the
application's normal DB layer.

## 2. Why PyMySQL (not `mysql` CLI, not full MariaDB)

| Option | Verdict | Reason |
| --- | --- | --- |
| Homebrew `mysql` 9.x CLI | ❌ Rejected | MySQL 9.x dropped `mysql_native_password` — cannot connect to legacy managed-host DBs (e.g., Helio, many shared-hosting providers). |
| Full MariaDB server install | ❌ Rejected | Multi-GB, runs a local daemon you don't need; overkill to issue one probe query. |
| `mariadb-connector-c` (Homebrew, headers only) | ❌ Rejected | Provides C library only, no CLI binary. |
| **PyMySQL** | ✅ Adopted | Pure-Python (~100 KB), zero native deps, speaks `mysql_native_password` natively, exposes `client_flag` directly. |

## 3. Required Inputs

- A KEY=VALUE secrets file with at minimum:

    ```text
    DB_HOST=...
    DB_USER=...
    DB_PASSWORD=...
    DB_NAME=...
    DB_PORT=3306   # optional
    ```

  This matches the existing `act.secrets` convention used by Account-Ledger and similar projects.
  If your project uses a different layout (`.env`, JSON), convert via a one-liner first.

- A Python interpreter — sourced from **mise global python** (NEVER the system `/usr/bin/python3`
  on macOS, which is Apple Xcode 3.9 and ignores `mise ls` globals). The shipped runner resolves
  this via the DIRECT install path to avoid the `mise exec` cascade pitfall — see
  [`mise-tool-management` Layer 5](../mise-tool-management/SKILL.md).

## 4. Operational Logic

### 4.1 Inputs and Secrets

If the secrets file is a broken symlink (common in cross-machine workspaces), repair it via
[`dev-env-private-config-symlink`](../dev-env-private-config-symlink/SKILL.md) BEFORE running the
probe — the script gives an opaque `OSError` if it cannot read the file.

### 4.2 One-Shot Probe

```bash
bash .agents/skills/mysql-capability-probe-pymysql/scripts/probe-runner.sh \
    --probe   .agents/skills/mysql-capability-probe-pymysql/scripts/probe-multi-statement.py \
    --secrets /path/to/act.secrets \
    --name    probe-multi
```

The runner:

1. Resolves mise global python at `~/.local/share/mise/installs/python/<latest>/bin/python`
   (direct path — no `mise exec`, no cascading auto-install of Flutter / PHP / etc.).
2. Idempotently installs `pymysql` via that python's `pip --user` if missing.
3. Ensures `<repo-root>/scratch/` exists and is gitignored
   (delegates to [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md)).
4. Runs the probe, redirecting stdout → `scratch/<name>.out`, stderr → `scratch/<name>.err`.
5. Forwards the probe's exit code.

### 4.3 Verdict Schema

Probe scripts MUST emit ONE deterministic verdict line on stdout:

```text
MULTI_STATEMENT_SUPPORTED: True   [((2,),), ((4,),)]
MULTI_STATEMENT_SUPPORTED: False  OperationalError  (1064, 'You have an error...')
```

Exit codes:

- `0` — capability supported.
- `1` — capability not supported (probe ran cleanly, server rejected).
- `2` — configuration error (missing secrets, missing pymysql, no mise python).

### 4.4 Adding a New Capability Probe

1. Copy `probe-multi-statement.py` to `scripts/probe-<capability>.py`.
2. Replace the `cur.execute(...)` block with the capability-specific query.
3. Emit a single verdict line: `<CAPABILITY>: True|False  <evidence>`.
4. Invoke via the same `probe-runner.sh` with `--probe scripts/probe-<capability>.py`.

## 5. Composition

This skill composes with:

- [`mise-tool-management`](../mise-tool-management/SKILL.md) — Layer 5 (Bypass `mise exec`
  Cascade) provides the direct-binary invocation rule used by `probe-runner.sh`.
- [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md) — captures probe
  stdout/stderr to gitignored `scratch/` files.
- [`dev-env-private-config-symlink`](../dev-env-private-config-symlink/SKILL.md) — repairs
  broken secrets-file symlinks before the probe runs.
- [`remote-mysql-roundtrip-minimization`](../remote-mysql-roundtrip-minimization/SKILL.md) —
  the primary CONSUMER of this skill (probes server BEFORE adopting `multi_query`).

## 6. Prohibited Behaviors

- Calling `mise exec -- python ...` from a CWD whose ancestor `mise.toml` chain contains
  unwanted tools (triggers cascading auto-install of Flutter, PHP, etc.).
- Using `/usr/bin/python3` (Apple Xcode 3.9) — `pymysql` may install there but the version
  is unmanaged and not the developer's pinned environment.
- Installing the full MariaDB server just to issue one probe query.
- Hard-coding credentials in the probe script — always use a secrets file argument.
- Probing a production server without read-only-safe queries (`SELECT 1+1` is safe;
  multi-statement DML probes are NOT — keep probes idempotent and side-effect-free).

## 7. Cross-References

- [`remote-mysql-roundtrip-minimization`](../remote-mysql-roundtrip-minimization/SKILL.md)
- [`mise-tool-management`](../mise-tool-management/SKILL.md) §Layer 5
- [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md)
- [`dev-env-private-config-symlink`](../dev-env-private-config-symlink/SKILL.md)
