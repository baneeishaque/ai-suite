# AGENTS.md — git-jq-pretty-json-filter

Passive bridge. Active SSOT is [SKILL.md](SKILL.md).

**Composer** — sets up the jq-pretty Git clean+textconv filter and feeds
pre-filter backfill to
[`git-clean-filter-renormalize-backfill`](../git-clean-filter-renormalize-backfill/SKILL.md).

**When to invoke**: any time minified JSON committed to a repository
renders as unreadable single-line diffs on GitHub web or in `git diff`
and pretty diffs are wanted in BOTH places.

**Two scripts**:

- [`scripts/install_jq_pretty_config.py`](scripts/install_jq_pretty_config.py)
  — idempotent install of the filter + diff blocks.
- [`scripts/append_gitattributes_pattern.py`](scripts/append_gitattributes_pattern.py)
  — narrow-pattern appender with wildcard refusal.
