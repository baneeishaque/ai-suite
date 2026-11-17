<!-- title: Bailu input data length and OpenCode workspace/skill context diagnostics -->

# Input Length and Workspace Context

The user reports that Bailu can limit input-data length and that ai-suite's auto-loaded skills may enlarge
OpenCode requests. Treat this as a diagnostic requirement; do not invent a numeric gateway cutoff.

## Controlled Retry

1. Capture the actual OpenCode error/code, reported limit kind, model, prompt/profile, and original context.
2. Retry the same case in a fresh child from a verified blank workspace under `lab-data`.
3. Keep credentials, model/protocol, prompt/marker, required tools, output cap, and state/data roots constant.
4. If global context remains enabled and the length error persists, use child-only documented skill-disabling flags.
5. Keep direct curl/API outcomes independent; a workspace change does not alter the direct payload or result.
6. Interpret a clean-workspace success as context-sensitive compatibility, not proof that full ai-suite context works.

The dedicated blank workspace contains no repo/config/instruction/skill files. Probe logs, auth/state, and the nonce
fixture live outside it. Character/content/body limits are distinct from token context/output limits.

## This Audit's Observation

The controlled client profile disabled external project configuration/skills, used no external plugins,
disabled auxiliary title/summary/compaction requests, and capped diagnostic output.
No input-length error was observed in the completed isolated text/read tests. The conditional blank retry therefore
was not triggered; no claim that folder selection alone cured a length failure is made.

Optional image/audio/video input was not verified by this text/tool audit and is not advertised in its admitted profiles.
The provider's large declared token limits were source-validated, not stress-tested by million-token prompts.

See the [client CSV](evidence/opencode-probe-results.csv) and [retry summary](evidence/input-length-retry-summary.json)
for actual per-case context controls, outcomes, and limits of the evidence.
