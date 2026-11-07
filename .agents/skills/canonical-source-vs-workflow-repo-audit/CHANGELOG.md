# Changelog

## 2026-11-06 — Existing-file input support

- Resolve existing file inputs through their containing directory before Git root discovery.
- Reject invalid inputs explicitly and retain nested-repository discovery and existing score weights.
- Add CLI regressions for file/directory parity and invalid paths; document the existing tie-break behavior accurately.
