# find-current-session.py — Industrial Explainer

> Composer script: discovers current opencode session ID/title from `.opencode/logs/` by sequencing `file-glob-sort-by-mtime` + `yaml-field-extract` base skills. Adds repo-root discovery, parallel header validation, `--since` filter, `--state` gate, `--dry-run` mode.

---

## Purpose

Programmatically obtain the active opencode session ID (`ses_XXXXXXXXXXXXX`) and optional title for traceability workflows (planning artifacts, transcript resolution, CI gates). Designed as a **composer** — it orchestrates base skills via subprocess, never re-implementing sorting or YAML parsing.

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
| `--dry-run` | flag | false | Print discovered paths (repo_root, log_dir, base scripts) as JSON and exit |

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success — session ID found, optional gate passed |
| `1` | Data failure — no logs, missing `session.id`, bad timestamp, base script not found |
| `2` | Policy failure — `--state` gate not satisfied |

### Output Formats

**Human (default):**
```
Session ID: ses_abc123def456
Title: My session title
State file: exists
```

**JSON (`--json`):**
```json
{
  "session_id": "ses_abc123def456",
  "title": "My session title",
  "state": "exists",
  "yaml_path": "/abs/path/.opencode/logs/ses_abc123def456/000-header-1.yaml",
  "log_dir": "/abs/path/.opencode/logs"
}
```

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

```
find-current-session.py (composer)
├── find_repo_root() — env → git → legacy
├── resolve_base_scripts() — primary + per-file fallback
├── Fast path: parallel probe_session_id() on top-5 ses_*/ dirs
│   └── extract-field.py --key session.id (via ThreadPoolExecutor)
├── Fallback: sort-by-mtime.py --glob *.yaml --limit 1
├── extract-field.py --key session.id (single, if fast path missed)
├── extract-field.py --key title (non-fatal)
├── <sid>.state.json existence check
└── --state gate (exit 2) → output
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
| `2-5` | Module docstring | Scope statement: declares composer role, names base skills. |
| `6` | `from __future__ import annotations` | Enables `list[str] \| None`, `tuple[Path,Path]` on 3.10+ without runtime cost. |
| `7-11` | Imports | Stdlib only: `ThreadPoolExecutor` for parallel probe, `datetime` for `--since`, `lru_cache` for repo-root memoization. |
| `13` | `SCRIPT_DIR = Path(__file__).resolve().parent` | Anchor for all relative resolution; `resolve()` follows symlinks to real skill location. |
| `15-16` | Env var constants | Single source of truth: `OPENCODE_REPO_ROOT`, `AI_SUITE_ROOT`, `OPENCODE_LOGS_DIR`. |
| `19-46` | `find_repo_root()` | **Three-tier discovery** (env → git → legacy) with `@lru_cache(maxsize=1)`. Cache avoids repeated `git rev-parse` spawns. Docstring warns about env-change staleness. |
| `49-62` | `resolve_base_scripts()` | Primary path under `repo_root/.agents/skills/...` + fallback to `SCRIPT_DIR.parents[3]/.agents/...`. Per-file `is_file()` check: one base can come from primary, other from fallback. |
| `65-74` | `parse_args()` | Added `--since` (ISO timestamp), `--dry-run` (discovery mode), `--state` gate. `argv` param enables test injection. |
| `77-85` | `run()` | Bulkhead: base script runs in subprocess. Returns `(rc, stdout.strip(), stderr.strip())`. Sentinel codes: `127`=binary missing, `124`=timeout. Stderr surfaced for error detail. |
| `88-92` | `probe_session_id()` | Isolated validator: calls `extract-field.py --key session.id`, returns `sid` string or `None`. Used by parallel probe. |
| `95-104` | `main()` setup | Parse args, resolve root, locate bases, pick log_dir (CLI > env > default). |
| `106-115` | `--dry-run` early exit | Prints discovery info as JSON **before** extractors run. Validates wiring without log files. |
| `117-125` | Preflights | Bases + log_dir existence. Runs after dry-run so dry-run works even if missing. |
| `130-132` | `session_dirs` collection | `iterdir()` + `startswith("ses_")` + `st_mtime` sort desc. One level only, cheap. |
| `134-141` | `--since` filter | `datetime.fromisoformat().timestamp()` → filter `st_mtime >= since_ts`. `ValueError` → exit 1. |
| `143-163` | **Parallel probe** (key enhancement) | `ThreadPoolExecutor(max_workers=5)` submits `probe_session_id` for top-5 dirs' `000-header-*.yaml[-1]`. `as_completed` yields finish order — first valid `sid` wins. Cancels remaining futures. Prevents corrupt newest header from shadowing healthy older session. |
| `165-174` | Flat fallback | `sort-by-mtime.py --limit 1` → JSONL parse. `sort_err` captured for error message. |
| `176-179` | Convergence error | No logs found in either layout → `ERROR` with base stderr detail. |
| `181-188` | `session.id` extraction | Reuses `fast_sid` from parallel probe or calls extractor once. Failure surfaces `extract-field` stderr. Exit 1. |
| `189` | Title extraction | Non-fatal; discards rc/stderr; empty → `None`. |
| `191-200` | Payload assembly | Single dict for both JSON/human output. Includes provenance (`yaml_path`, `log_dir`). |
| `202-209` | `--state` gate | `gate_ok = args.state=="any" or (args.state=="exists")==state_exists`. Exit 2 separates policy from data failure. |
| `211-219` | Output | `--json` prints payload; human prints three lines (omits `Title:` if absent). |

---

## Parallel Probe Deep Dive (Lines 143-163)

```python
max_parallel = 5
if session_dirs:
    with ThreadPoolExecutor(max_workers=min(max_parallel, len(session_dirs))) as executor:
        future_to_dir = {
            executor.submit(probe_session_id, extract_field,
                           sorted(sdir.glob("000-header-*.yaml"))[-1]): sdir
            for sdir in session_dirs[:max_parallel]
            if sorted(sdir.glob("000-header-*.yaml"))
        }
        for future in as_completed(future_to_dir):
            sdir = future_to_dir[future]
            sid_probe = future.result()
            if sid_probe:
                header_files = sorted(sdir.glob("000-header-*.yaml"))
                yaml_path, fast_sid = header_files[-1], sid_probe
                for f in future_to_dir:
                    f.cancel()
                break
