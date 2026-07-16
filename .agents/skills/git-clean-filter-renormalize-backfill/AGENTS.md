# AGENTS.md — git-clean-filter-renormalize-backfill

Passive bridge. Active SSOT is [SKILL.md](SKILL.md).

**When to invoke**: any time a Git clean filter has just been installed
or modified and tracked files predating the filter must be backfilled
through it so stored blobs match the post-filter canonical form.

**Two scripts**:

- [`scripts/renormalize_filtered_files.py`](scripts/renormalize_filtered_files.py)
  — pathspec-driven `git add --renormalize` with mandatory true-byte-drift
  exclusion.
- [`scripts/audit_filtered_blobs.py`](scripts/audit_filtered_blobs.py)
  — verifies post-filter form of every matching stored blob.

**Composers**: [`git-jq-pretty-json-filter`](../git-jq-pretty-json-filter/SKILL.md).
