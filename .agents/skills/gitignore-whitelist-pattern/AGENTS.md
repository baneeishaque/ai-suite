# Gitignore Whitelist Pattern — Companion Bridge

## Purpose

This bridge provides passive context for non-skill-aware agent runtimes that auto-load `AGENTS.md` by filename convention. The operational SSOT lives in [`SKILL.md`](SKILL.md). This file is intentionally non-actionable — read `SKILL.md` before generating any `.gitignore` whitelist block. The skill produces a deny-all + selective negation pattern (`*` + `!*.ext`) for directories where only a narrow set of file types should be tracked and everything else must be ignored.

This is the inverse of a standard `.gitignore` blacklist: instead of listing what to exclude, it lists what to include and blocks everything else. It is the correct pattern when the set of wanted files is small and well-defined while the set of unwanted files is open-ended and unpredictable (e.g., archive directories, binary deliverable folders).

## When This Skill Applies

- A user asks to track only specific file extensions in a directory while ignoring everything else — including extracted folders, temp files, and future additions that do not match the whitelist.
- A directory contains large archives (`.7z`, `.zip`, `.tar.gz`) alongside unpredictable extracted or temporary artifacts that must never be committed.
- A user explicitly says "I only need X files here, nothing else" — the set of wanted files is small and well-defined while the set of unwanted files is open-ended and cannot be enumerated in advance.
- A `.gitignore` block with a deny-all (`*`) plus selective negation patterns (`!*.ext`) is the correct pattern rather than a standard blacklist approach with specific exclusion rules.
- Previously committed files now fall under the whitelist and need to be untracked via `git rm --cached` using the companion `git-post-gitignore-untrack` skill.
- The directory also needs a `.gitattributes` file for Git LFS tracking of whitelisted large binaries, and the `!.gitattributes` negation must be included in the whitelist pattern to make the LFS rules themselves trackable.
- A nested directory structure requires whitelisting at depth, where `!*/` must be added to allow directory traversal and `**/*.ext` patterns must be used for recursive matching.

Do NOT apply this skill when the user wants to ignore specific known files (standard blacklist is simpler), when the set of unwanted files can be enumerated and is predictable, or when the `.gitignore` already correctly uses the deny-all + whitelist pattern.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full operational procedure. The skill proceeds through six steps: identify the target directory, determine the whitelist (always including `.gitignore` and `.gitattributes`), generate the deny-all + whitelist block with strict ordering rules (`*` first, then Git config negations, then extension negations), insert into the existing or new `.gitignore`, verify with `git check-ignore`, and untrack previously committed artifacts via `git rm --cached`. Common recipes for archive-only, archive-plus-docs, multi-extension, and nested-directory scenarios are provided in §5.

**Key verifications:** `git check-ignore -v` confirms whitelisted files are NOT ignored (empty output) and that non-whitelisted files ARE ignored (match shown). `git ls-files --others --ignored --exclude-standard` lists everything the `.gitignore` blocks. Troubleshooting for common issues (whitelisted file still ignored, folder appears in status, `.gitignore` itself untracked) is covered in §7.

Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`gitignore-rules`](../gitignore-rules/SKILL.md) — structural audit for directory-ignore and negation pitfalls in `.gitignore` files; complementary skill that audits blacklist-style patterns while this skill generates whitelist-style patterns
- [`git-post-gitignore-untrack`](../git-post-gitignore-untrack/SKILL.md) — post-processor for untracking previously committed files that are now ignored by the whitelist block; run after applying the deny-all + whitelist pattern if any files were previously tracked
- [`git-lfs-selective-clone`](../git-lfs-selective-clone/SKILL.md) — LFS companion for selective blob retrieval when whitelisted files are large binaries tracked by Git LFS via `.gitattributes` in the same directory
- [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md) — atomic commit discipline for the commit that adds the whitelist `.gitignore` block and untracks previously committed artifacts
- [`gitignored-reference-detection`](../gitignored-reference-detection/SKILL.md) — detection of untracked files that are ignored but should not be; run after applying the whitelist to verify no files fell through the negation rules incorrectly
- [`github-gitignore-template`](../github-gitignore-template/SKILL.md) — standard `.gitignore` template generator; useful when merging whitelist blocks with generated OS/IDE gitignore patterns
- [`skill-cross-reference-audit`](../general/skill-cross-reference-audit/SKILL.md) — automated audit for skill graph issues in the library; run after creating or modifying this skill to verify cross-reference integrity
- [`script-over-instruction-decomposition`](../script-over-instruction-decomposition/SKILL.md) — decomposition pattern that this skill follows: the deterministic `.gitignore` block generation is the script-tier core, while the whitelist determination and verification steps remain as prose judgement calls
- [`git-commit-message-reword`](../git-commit-message-reword/SKILL.md) — commit message discipline for the commit that introduces the whitelist pattern; follow its commit-message rules when committing the `.gitignore` addition
- [`git-commit-identity-rewrite`](../git-commit-identity-rewrite/SKILL.md) — author/committer metadata handling; relevant if the whitelist commit includes untracked-file removal that touches previously committed content
- [`git-rebase-standardization`](../git-rebase-standardization/SKILL.md) — interactive rebase discipline; relevant when the whitelist commit is part of a larger commit sequence that needs reorganizing before push