```

| Property | Detail |
|----------|--------|
| **Window** | Only top 5 newest `ses_*/` dirs probed (`session_dirs[:5]`). |
| **Submission** | Per-dir: lexically-last `000-header-*.yaml` (rotation-safe). |
| **Race** | `as_completed` = finish order, not mtime order. First valid `sid` wins. |
| **Cancellation** | `f.cancel()` on remaining futures after winner found. |
| **Failure** | All 5 corrupt/empty → loop ends → flat fallback. |
| **Timeout** | Each `run()` has 30s timeout; hung extractor auto-terminated. |

---

## Architectural Decision Matrix

| Decision | Rejected Alternative | Rationale |
|----------|---------------------|-----------|
| Subprocess to base skills | `import sort_by_mtime, yaml` | Composer discipline: base fixes propagate with zero composer edits; process isolation. |
| `@lru_cache` on `find_repo_root` | Manual cache / call every time | 1-line stdlib; `maxsize=1` = zero memory risk. Git spawn dominates runtime. |
| `--state` gate with exit 2 | Exit 1 with message | Exit 2 separates *data* failure (1) from *policy* failure (2). Workflows can `|| exit 2` specifically. |
| Parallel probe (`ThreadPoolExecutor`) | Serial loop (v2) / `asyncio` | Stdlib, no event loop; 5 concurrent subprocesses cheap. `asyncio` would require async `run()`. |
| `--since` ISO timestamp | `--since-days N` / relative | Unambiguous, supports timezone offset, matches common log formats. |
| `--dry-run` prints JSON | Human text | Machine-parseable; CI can `jq .repo_root` to verify wiring. |
| Per-file base-script fallback | All-or-nothing | Monorepo sub-checkouts: one base in primary, other in fallback — both work. |

---

## Common Use Cases

```bash
# Default human output
python3 scripts/find-current-session.py

# Machine JSON for scripting
python3 scripts/find-current-session.py --json | jq -r .session_id

# CI gate: only proceed if state file exists
python3 scripts/find-current-session.py --state exists --json || exit 2

# Find sessions after deploy
python3 scripts/find-current-session.py --since 2026-09-19T10:00:00 --json

# Debug path resolution (no logs needed)
python3 scripts/find-current-session.py --dry-run --repo-root /abs/path

# Fixture-based test
python3 scripts/find-current-session.py --log-dir tests/fixtures/logs --dry-run
```

---

## Edge Cases Handled

| Scenario | Behavior |
|----------|----------|
| `$OPENCODE_REPO_ROOT` set but not a dir | Falls to git/legacy (`strip()` + `is_dir()` guard) |
| `git rev-parse` timeout (5s) | Falls to legacy; no hang |
| Newest `ses_*/` has header but `session.id` missing | Skips to next-oldest dir; `probe_session_id` returns `None` |
| `--since` filters out all dirs | `session_dirs` empty → flat `*.yaml` fallback |
| Parallel probe: extractor hangs on one dir | Others complete; winner found → `cancel()` on hung future |
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
- [`yaml-field-extract`](../../general/yaml-field-extract/SKILL.md) — base for header extraction
- [`code-explanation`](../../code-explanation/SKILL.md) — documentation standards this file follows
- [`python-script-generation`](../../python-script-generation/SKILL.md) — script generation standards

---

## Traceability

- **Skill**: `opencode-current-session-id` (composer)
- **Script**: `scripts/find-current-session.py`
- **Session logs**: `.opencode/logs/ses_*/000-header-*.yaml` (created by opencode logger plugin)
- **State sidecar**: `.opencode/logs/<sid>.state.json` (advisory, not authoritative)