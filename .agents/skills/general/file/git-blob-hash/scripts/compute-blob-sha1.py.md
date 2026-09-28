# `compute-blob-sha1.py.md` — Explainer (Industrial Explainer Pattern 1.4)

## Deep Technical Breakdown

| Logic | Rationale |
|---|---|
| `compute_blob_sha1(data)` constructs `sha1(b"blob " + len + b"\0" + data)` | This is the git object hash preamble. SWH defines `cnt` ids identically (SWHIDs v1.1 §5.1), so the raw SHA-1 output IS the SWHID content identifier — no git binary, no SWH API round-trip needed for hashing. |
| `iter_files` walks globs with `recursive=True` and falls back to `os.path.isdir` → `os.walk` | `glob.glob("**/*.py")` only recurses with `recursive=True`, but a directory target itself needs `os.walk` to enumerate its contents. Unified iterator keeps the main loop single-pass. |
| `--verify SHA,FILE` mode runs ONLY the assertion | Single-purpose verification is a distinct atomic operation from bulk hashing. Separating it prevents the main loop from emitting partial results alongside a verification report. Exit 1 on mismatch, 2 on bad args. |
| Files read as `"rb"` (raw bytes) | Git stores exactly what is on disk; CRLF files hash to CRLF hashes. `hashlib.sha1` of the raw bytes reproduces `git hash-object` byte-for-byte. Text-mode opens would normalize line endings and produce wrong hashes. |

## Common Use Cases

- Mint SWH content links (`swh-content-link-mint` delegates here).
- Verify a file's blob matches a recorded SWH `cnt` before referencing it.
- Bulk-hash a `docs/` tree for content-addressable storage migration.

## Edge Cases

- **Empty file**: `sha1(b"blob 0\0")` = `e69de29bb2d1d6434b8a4f3e0e7ad23c0d2c5d4c`.
- **Absolute vs relative paths**: `--root` anchors glob resolution and the output path column; positional files are output relative to `--root` regardless of how they were specified.
- **No matches**: exit 2 (not exit 1), because "no files found" is a usage error, not a hash failure.

## Recommended Enhancements

- Accept `--stdin` for hashing piped content (echo "hello" | compute-blob-sha1.py --stdin).
- Add `--algo sha256` option: SWH also indexes `sha256` variants; computing both in one pass via `hashlib` multi-hash would speed batch verification.
