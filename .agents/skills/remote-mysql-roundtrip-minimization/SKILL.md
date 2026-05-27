---
name: remote-mysql-roundtrip-minimization
description: Pack multiple inter-dependent MySQL statements (e.g., guard SELECTs + a guarded DELETE) into a single network round-trip via `mysqli::multi_query`, for PHP web servers whose database is hosted on a separate remote host. Includes the four design alternatives (N-roundtrip → optimistic-only → optimistic+fallback → multi_query packed) and the read-protocol for multi-result-set responses.
category: Database
---

# Remote MySQL Round-Trip Minimization Skill (v1)

> **Skill ID:** `remote-mysql-roundtrip-minimization`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## 1. When to Apply

Apply this skill when:

- The PHP web tier and the MySQL database are on **separate hosts** (e.g., app on Render,
  DB on Helio / PlanetScale / managed RDS), so every query incurs real network latency.
- An endpoint issues **≥ 2 statements that share intent** — typically guard SELECTs followed
  by a mutating INSERT/UPDATE/DELETE that depends on the guard outcome, or fan-out reads that
  populate a single response.
- The mutation has **safe race semantics under `NOT EXISTS` guards** (i.e., the mutation
  itself can re-check the precondition atomically).

Do NOT apply when:

- App and DB share a host / Unix socket — round-trip cost is negligible.
- Statements are independent and the caller doesn't care about ordering (use parallel
  connections instead).
- The mutation cannot embed its own precondition (then optimistic+fallback is the ceiling).

## 2. Prerequisite — Server Capability Probe (MANDATORY)

`mysqli::multi_query` requires the server to accept `CLIENT_MULTI_STATEMENTS`. Some managed
hosts disable it. Before adopting this skill, **probe the live target server** via
[`mysql-capability-probe-pymysql`](../mysql-capability-probe-pymysql/SKILL.md):

```bash
bash .agents/skills/mysql-capability-probe-pymysql/scripts/probe-runner.sh \
    --probe   .agents/skills/mysql-capability-probe-pymysql/scripts/probe-multi-statement.py \
    --secrets ~/Lab_Data/configurations-private/<project>/act.secrets
```

Exit 0 = proceed; exit 1 = fall back to design (c) optimistic+fallback (§3.3).

## 3. The Four Design Alternatives

### 3.1 Baseline — N Round-Trips (REJECTED)

```php
$exists  = $con->query("SELECT COUNT(*) FROM accounts WHERE account_id=$id");          // RT 1
$kids    = $con->query("SELECT COUNT(*) FROM accounts WHERE parent_account_id=$id");    // RT 2
$txns    = $con->query("SELECT COUNT(*) FROM transactionsv2 WHERE ...=$id");            // RT 3
if ($kids == 0 && $txns == 0) {
    $con->query("DELETE FROM accounts WHERE account_id=$id");                           // RT 4
}
```

**Verdict:** 4 round-trips for the happy path. Unacceptable when each RT is 50-200 ms.

### 3.2 Optimistic-Only — 1 Round-Trip, but No Diagnostic

```php
$con->query("DELETE FROM accounts a WHERE a.account_id=$id
    AND NOT EXISTS (SELECT 1 FROM (SELECT account_id FROM accounts WHERE parent_account_id=$id) c)
    AND NOT EXISTS (SELECT 1 FROM transactionsv2 WHERE from_account_id=$id OR to_account_id=$id)");
if ($con->affected_rows == 0) {
    // Why? Don't know. Could be: account not found, or had children, or had transactions.
}
```

**Verdict:** 1 RT always, but the failure mode is opaque — caller cannot tell the user
*why* the deletion was rejected. Acceptable only when "rejected" is enough info.

### 3.3 Optimistic + Diagnostic Fallback — 1 RT Happy, 2 RT Sad

```php
$con->query("DELETE ...");           // RT 1
if ($con->affected_rows == 0) {
    $row = $con->query("SELECT counts...")->fetch_assoc();  // RT 2 (only on failure)
    // Build precise error message from $row.
}
```

**Verdict:** Optimal happy-path cost; sad path still incurs 2 RT. Use this when the server
does NOT support multi-statement.

### 3.4 Multi-Query Packed — Always 1 Round-Trip ✅ (TARGET PATTERN)

```php
$sql = "SELECT (SELECT COUNT(*) FROM accounts WHERE account_id='$id') AS account_exists,
               (SELECT COUNT(*) FROM accounts WHERE parent_account_id='$id') AS child_count,
               (SELECT COUNT(*) FROM transactionsv2 WHERE from_account_id='$id'
                                                       OR to_account_id='$id') AS transaction_count;
        DELETE a FROM accounts a WHERE a.account_id='$id'
          AND NOT EXISTS (SELECT 1 FROM (SELECT account_id FROM accounts
                                          WHERE parent_account_id='$id') c)
          AND NOT EXISTS (SELECT 1 FROM transactionsv2 WHERE from_account_id='$id'
                                                          OR to_account_id='$id');";

if (!$con->multi_query($sql)) { /* network/syntax error */ }

$row      = $con->store_result()->fetch_assoc();   // first result set: the counts
$con->next_result();                                // advance to DELETE result set
$affected = $con->affected_rows;                    // rows the DELETE actually removed

if ($affected > 0)                  /* success */
elseif ($row['account_exists']==0)  /* "Account not found" */
else                                /* "Cannot delete: $child_count children, $tx transactions" */
```

