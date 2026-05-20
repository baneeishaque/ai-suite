---
name: Chat History Analysis Framework
description: Quick-reference framework card for the five-stage copilot-chat-history-analysis protocol.
category: Metrics & Reporting
---

# Chat History Analysis Framework

Quick-reference card for the five-stage protocol defined in
[`../SKILL.md`](../SKILL.md). Use this when you need a compact mental model without
re-reading the full SKILL.md.

***

## The Five Stages at a Glance

```text
Stage 1 → STRUCTURAL DIGEST     What is the shape of the data?
Stage 2 → INTENT RECONSTRUCTION  What was the user actually trying to do?
Stage 3 → AI EXECUTION AUDIT    How well did the AI carry out that process?
Stage 4 → SATISFACTION ASSESSMENT  Was the user satisfied? (signal-based, not opinion)
Stage 5 → SYNTHESIS             Verdict + gap + concrete next step
```

***

## Key Ratios & Thresholds

| Metric | Formula | Threshold |
| :--- | :--- | :--- |
| Message length ratio | `avg(AI chars) / avg(Human chars)` | > 20 = over-verbose; > 100 = essay mode |
| Upsell friction rate | `upsell_turns / total_AI_turns` | > 20% = problematic |
| Session gap | Timestamp gap between consecutive turns | > 4 h = new session |
| Satisfaction polarity | `positive_signals - friction_signals` | < 0 = Unsatisfied |

***

## Intent Reconstruction Formula

```text
"The user was [verb]-ing [object] in order to [goal]."
```

Example: *"The user was **vetting** a personal command-line toolkit in order to **build a
safe-command allowlist** for autonomous AI-agent delegation."*

***

## Satisfaction Signal Pocket Reference

| Type | Quick signals |
| :--- | :--- |
| ✅ Positive | Returned after >1 day · Affirmation turns · No pivot to another tool · Zero corrections |
| ⚠️ Friction | Correction turns · AI misidentified topic · Upsell ignored · Implicit artifact never delivered |

***

## Execution Verdict Decision Tree

```text
All facts correct?
  └─ No  → Functional Failure
  └─ Yes →
        Implicit artifact produced?
          └─ No  → Partial Success (gap)
          └─ Yes →
                Meta-pattern noticed?
                  └─ No  → Partial Success (missed consolidation)
                  └─ Yes → Execution Success
```

***

## Known CSV Schemas

| Schema ID | Key columns |
| :--- | :--- |
| `copilot-chat-v1` | `Conversation, Time, Author, Message` |
| `chatgpt-v1` | `title, create_time, author_role, content` |
| `generic-qa` | Any role + content columns (confirm with user) |

***

## Report Section Order (Mandatory)

1. Structural Digest
2. User Intent
3. AI Execution Audit
4. Satisfaction Assessment
5. Synthesis

Reordering is **BLOCKED** per [SKILL.md §8](../SKILL.md#8-prohibited-behaviors).
