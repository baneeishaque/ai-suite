# `mint-content-links.py.md` — Explainer (Industrial Explainer Pattern 1.4)

## Deep Technical Breakdown

| Logic | Rationale |
|---|---|
| `SCRIPT_DIR` + `../../../general/file/git-blob-hash/scripts/...` base resolution | Per the Layered Composition Mandate: composer resolves base scripts through a path anchored on its own location, so the pipeline works regardless of `cwd`. Inlining base logic is FORBIDDEN (SSOT divergence). |
| `run_base` validates the base script exists before subprocess | A missing base script yields a clear exit-2 error naming the path, instead of a confusing `No such file` traceback deep inside the pipeline. |
| `hash_file` parses `compute-blob-sha1.py --json` | The base emits a JSON array with `sha1`; reusing its JSON contract (not TSV) avoids fragile whitespace parsing and keeps the composer decoupled from the base's display format. |
| `content_ingested` checks stdout starts with `KNOWN` | `check-ingestion.py` prints `KNOWN <hash>` / `UNKNOWN <hash>`; the composer only needs the boolean. Exit 1 (some unknown) is a "wait", not a failure — that's exactly why `--verify` skips the file with a `pending:` notice rather than aborting. |
| `--lines` gate requires `--verify` (or `--force-lines`) | Enforces the procedure rule: a line range is meaningless until SWH serves the blob. `--force-lines` is the explicit operator override. |
| `path=` quote with `safe="/"` | Slashes stay literal (matches procedure examples); other chars percent-encoded. Canonical qualifier order is `origin;path[;lines]`. |

## Common Use Cases

- Mint citable links for cited files after a Save + crawl: `--verify`.
- Add line refs post-confirmation: `--lines 9-15`.
- `--format markdown` for docs; `--format json` for CI parsing (carries `sha1_git` + `ingested`).

## Edge Cases

- Non-file / unreadable → stderr error, exit 1, remaining files processed.
- SWH 403 on verify → `check-ingestion.py` raises a clear Anubis hint; composer surfaces it.
- CRLF vs LF: hash covers raw bytes — different line endings mint a different (correct) id.

## Recommended Enhancements

- Batch `--verify` through `content-ingestion-check --hashes <file>` (one round trip instead of N).
- Add `--anchor rev:<sha>` mode emitting full `origin;visit;anchor;path` links for snapshot-pinned citations.