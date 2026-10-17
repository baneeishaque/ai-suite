# Git Remote Branch Convention Discovery — Traceability

- Created 2026-10-17.
- Origin: a session that pushed a branch under a bare worktree-local name, then had to
   rename the remote branch because that remote already followed a `personal/` grouping
   scheme. The convention had to be read off the remote's live heads by hand.
- Gap-register evidence: no skill anywhere owned convention DISCOVERY. Convention
   OWNERSHIP was documented, but only as an axiom that teaches nothing about a remote
   whose scheme is unknown.
- Split decision D1=C: this skill and git-remote-ref-reachability-primitives have separate
   reusability and separate consumers. Merged, the combined name could not describe both a
   reachability question and a naming-convention question, which the Skill-Name Precision
   Mandate forbids. Split, each name is exact and each namespace is free for future use.
