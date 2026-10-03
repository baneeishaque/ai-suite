# find-current-session.py — Industrial Explainer

> Composer script: discovers current opencode session ID/title from `.opencode/logs/` by sequencing
> `file-glob-sort-by-mtime` + `yaml-field-extract` base skills. Adds repo-root discovery,
> pending-marker-aware selection, parallel header validation, `--since` filter, `--pending-ttl`
> staleness guard, `--state` gate, `--dry-run` mode.

---

## Purpose

Programmatically obtain the active opencode session ID (`ses_XXXXXXXXXXXXX`) and optional title for
traceability workflows (planning artifacts, transcript resolution, CI gates). Designed as a
**composer** — it orchestrates base skills via subprocess, never re-implementing sorting or YAML
parsing.

Selection is **pending-marker-first**: the logger writes an in-flight `NNN-pending-*.yaml` into the
session directory whose turn is currently executing, which is the strongest available "this is the
current session" signal (session IDs change on fork, so a remembered or artifact-derived ID must
never be trusted). Newest-mtime ordering is the fallback.

---

## CLI Contract

```bash
python3 scripts/find-current-session.py [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--log-dir` | path | `$OPENCODE_LOGS_DIR` or `<repo-root>/.opencode/logs` | Override log directory |
| `--repo-root` | path | `$OPENCODE_REPO_ROOT` / `$AI_SUITE_ROOT` / `git rev-parse` / legacy `parents[4]` | Override repo root discovery |
| `--json` | flag | false | Emit single-line JSON instead of human text |
| `--state` | `exists\|missing\|any` | `any` | Gate on `<sid>.state.json` presence; mismatch exits 2 |
| `--since` | ISO timestamp | none | Filter sessions by `st_mtime >= timestamp` (e.g. `2026-09-19T10:00:00`) |
| `--pending-ttl` | int seconds | `3600` | In-flight (`*-pending-*.yaml`) markers older than this are treated as stale (crashed turn); `0` disables |
| `--dry-run` | flag | false | Print discovered paths (repo_root, log_dir, base scripts) as JSON and exit |

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success — session ID found, optional gate passed |
| `1` | Data failure — no logs, missing `session.id`, bad timestamp, base script not found |
| `2` | Policy failure — `--state` gate not satisfied |

### Output Formats

**Human (default):**

```text
Session ID: ses_abc123def456
Title: My session title
State file: exists
Pending marker: yes
```

**JSON (`--json`):**

```json
{
  "session_id": "ses_abc123def456",
  "title": "My session title",
  "state": "exists",
  "pending": true,
  "yaml_path": "/abs/path/.opencode/logs/ses_abc123def456/000-header-1.yaml",
  "log_dir": "/abs/path/.opencode/logs"
}
```

`pending: true` means the winning session dir contains a fresh in-flight turn marker — the strongest
"you are inside this session" signal. `false` means selection fell back to newest-mtime and should
be treated as unverified.

**Dry-run (`--dry-run`):**

```json
{
  "repo_root": "/abs/path",
  "log_dir": "/abs/path/.opencode/logs",
  "sort_by_mtime": "/abs/path/.agents/skills/.../sort-by-mtime.py",
  "extract_field": "/abs/path/.agents/skills/.../extract-field.py",
  "since": "2026-09-19T10:00:00"
}
```

---

## Architecture

### Composition Graph

```text
find-current-session.py (composer)
├── find_repo_root() — env → git → legacy
├── resolve_base_scripts() — primary + per-file fallback
├── pending_marker() — in-flight turn detection per ses_*/ dir (TTL-guarded)
├── Fast path: pending-first + newest-mtime ordering of ses_*/ dirs,
│   parallel probe_session_id() on top-5 (order-preserving selection)
│   └── extract-field.py --key session.id (via ThreadPoolExecutor)
├── Fallback: sort-by-mtime.py --glob *.yaml --limit 1
├── extract-field.py --key session.id (single, if fast path missed)
├── extract-field.py --key title (non-fatal)
├── <sid>.state.json existence check
└── --state gate (exit 2) → output (incl. pending flag)
```

