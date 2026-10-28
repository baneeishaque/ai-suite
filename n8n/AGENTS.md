# AGENTS.md — n8n workflows

## Purpose

Version-controlled source for the n8n instance's workflows, kept as
[`@n8n/workflow-sdk`](https://docs.n8n.io/) TypeScript so every change is
reviewable, diffable, and restorable in Git.

## Ownership

- `workflows/` owns one `.ts` file per n8n workflow.
- The n8n instance owns runtime state: credentials, executions, and published
  versions. This repository owns the workflow definitions.

## Local Contracts

- Each workflow file exports `default workflow(<id>, <name>)` and carries a
  header comment with the live n8n workflow ID.
- Git is the source of truth; the n8n canvas is a deploy target. Any change made
  in n8n must be mirrored into the matching file in the same task.
- Never store credentials, tokens, or instance secrets in workflow sources. Use
  `newCredential('<Name>')` and attach credentials in n8n.
- New workflows are drafts until published; publishing is a separate, explicit
  action.

## Work Guidance

- Validate with the n8n MCP `n8n_validate_workflow` tool before saving.
- Create with `n8n_create_workflow_from_code`; update the existing workflow with
  `n8n_update_workflow` instead of creating a duplicate.
- Keep the workflow ID in the header stable so updates target the same workflow.
- Prefer descriptive node names and 2-4 word outcome-focused group titles when a
  workflow grows past seven top-level items.

## Verification

- `n8n_validate_workflow` must pass for every changed workflow file.
- Run `markdownlint-cli2` from the repository root after editing this document.

## Child DOX Index

- None.
