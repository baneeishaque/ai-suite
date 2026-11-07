# Handoff: Live-Repository Protection

## Current Packet

The reviewed two-file proposal was applied on explicit user approval and verified at 2026-11-07T19:26:43+05:30.
Both live files match the saved projected snapshots; pre-existing content, HEADs and indexes were preserved.
The current packet records application details. The older capture below is historical; do not apply its patches again.

Use the [refreshed handoff](current/README.md) for the current four patch layers and recipient instructions.
Its ai-suite baseline was refreshed at 2026-11-07T18:32:40+05:30 after commit
`f39495b083eab515da80e92df2debf8f2060e4d5`. The Repowise preference is now committed, and remaining target changes
are unstaged. The active packet preserves the latest generated metadata and the unchanged proposed policy text;
earlier snapshots and patches remain historical evidence. Use the packet's post-commit patch links.
The capture below is retained as initial evidence, not the current application baseline.
After it was captured, another session inserted a Repowise-generated-metadata preference next to the proposed
replacement. The initial ai-suite patch no longer passed its context check; the refreshed packet preserves that
new preference unchanged. No target-file edit was made during capture; the later approved application is recorded above.

## Status, Ownership and Retention

- Prepared 2026-11-07T16:49:35+05:30. This bundle contains **proposed, unapplied** changes to two root instruction files.
- The user requested HEAD → pre-existing and pre-existing → proposed patch layers, with no target-file edits.
- Both targets were modified but unstaged at capture. Those pre-existing edits remain owned by their existing
  contributors; no receiving-session identity or acknowledgment is inferred.
- Implementation approval and coordination with any active writers are still required. Creating this bundle is
  not applying its proposed changes, creating commits, notifying recipients or completing their work.
- Retain this entire task-named bundle until recipients complete/reconcile the work and the user separately
  authorizes retirement. Producer-session deletion, log cleanup and scratch cleanup must not remove it.
- All evidence files are independent regular files. No session logs or local planning artifacts are needed to use it.

## Requested Outcome

The assistant always starts in ai-suite. Keep the operating policy in its root AGENTS.md and carry its safety
constraints into other repositories. The private configuration repository gets only this factual declaration:

> Repository state: live — running applications use these files, which may change outside the current session.

Missing, stale or ambiguous liveness metadata means unknown, not inactive. Treat unknown repositories as potentially
live/shared; use non-intrusive safety capture and coordinate overlapping edits. Clean Git status, stable mtimes and
failure to detect a writer do not prove exclusive access. Do not use ordinary stash/restore/clean cycles as preparation.
Snapshot capture, content restoration and reference release require distinct authorization and verification.

The ai-suite proposed patch replaces the existing three-line Git-stash preference with the complete central
policy. The private-repository patch adds only one metadata bullet. No change to snapshot scripts, runtime
configuration or Git references is part of these patches.

## Patch Layers and Target Mapping

Each patch uses the repository-relative target `AGENTS.md`. Select the correct repository explicitly:
**the same filename appears in both repositories, so a path match alone is insufficient.**

```text
H (recorded HEAD file) -- head-to-pre-existing.patch --> P (captured live file)
P -- pre-existing-to-proposed.patch --> Q (projected file, never applied to the live target)
```

- H → P is ownership/preservation evidence. P was already present at capture; do not reapply that layer to P.
- P → Q contains only the producing session's requested proposal. Q is a file snapshot, not a commit.
- Both patch layers preserve exact evidence bytes. Their headers target AGENTS.md rather than bundle snapshot names.
- Full patches are linked below; they include all hunks without truncation.

| Target repository / file | HEAD to pre-existing | Pre-existing to proposed |
| --- | --- | --- |
| ai-suite: `AGENTS.md` | [ai-suite-head-to-pre-existing.patch](ai-suite-head-to-pre-existing.patch) | [ai-suite-pre-existing-to-proposed.patch](ai-suite-pre-existing-to-proposed.patch) |
| configurations-private: `AGENTS.md` | [configurations-private-head-to-pre-existing.patch](configurations-private-head-to-pre-existing.patch) | [configurations-private-pre-existing-to-proposed.patch](configurations-private-pre-existing-to-proposed.patch) |

## Captured Repository State

| Repository | Captured HEAD commit | Branch | Target status |
| --- | --- | --- | --- |
| ai-suite | `671c7f5f1e9e70345c013966229eeadf228de3cf` | `personal/main` | Modified, unstaged |
| configurations-private | `7eb66d87ef9ba8810743e84fce52a4d1b427218b` | `stash/changes-on-macOS` | Modified, unstaged |

These are actual HEAD commit IDs captured from the two repositories. No projected commit IDs are invented.
The capture verified each HEAD, target bytes, target mode, status and index listing again after generation.
The live target and index checks passed unchanged over that capture interval. This does not claim other live
files were frozen, nor that the historical stash-related loss has been resolved.

## Independent Snapshot and Patch Evidence

The following Git blob IDs identify file contents, not commits. Snapshot `.txt` files are evidence copies, not
additional active instruction files; embedded relative links inside those raw copies are not relocated or rewritten.
The [manifest](manifest.json) records the same identities, sizes, source modes and capture checks in machine form.