### Base Skills Consumed

| Skill | Script | Role |
|-------|--------|------|
| `file-glob-sort-by-mtime` | `sort-by-mtime.py` | Newest `*.yaml` by mtime (flat fallback) |
| `yaml-field-extract` | `extract-field.py` | Dot-path extraction from YAML header (`session.id`, `title`) |

**Composer discipline:** no `import yaml`, no `rglob` sorting logic inline — always delegate via `run()`.

---

## Deep Technical Breakdown

### Line-by-Line Mapping

| Lines | Component | Pedagogical Rationale |
|-------|-----------|----------------------|
| `1` | `#!/usr/bin/env python3` | Portable shebang; works under mise/venv/system Python (`python-script-generation` §2). |
| `2-7` | Module docstring | Scope statement: composer role, base skills, pending-marker-first selection. |
| `8` | `from __future__ import annotations` | Enables `list[str] \| None`, `tuple[Path,Path]` on 3.10+ without runtime cost. |
| `9-13` | Imports | Stdlib only: `ThreadPoolExecutor` for parallel probe, `datetime` for `--since`, `lru_cache` for repo-root memoization, `time` for the pending TTL. |
| `15` | `SCRIPT_DIR = Path(__file__).resolve().parent` | Anchor for all relative resolution; `resolve()` follows symlinks to real skill location. |
| `17-18` | Env var constants | Single source of truth: `OPENCODE_REPO_ROOT`, `AI_SUITE_ROOT`, `OPENCODE_LOGS_DIR`. |
| `21-48` | `find_repo_root()` | **Three-tier discovery** (env → git → legacy) with `@lru_cache(maxsize=1)`. Cache avoids repeated `git rev-parse` spawns. Docstring warns about env-change staleness. |
| `51-64` | `resolve_base_scripts()` | Primary path under `repo_root/.agents/skills/...` + fallback to `SCRIPT_DIR.parents[3]/.agents/...`. Per-file `is_file()` check: one base can come from primary, other from fallback. |
| `67-78` | `parse_args()` | CLI surface: `--since` (ISO timestamp), `--pending-ttl` (staleness guard for in-flight markers), `--dry-run` (discovery mode), `--state` gate. `argv` param enables test injection. |
| `81-89` | `run()` | Bulkhead: base script runs in subprocess. Returns `(rc, stdout.strip(), stderr.strip())`. Sentinel codes: `127`=binary missing, `124`=timeout. Stderr surfaced for error detail. |
| `92-96` | `probe_session_id()` | Isolated validator: calls `extract-field.py --key session.id`, returns `sid` string or `None`. Used by parallel probe. |
| `99-115` | `pending_marker()` | In-flight turn detection: newest `*-pending-*.yaml` in a session dir, treated as stale when older than `--pending-ttl` (crashed/force-quit orphan guard). Returns the marker path or `None`. |
| `118-127` | `main()` setup | Parse args, resolve root, locate bases, pick log_dir (CLI > env > default). |
| `129-138` | `--dry-run` early exit | Prints discovery info as JSON **before** extractors run. Validates wiring without log files. |
| `140-148` | Preflights | Bases + log_dir existence. Runs after dry-run so dry-run works even if missing. |
| `150-155` | `session_dirs` collection | `iterdir()` + `startswith("ses_")` — one level only, cheap. |
| `157-164` | `--since` filter | `datetime.fromisoformat().timestamp()` → filter `st_mtime >= since_ts`. `ValueError` → exit 1. |
| `166-175` | **Pending ranking** | Per-dir `pending_map`; pending dirs sorted by marker mtime; multi-pending emits a stderr WARNING; final order = pending-first + newest-mtime remainder. |
| `177-195` | **Parallel probe** (key enhancement) | `ThreadPoolExecutor(max_workers=5)` probes top-5 dirs' `000-header-*.yaml[-1]` via order-preserving `executor.map`. Winner = first dir in pending-first/newest-first order whose `sid` parses — finish order never decides. A corrupt newest header deterministically falls back to the next candidate. |
| `197-206` | Flat fallback | `sort-by-mtime.py --limit 1` → JSONL parse. `sort_err` captured for error message. |
| `208-211` | Convergence error | No logs found in either layout → `ERROR` with base stderr detail. |
| `213-220` | `session.id` extraction | Reuses `fast_sid` from parallel probe or calls extractor once. Failure surfaces `extract-field` stderr. Exit 1. |
| `221` | Title extraction | Non-fatal; discards rc/stderr; empty → `None`. |
| `223-234` | Payload assembly | Single dict for both JSON/human output. Includes `pending` (winner had a fresh in-flight marker) and provenance (`yaml_path`, `log_dir`). |
| `236-243` | `--state` gate | `gate_ok = args.state=="any" or (args.state=="exists")==state_exists`. Exit 2 separates policy from data failure. |
| `245-254` | Output | `--json` prints payload; human prints four lines (omits `Title:` if absent, always prints `Pending marker:`). |

