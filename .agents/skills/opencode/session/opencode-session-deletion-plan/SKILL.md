---
name: opencode-session-deletion-plan
description: Composer — produce a versioned session-deletion implementation plan that embeds content-survival markers, the commit roster, the mandatory gap-closure gate, and the execution phases the deletion composer runs from another session.
category: OpenCode
version: 1.0.0
---

# opencode-session-deletion-plan (v1)

> **Name:** opencode-session-deletion-plan<br>
> **Description:** Composer — author the versioned plan that
> `opencode-session-deletion` executes, with embedded content markers,
> commit roster, gap-closure gate, and verification phases.<br>
> **Category:** OpenCode

## Description

Author the session-deletion plan itself. The plan is a versioned
`implementation-plan` under `docs/` that another session can execute after
the authoring session is gone. It carries everything the executor cannot
re-derive: the target artifact inventory, the content-survival markers for
the authoring session's work, the commit roster, the mandatory gap-closure
gate, the TUI-closure check, the recreation guard, and the plan's own
retirement step.

This skill does NOT delete anything. It produces the plan;
[`opencode-session-deletion`](../opencode-session-deletion/SKILL.md)
executes it.

## Composition Rationale

This skill is a **composer**. It sequences existing capabilities instead of
re-implementing them:

1. [`opencode-session-deletion`](../opencode-session-deletion/SKILL.md) —
   invoked FIRST through its `scripts/delete-session.py <id> --dry-run`
   inventory; the rendered plan embeds that inventory.
2. [`planning-artifact-naming`](../../../general/planning/planning-artifact-naming/SKILL.md) —
   owns the `<date>_<session-id>_<slug>_implementation-plan_v<N>.md` filename
   contract the generator follows.
3. [`planning-artifact-lifecycle`](../../../general/planning/planning-artifact-lifecycle/SKILL.md) —
   owns the plan-first gate and the retirement-last rule.
4. [`markdown-lint-workflow`](../../../general/markdown-lint-workflow/SKILL.md) —
   owns the lint gate for the rendered plan.
5. `scripts/build-deletion-plan.py` + `scripts/plan.template` — the
   deterministic tier: JSON spec in, markdown plan out.

The composer's value-add is the marker-extraction judgement and the
plan structure that survives session deletion. Inlining the renderer into
prose would make the plan non-deterministic and untestable.

**Recovery source.** An already-retired plan may be read back from the OS
Trash by exact filename, and related authoring-session logs may be reused
from the Trash destination used by
[`opencode-session-log-cleanup`](../../opencode-session-log-cleanup/SKILL.md)
when the session record itself is gone.

## Environment & Dependencies

| Requirement | Version | Notes |
| --- | --- | --- |
| Python | 3.12+ | Stdlib only — no pip dependencies |
| `opencode-session-deletion` skill | — | At `../opencode-session-deletion/` for the dry-run inventory |
| `planning-artifact-naming` / `planning-artifact-lifecycle` skills | — | Filename and lifecycle contracts |
| `markdownlint-cli2` | any | Lint gate for the rendered plan |

## CLI Contract

`scripts/build-deletion-plan.py`:

| Argument | Required | Description |
| --- | --- | --- |
| `--spec PATH` | Yes | JSON spec with target, inventory, markers, roster, gate |
| `--output PATH` | No | Output plan path (default: `<docs-dir>/<date>_<session-id>_<slug>_implementation-plan_v<N>.md`) |
| `--docs-dir DIR` | No | Docs directory for the default name (default: `docs`) |
| `--version N` | No | Plan version (default: `1`) |
| `--overwrite` | No | Replace an existing output file |
| `--dry-run` | No | Validate and render without writing |
| `--json` | No | Machine-readable summary |

Exit codes: `0` OK, `1` spec validation failed, `2` usage/IO/template error,
`3` output exists without `--overwrite`.

### Spec contract

```json
{
  "date": "YYYY-MM-DD",
  "session_id": "ses_<target>",
  "session_slug": "session-deletion",
  "authoring_session_id": "ses_<author>",
  "target_title": "<title or omit>",
  "inventory": {
    "database": true,
    "logs": ["<absolute path>"],
    "scratch": ["<absolute path>"],
    "docs": ["<absolute path>"]
  },
  "markers": [
    {
      "path": "<absolute path>",
      "pattern": "<literal marker>",
      "match_mode": "case_insensitive"
    }
  ],
  "markers_none": false,
  "commit_roster": [{"sha": "<full sha>", "subject": "<subject>"}],
  "gap_closure": {
    "pass": 6,
    "verdict": "zero open gaps",
    "register_path": "<absolute path or null>"
  }
}
```

`markers` and `markers_none: true` are mutually exclusive; one of them is
mandatory. A missing marker baseline is a spec error, never silently
rendered.

## Protocol

1. Confirm the target session ID and the authoring session ID. Never guess
   either.
2. Run the deletion composer's dry-run and keep its inventory:

   ```bash
   python3 .agents/skills/opencode/session/opencode-session-deletion/scripts/delete-session.py <id> --dry-run --json
   ```

3. Extract one marker per protected file from the authoring session's
   commits and touched files. Each marker needs an absolute path, a literal
   pattern, and `match_mode` (`case_insensitive` by default; `exact` only
   when casing is the invariant). If there is no protected work, set
   `markers_none: true` explicitly.
4. Record the authoring session's commit roster (full SHA + subject).
5. Record the latest gap-closure pass and its verdict, or point at the
   register that must be validated before deletion.
6. Write the JSON spec and render the plan:

   ```bash
   python3 .agents/skills/opencode/session/opencode-session-deletion-plan/scripts/build-deletion-plan.py --spec <spec.json>
   ```

7. Lint the rendered plan:

   ```bash
   markdownlint-cli2 <plan.md>
   ```

8. Present the plan and STOP for approval. Execution belongs to
   `opencode-session-deletion`, from a different session, with the target
   TUI closed.

## Edge Cases

- **Plan already retired**: recover it from the OS Trash by exact filename;
  do not re-author markers from memory.
- **Authoring session logs deleted**: reuse any related logs or plan copy in
  the Trash; if neither exists, the marker baseline is unavailable — set
  `markers_none` only if the authoring session truly had no protected work,
  otherwise STOP.
- **No protected work**: `markers_none: true` is valid and renders an
  explicit "Markers: none" section.
- **Inventory drift**: the executor must compare its fresh dry-run with the
  plan's inventory and report differences; new files are never swept in.
- **Multiple docs artifacts**: every absolute path is listed; the plan file
  itself is retired last.
- **Existing plan file**: the generator refuses to overwrite without
  `--overwrite`; increment `--version` instead.

## Related Skills

- [`opencode-session-analysis-bundle`](../opencode-session-analysis-bundle/SKILL.md) —
  produces the transcript evidence used to choose markers.
- [`skill-library-gap-closure`](../../../general/skill-dev/skill-library-gap-closure/SKILL.md) —
  the mandatory gate the rendered plan embeds.

## Traceability

See [TRACEABILITY.md](TRACEABILITY.md).

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
