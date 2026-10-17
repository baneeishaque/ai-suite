# Git Remote Branch Lifecycle — Traceability

- Created 2026-10-17.
- Origin: a session that pushed a branch to a remote, then had to rename the remote branch to match the grouping
   scheme that remote already followed, then delete the misnamed remote branch - each step worked out by hand.
- Gap-register evidence: `git branch -m` had zero occurrences across the skill library, so no local-rename
   guardrail existed; the `<local>:<remote>` refspec form was likewise undocumented.
