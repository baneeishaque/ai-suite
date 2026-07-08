# Jira Work Item Hierarchy Report

Companion skill for generating markdown hierarchy reports from Jira JQL queries — builds a parent-child tree with clickable links, type summaries, and testing subtask classification.

## Quick Reference

- **Skill SSOT:** [SKILL.md](./SKILL.md)
- **Script:** `scripts/jira-hierarchy-report.py`

## When to Apply

Use this skill when:
- Given a JQL query and asked to map the work item hierarchy
- Auditing the scope and status of items under an epic
- Producing a report that distinguishes dev subtasks from testing/QA work
- Documenting work item structure for sprint planning or status reporting

## Key Standards

- Always classify subtasks: "test" or "qa" in summary → testing (not dev responsibility); all others → dev subtasks
- All ticket keys must be clickable links in the report
- Sort everything by ticket key ascending
- Output markdown with `<pre>` hierarchy tree and per-type detail tables