| File | Role | Bytes | Git blob ID |
| --- | --- | --- | --- |
| [ai-suite-head-agents.txt](ai-suite-head-agents.txt) | head | 29231 | `0d7a903cc8188a944d7996a3971278e4a4ecb107` |
| [ai-suite-pre-existing-agents.txt](ai-suite-pre-existing-agents.txt) | pre-existing | 29832 | `8d76abeb88679ddd6d3dc230ea4310f0acf2e02b` |
| [ai-suite-proposed-agents.txt](ai-suite-proposed-agents.txt) | proposed | 32333 | `abf6b6c037ef985b6ffe35c3f77e3cb05687b499` |
| [ai-suite-head-to-pre-existing.patch](ai-suite-head-to-pre-existing.patch) | head-to-pre-existing | 19010 | `cf17caaf3cb800003124ff97db7c9ec83ecec841` |
| [ai-suite-pre-existing-to-proposed.patch](ai-suite-pre-existing-to-proposed.patch) | pre-existing-to-proposed | 4012 | `9f5d366d15548a53580276fb58eca3bec6aaba05` |
| [configurations-private-head-agents.txt](configurations-private-head-agents.txt) | head | 5720 | `507184d906bdef895fc9ac0391c9f2e027630fef` |
| [configurations-private-pre-existing-agents.txt](configurations-private-pre-existing-agents.txt) | pre-existing | 6110 | `81e81583d19df7b18781346a0f271860195a6055` |
| [configurations-private-proposed-agents.txt](configurations-private-proposed-agents.txt) | proposed | 6224 | `3c8e5b8b192271fcfd71b11c29580406dbd1687e` |
| [configurations-private-head-to-pre-existing.patch](configurations-private-head-to-pre-existing.patch) | head-to-pre-existing | 1020 | `10b667deabb6ec120cafc3c51454b4e58f62ed75` |
| [configurations-private-pre-existing-to-proposed.patch](configurations-private-pre-existing-to-proposed.patch) | pre-existing-to-proposed | 475 | `940fa53e4ff8f046fc071d40ec3dc92dd11268f8` |

## Verification Performed

- H → P and P → Q were each replayed against independent copied snapshots, with exact byte and Git-blob equality.
- Replay used a task-owned scratch directory excluded from Git discovery. No real repository index, branch,
  configuration, stash, live AGENTS.md or other working file was used as the replay destination.
- The source target bytes, modes, HEADs and index listings matched their pre-generation observations.
- All bundle evidence was compared using `git hash-object --no-filters`, and all entries are regular files.
- Manifest paths and README links resolve inside this bundle or to public repository content.
- README Markdown lint was checked using the standalone binary from the ai-suite root.

The raw H/P snapshots include existing Markdown structure and formatting; they are preserved as evidence rather
than formatted. The recipient must distinguish pre-existing lint findings from defects introduced by P → Q.

## Recipient Instructions

1. Confirm which checkout is ai-suite and which is the private configuration repository. Read the current root
   contracts and coordinate any overlapping edits before changing either file.
2. Set the appropriate repository root and absolute bundle root. Before each proposed patch, run:

   ```bash
   git -C "$REPO" --no-optional-locks status --short --untracked-files=all -- AGENTS.md
   git -C "$REPO" hash-object --no-filters AGENTS.md
   git -C "$REPO" --no-optional-locks diff --cached --raw -- AGENTS.md
   ```

3. Compare the current raw-file blob with P in the table. A mismatch requires reconciliation with the current
   owners and a refreshed proposal; do not overwrite current work with a saved snapshot. A stable hash is not a lock.
4. Inspect both linked patch layers. Reconcile all current pre-existing changes. A HEAD-to-live diff includes
   other contributors' work; do not attribute or stage the whole diff as this proposal.
5. Only after approval, coordination and identity verification, validate the appropriate unapplied proposal:

   ```bash
   git -C "$REPO" apply --check "$BUNDLE/ai-suite-pre-existing-to-proposed.patch"
   ```

   For the private repository, use its own file:

   ```bash
   git -C "$REPO" apply --check "$BUNDLE/configurations-private-pre-existing-to-proposed.patch"
   ```

6. Apply only the approved proposal with a narrow edit, then verify its complete file identity against Q when
   the starting point was exactly P. If other coordinated changes intervene, use a refreshed proof rather than
   forcing this historical snapshot. Do not use stash/reset/clean to make a patch fit.
7. Lint from the ai-suite root using the standalone `markdownlint-cli2` binary on the exact target. Compare with
   the baseline findings, preserve staged work, and report any drift or failure before proceeding.
8. Acknowledge receipt, then record actual implementation/commit verification only after it occurs. Commit/push
   authorization is separate. The existing recovered safety reference and missing-content recovery are outside scope.

## Precedents Reviewed

This follows the independent-evidence and recipient-owned-retention model demonstrated by:

- [Non-overlapping skill edits](../skill-doc-non-overlapping-edits/README.md), recorded in commit
  `d1614b4c` and corroborated against its originating session records.
- The November 4 OpenCode configuration-consolidation handoff, including its originating request to keep the
  handoff usable after producer-session deletion. Its retention requirements are reproduced above; there is no
  dependency on that uncommitted handoff's files.

Unlike a handoff describing edits already applied, the second patch layer here is strictly projected.
Operational retention does not depend on either precedent surviving: the complete contract is stated above.

## Remaining Work

| Item | State |
| --- | --- |
| Four requested patch layers and independent snapshots | Prepared and replay-verified |
| Source AGENTS.md edits | Not applied |
| Implementation approval and per-file coordination | Pending |
| Direct recipient notification | Pending; prepared for user relay |
| Recipient acknowledgment and completion | Pending |
| Producer commit or push for this work | Not performed |
| Reported historical data-loss recovery | Separate pending objective |
| Handoff retirement | Not authorized |