---

## Pending-Marker Selection Deep Dive (Lines 150-195)

```python
pending_map = {d: pending_marker(d, args.pending_ttl) for d in session_dirs}
pending_dirs = [d for d in session_dirs if pending_map[d] is not None]
session_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
if pending_dirs:
    pending_dirs.sort(key=lambda d: pending_map[d].stat().st_mtime, reverse=True)
    if len(pending_dirs) > 1:
        print(f"WARNING: multiple sessions have in-flight turns ({names}); ...", file=sys.stderr)
    session_dirs = pending_dirs + [d for d in session_dirs if d not in pending_dirs]
```

| Property | Detail |
|----------|--------|
| **Signal** | An in-flight turn writes `NNN-pending-*.yaml` into the ACTIVE session's dir — stronger than mtime, which an idle sibling can win. |
| **TTL guard** | Markers older than `--pending-ttl` (default 3600s) are stale (crashed/force-quit turn) and ignored. |
| **Multi-pending** | Two genuinely in-flight sessions → stderr WARNING + newest marker wins; callers should treat the result as ambiguous and verify against their own context. |
| **Window** | Only top 5 ordered `ses_*/` dirs probed (`session_dirs[:5]`). |
| **Submission** | Per-dir: lexically-last `000-header-*.yaml` (rotation-safe). |
| **Selection** | `executor.map` preserves submission order; winner = first dir in pending-first, then newest-first order whose `sid` parses. Finish order never decides. |
| **Join** | All top-5 probes complete before selection (each capped by the 30s `run()` timeout). |
| **Failure** | All 5 corrupt/empty → no winner → flat fallback. |

---

## Architectural Decision Matrix

| Decision | Rejected Alternative | Rationale |
|----------|---------------------|-----------|
| Subprocess to base skills | `import sort_by_mtime, yaml` | Composer discipline: base fixes propagate with zero composer edits; process isolation. |
| `@lru_cache` on `find_repo_root` | Manual cache / call every time | 1-line stdlib; `maxsize=1` = zero memory risk. Git spawn dominates runtime. |
| Pending-marker-first selection | Newest-mtime only / remembered-ID pinning | Session IDs change on fork; mtime lets an idle sibling win. The in-flight marker is the strongest liveness signal, with `--pending-ttl` guarding crashed-turn orphans. |
| Multi-pending → warn + newest | Silent pick / hard error | Surfacing ambiguity preserves automation (exit 0) while letting callers treat the result as unverified. |
| `--state` gate with exit 2 | Exit 1 with message | Exit 2 separates *data* failure (1) from *policy* failure (2). Workflows can `\|\| exit 2` specifically. |
| Parallel probe (`ThreadPoolExecutor` + `executor.map`) | Serial loop / `as_completed` finish-order selection / `asyncio` | Stdlib, no event loop; 5 concurrent subprocesses cheap; `executor.map` keeps ordered selection deterministic — finish-order selection let an older session win under load. |
| `--since` ISO timestamp | `--since-days N` / relative | Unambiguous, supports timezone offset, matches common log formats. |
| `--dry-run` prints JSON | Human text | Machine-parseable; CI can `jq .repo_root` to verify wiring. |
| Per-file base-script fallback | All-or-nothing | Monorepo sub-checkouts: one base in primary, other in fallback — both work. |

