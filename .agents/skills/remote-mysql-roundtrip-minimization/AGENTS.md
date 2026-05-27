# Remote MySQL Round-Trip Minimization

> **Skill:** [`remote-mysql-roundtrip-minimization`](SKILL.md)

## Summary

Pack multiple inter-dependent MySQL statements into a single `mysqli::multi_query` call
so a remote DB (PHP-on-Render + MySQL-on-Helio style) incurs ONE network round-trip
instead of N — without losing diagnostic information on failure.

## When the Agent Should Invoke This Skill

- A PHP endpoint issues 2+ statements that share intent (guards + mutation, fan-out reads).
- App and DB are on separate hosts, so RT cost matters.
- User asks to "reduce DB calls" / "pack queries" / "one network round-trip".

## Quick Reference — Target Pattern

```php
$con->multi_query("SELECT counts...; DELETE ... WHERE NOT EXISTS guards;");
$row = $con->store_result()->fetch_assoc();   // counts
$con->next_result();
$affected = $con->affected_rows;              // DELETE outcome
```

## Mandatory Upstream

Before adopting `multi_query`, probe the live server via
[`mysql-capability-probe-pymysql`](../mysql-capability-probe-pymysql/SKILL.md).

## Key Rules

1. Probe first — not every server enables `CLIENT_MULTI_STATEMENTS`.
2. Keep `NOT EXISTS` guards on the mutation (race safety) even with pre-counts.
3. Wrap self-referential subqueries in a derived table (MySQL error 1093).
4. Consume every result set with `next_result()` or the connection desyncs.
5. `multi_query` doesn't support prepared bindings — sanitise inputs separately.
