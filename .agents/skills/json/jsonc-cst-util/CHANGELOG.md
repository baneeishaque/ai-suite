# Changelog

## 2026-10-03 — Initial release

- Base primitive established: CST-aware JSONC `read` / `sort` / `format` with
  comment preservation, merge-friendly trailing commas, `auto`/`jsonc`/`strict`
  mode resolution, CRLF preservation, and a 0/1/2/3 exit-code contract.
- Composed by `json-deep-sort` (sort subcommand) and `opencode-jsonc-util`
  (read subcommand).
