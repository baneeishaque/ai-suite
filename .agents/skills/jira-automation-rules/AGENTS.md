# Jira Automation Rules

Companion skill for designing, building, debugging, and hardening Jira Cloud
native automation rules — no-code automation engine built into Jira.

## Quick Reference

- **Skill SSOT:** [SKILL.md](./SKILL.md)
- **Scripts:** (none — rule configuration is done in the Jira UI)

## When to Apply

Use this skill when:

- Building a Jira automation rule from scratch
- Syncing fields (e.g., Due date) across parent/subtask hierarchies
- Debugging automation audit logs (Some errors, Failed, Conditions not met)
- Replacing the built-in Comment action with a REST API web request to bypass dedupe
- Configuring Send web request with Basic Auth and ADF JSON body
- Diagnosing field-not-on-screen errors that cause silent edit failures
- Understanding which smart values work reliably vs. which are instance-dependent

## Key Standards

- Always add the target field to the Subtask Edit screen before setting it via automation
- Use `{{issue.self.replaceAll("/rest/.*", "")}}` to derive the base URL — never hardcode the domain
- Use Send web request (not Comment on issue) for reliable audit comments — bypasses dedupe
- Use JQL condition after Edit work item to verify the edit took effect (no native fail-on-error)
- Set Delay until response = On and Continue on non-200 = Off for web requests
- Set Allow rule trigger = Off on the rule to prevent loop re-triggering
- Use `{{triggerIssue.duedate}}` and `{{now}}` — avoid `{{now.toEpochSecond}}` and `{{fieldChange.to.jiraDate}}`
