# Traceability — docker-resource-cleanup

## Provenance

- Created: 2026-08-10
- Source: "get rid of my docker resources" session
  (`01360e993ffeP65zXAhxHZ38wY`) — the stop-before-remove correction, the volume-
  prune survivor sweep, and the rejected chained-`rm -f && prune` call were
  extracted from the live cleanup replay.
- Layer decision: per [`skill-factory` §2.0](../../skill-factory/SKILL.md) —
  the destructive ordering logic is distinct from the read-only enumeration, so
  base/composer separation is MANDATORY; this composer shells out to the
  `docker-resource-inventory` base rather than re-implementing `docker ps` /
  `docker system df` parsing.

## Session Evidence

Session `01360e993ffeP65zXAhxHZ38wY` (2026-08-10) replayed the full cleanup:
inventory (L1) → scope gate (L2) → rejected `docker rm -f <c> && docker volume
prune -f && docker system prune -a -f` ("stop the running containers first", L3)
→ `docker stop ai_opencode_services_agent` → `docker rm …` → `docker volume
prune -f` reporting `0B` while the dangling volume survived (L5) → `docker
volume rm ai-opencode-sandbox_repo-volume` → final `docker system df` showing
0 images / 0 containers / 0 volumes / 0 build cache (L6).

## The Six Industrial Lessons (L1–L6)

1. **L1 — Inspect before acting.** Inventory precedes any destructive step.
2. **L2 — Human scope gate.** A running container may serve an active tool
   session; scope (full / keep-running / unused) is chosen by the user, not
   inferred.
3. **L3 — Stop-before-remove discipline.** Running containers are stopped (`docker
   stop`) BEFORE removal; destructive docker commands are never chained in one
   shell call.
4. **L4 — Prune never touches running containers.** `docker system prune`
   removes only stopped containers; full cleanup requires explicit stop + rm.
5. **L5 — Volume-prune survivor sweep.** `docker volume prune -f` can report `0B`
   reclaimed while dangling volumes survive; the sweep removes each listed
   volume (in-use refusals are expected and tolerated).
6. **L6 — Final verification.** `docker system df` is re-run and compared against
   the per-scope expected end state.
