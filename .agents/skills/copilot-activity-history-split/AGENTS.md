---
name: Copilot Activity History Split
description: Passive context bridge for splitting Copilot activity-history CSV exports into per-conversation CSV files.
category: Data Processing
---

# Copilot Activity History Split (Ref)

This bridge provides passive context for the `copilot-activity-history-split`
skill, which partitions a `copilot-activity-history.csv` export
(`Conversation, Time, Author, Message`) into one CSV per Conversation, sorted by
`Time` ascending with the `Human` row placed before the `AI` row on tied
timestamps, and named with a deterministic slug derived from the Conversation
title.

It should be invoked whenever the user asks to:

- split, partition, or shard a Copilot activity-history CSV;
- archive Copilot conversations as individual files for offline analysis or
  retrieval-augmented generation pipelines;
- normalise the chronological ordering of a chat-history export with a stable
  Human-first tiebreak.

- **Primary Entry Point**: [.agents/skills/copilot-activity-history-split/SKILL.md](./SKILL.md)
