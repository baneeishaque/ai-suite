# Git Remote Ref Reachability Primitives — Traceability

- Created 2026-10-17.
- Origin: a session that asked several questions about remote state - is this commit on
  any remote, does this branch track anything, what is the newest ancestor already in a
  remote, does this remote follow a grouping scheme, does this remote branch exist.
  Each was answered by hand-written `git` invocations with no reusable owner in the
  library.
- Gap-register evidence: the distinguishing tokens `--not --remotes` and
  `branch -r --contains` had zero occurrences across the skill library.
- Split decision D1=C: the naming-convention question was separated into
  `git-remote-branch-convention-discovery`. Merged, this name could not describe both a
  reachability question and a naming question, which the Skill-Name Precision Mandate
  forbids.