**Verdict:** ✅ Always 1 RT, with full diagnostic data captured even on failure.

Canonical reference implementation:
[`examples/delete_account.php`](examples/delete_account.php).

## 4. Read Protocol for Multi-Result-Set Responses

`mysqli::multi_query` returns multiple result sets. The read sequence is strict:

```php
$ok = $con->multi_query($sql);                  // dispatches all statements
if (!$ok) { /* immediate error — typically syntax */ }

// FIRST result set
$result = $con->store_result();                  // null if first statement was a mutation
if ($result) {
    $row = $result->fetch_assoc();              // or fetch_all(MYSQLI_ASSOC) for multi-row
    $result->free();
}

// Advance to subsequent result sets
while ($con->next_result()) {
    $r = $con->store_result();
    if ($r) {
        // SELECT result set
        $r->free();
    } else {
        // Mutation result set — check $con->affected_rows / $con->insert_id IMMEDIATELY
        // before the next next_result() call.
    }
}
```

Key gotchas:

1. `affected_rows` and `insert_id` reflect the **current** result set only — capture them
   into a local variable before advancing.
2. `store_result()` returns `false` (not `null`) on mutation statements — distinguish via
   `mysqli_more_results()` / `mysqli_field_count()` if needed.
3. You MUST consume every result set before issuing the next `multi_query`, or the
   connection enters `Commands out of sync` state.

## 5. Statement-Design Constraints

### 5.1 Derived-Table Wrapper for Self-Referential DELETE

MySQL forbids referencing the DELETE target table directly inside a subquery in the same
statement. Wrap in a derived table:

```sql
-- ❌ MySQL Error 1093 — You can't specify target table 'accounts' for update in FROM clause
DELETE FROM accounts WHERE account_id=? AND NOT EXISTS (
    SELECT 1 FROM accounts WHERE parent_account_id=?
);

-- ✅ Wrap in a derived table to break the self-reference
DELETE FROM accounts WHERE account_id=? AND NOT EXISTS (
    SELECT 1 FROM (SELECT account_id FROM accounts WHERE parent_account_id=?) c
);
```

### 5.2 Race-Safety — Keep Guards on the Mutation Itself

Even with a pre-count SELECT in the same packet, KEEP the `NOT EXISTS` guards on the
DELETE. The SELECT and DELETE are not atomic with each other; a concurrent INSERT of a
child row between them would otherwise orphan the constraint.

### 5.3 Input Sanitisation (Security Caveat)

The reference example uses string interpolation for brevity. **In production, sanitise
or cast inputs** — `mysqli::multi_query` does NOT accept prepared-statement bindings the
way `mysqli::prepare` does. Common defensive patterns:

```php
$id = (int) filter_input(INPUT_POST, 'account_id', FILTER_SANITIZE_NUMBER_INT);
// or
$id = $con->real_escape_string(filter_input(INPUT_POST, 'account_id'));
```

For untyped string fields, consider splitting into a `prepare`-able SELECT and a
`multi_query` mutation if security outweighs the round-trip savings.

## 6. Composition

| Delegated Concern | Skill |
| --- | --- |
| Server capability probe | [`mysql-capability-probe-pymysql`](../mysql-capability-probe-pymysql/SKILL.md) |
| Probe stdout/stderr capture | [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md) |
| Probe python invocation | [`mise-tool-management`](../mise-tool-management/SKILL.md) §Layer 5 |
| Secrets file resolution | [`dev-env-private-config-symlink`](../dev-env-private-config-symlink/SKILL.md) |
| Commit grouping after refactor | [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md) |

## 7. Prohibited Behaviors

- Adopting `multi_query` without first probing the live target server (§2).
- Removing `NOT EXISTS` guards from the mutation "because the SELECT already checked" —
  the two are not transactionally atomic (§5.2).
- Mixing prepared-statement binding placeholders inside a `multi_query` string — they are
  silently ignored, leading to either SQL injection (interpolated values) or empty
  parameter slots.
- Skipping the `next_result()` loop — orphaned result sets corrupt the connection state
  for the next query on the same `$con`.
- Using string interpolation in production without input sanitisation (§5.3).

## 8. Cross-References

- [`mysql-capability-probe-pymysql`](../mysql-capability-probe-pymysql/SKILL.md) — the
  mandatory upstream probe.
- [`examples/delete_account.php`](examples/delete_account.php) — canonical reference
  implementation as actually deployed in Account-Ledger-Server-PHP.
- MySQL Reference Manual — *Multiple Statement Execution* and *mysqli::multi_query*.