---

## Common Use Cases

```bash
# Default human output (verified: Pending marker: yes means active session)
python3 scripts/find-current-session.py

# Machine JSON for scripting
python3 scripts/find-current-session.py --json | jq -r .session_id

# CI gate: only proceed if state file exists
python3 scripts/find-current-session.py --state exists --json || exit 2

# Find sessions after deploy
python3 scripts/find-current-session.py --since 2026-09-19T10:00:00 --json

# Debug path resolution (no logs needed)
python3 scripts/find-current-session.py --dry-run --repo-root /abs/path

# Fixture-based test (fixture logs with pending markers)
python3 scripts/find-current-session.py --log-dir tests/fixtures/logs --json | jq -r .pending

# Disable the stale-marker TTL (trust any pending marker)
python3 scripts/find-current-session.py --pending-ttl 0
```

---

## Edge Cases Handled

| Scenario | Behavior |
|----------|----------|
| `$OPENCODE_REPO_ROOT` set but not a dir | Falls to git/legacy (`strip()` + `is_dir()` guard) |
| `git rev-parse` timeout (5s) | Falls to legacy; no hang |
| Newest `ses_*/` has header but `session.id` missing | Skips to next candidate; `probe_session_id` returns `None` |
| Idle sibling dir has newer mtime than the active session | Pending-marker-first ordering wins for the active session |
| Stale pending marker (crashed turn) | Ignored when older than `--pending-ttl` (default 3600s) |
| Two genuinely in-flight sessions | stderr WARNING; newest pending selected; `pending: true` still reported |
| `--since` filters out all dirs | `session_dirs` empty → flat `*.yaml` fallback |
| Parallel probe: extractor hangs on one dir | Bounded by the 30s per-probe timeout; other probes complete; selection then follows ordered candidates |
| Parallel probe: all 5 corrupt | No winner → flat fallback |
| `--dry-run` with missing bases | Still prints paths (preflights skipped), exit 0 |
| `--state exists` but `.state.json` missing | Human: `ERROR: state-file gate not satisfied...` (stderr, exit 2); JSON: prints payload + exit 2 |
| Title missing | Human omits `Title:` line; JSON emits `"title": null` |

---

## Recommended Enhancements

| Enhancement | Tracking |
|-------------|----------|
| `--max-parallel` CLI arg / `OPENCODE_MAX_PARALLEL` env | Tuning for large session counts |
| `--top N` to control candidate window | Currently hardcoded `[:5]` slice |
| `--since` relative formats (`-1h`, `-7d`) | Requires `dateutil` or custom parser |
| Persistent probe cache (`.opencode/.probe_cache.json`) | Avoid re-probing same headers across invocations |
| `--output {json,jsonl,human}` enum | Future multi-session output support |

---

## Related Skills

- [`opencode-current-session-id`](../SKILL.md) — owning composer skill
- [`file-glob-sort-by-mtime`](../../../general/file/file-glob-sort-by-mtime/SKILL.md) — base for flat fallback
- [`yaml-field-extract`](../../../general/yaml-field-extract/SKILL.md) — base for header extraction
- [`code-explanation`](../../../code-explanation/SKILL.md) — documentation standards this file follows
- [`python-script-generation`](../../../python-script-generation/SKILL.md) — script generation standards

---

## Traceability

- **Skill**: `opencode-current-session-id` (composer)
- **Script**: `scripts/find-current-session.py`
- **Session logs**: `.opencode/logs/ses_*/000-header-*.yaml` (created by opencode logger plugin)
- **In-flight markers**: `.opencode/logs/ses_*/*-pending-*.yaml` (written during an executing turn)
- **State sidecar**: `.opencode/logs/<sid>.state.json` (advisory, not authoritative)
