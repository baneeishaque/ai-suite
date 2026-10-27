# Maintainer and Contributor Discussion

> **Scope:** The Homebrew PR/issue record for the `antigravity` split · **Verified:** 2026-10-27

This page records who said what in the Homebrew repository, what the maintainers decided, and what
remains unanswered. It is a source record, not a rumor summary. Every claim links to the PR, issue, or
comment it comes from.

## Method

- Searched Homebrew/homebrew-cask pull requests, issues, and commits for `antigravity`.
- Searched Homebrew/brew and Homebrew/homebrew-cask GitHub Discussions; the GraphQL count was zero for
  both.
- Searched GitLab, Bitbucket, Azure DevOps, and Gitee for a maintainer thread; none was found.
- Read the exact comments through the GitHub API on 2026-10-27.
- Checked Homebrew organization membership with `gh api orgs/Homebrew/members/<login>`: HTTP 204 means
  member, HTTP 404 means not a member.

## The split PRs

| PR | Cask | Version | Merge time (UTC) | Merged by | Review notes |
| --- | --- | --- | --- | --- | --- |
| [#265182](https://github.com/Homebrew/homebrew-cask/pull/265182) | `antigravity` | `2.0.1` | 2026-05-21 06:11 | `khipp` | Approved by `krehel`, `chenrui333`, and `khipp` |
| [#265183](https://github.com/Homebrew/homebrew-cask/pull/265183) | `antigravity-cli` | `1.0.0` | 2026-05-21 06:07 | `khipp` | `bevanjkay` left an approval comment |
| [#265184](https://github.com/Homebrew/homebrew-cask/pull/265184) | `antigravity-ide` | `2.0.2` | 2026-05-22 08:57 | `khipp` | IDE split; contains the IDE-loss report |

The App cask merged about 27 hours before the IDE cask. That gap is the entire "my IDE disappeared"
incident: the `antigravity` token had already moved to the App, and the `antigravity-ide` token did not
exist yet.

## The exact Q&A

`singularitti` asked the clarifying question in PR #265489 on 2026-05-22 at 10:28 UTC:

- Question: [#265489 comment](https://github.com/Homebrew/homebrew-cask/pull/265489#issuecomment-4517872767)
- Answer: [#265489 comment](https://github.com/Homebrew/homebrew-cask/pull/265489#issuecomment-4518005201)

`0xCAFEBABEx0` answered at 10:49 UTC with the three-product mapping:

- `antigravity` is the Antigravity 2 agent orchestration app: `Antigravity.app`, bundle identifier
  `com.google.antigravity`.
- `antigravity-ide` is the IDE app: `Antigravity IDE.app`, bundle identifier
  `com.google.antigravity-ide`, with `agy-ide` and `antigravity-ide` shims.
- `antigravity-cli` is the standalone terminal CLI, installed as `agy`.

The PR was closed as unnecessary. The answer lives in the comment, not in a merged document. That is
why this guide records it.

`khipp` also asked a question in the same PR earlier:
[#265489 comment](https://github.com/Homebrew/homebrew-cask/pull/265489#issuecomment-4517610981).

## The IDE-loss report

On 2026-05-22 at 05:58 UTC, `sramekmichal` wrote on PR #265184:

> "My IDE just got lost, because cask antigravity was updated"

The original comment ends with a smiley emoji. The comment is at
[#265184 comment](https://github.com/Homebrew/homebrew-cask/pull/265184#issuecomment-4515581344).

This is the clearest user-side evidence of the 27-hour gap. It was posted about three hours before the
IDE cask merged.

## Who is who

| Login | Role in this record | Homebrew organization member? | Evidence |
| --- | --- | --- | --- |
| `khipp` | Merged all three split PRs; asked a question in #265489 | Yes (HTTP 204) | `gh api orgs/Homebrew/members/khipp` |
| `bevanjkay` | Reviewed the original cask path rename; approved #265183 | Yes (HTTP 204) | `gh api orgs/Homebrew/members/bevanjkay` |
| `krehel` | Approved #265182 | Yes (HTTP 204) | `gh api orgs/Homebrew/members/krehel` |
| `chenrui333` | Approved #265182 | Yes (HTTP 204) | `gh api orgs/Homebrew/members/chenrui333` |
| `0xCAFEBABEx0` | Author of the split casks; answered the Q&A | No (HTTP 404) | `gh api orgs/Homebrew/members/0xCAFEBABEx0` |
| `singularitti` | Asked the Q&A question | No (HTTP 404) | `gh api orgs/Homebrew/members/singularitti` |
| `sramekmichal` | Reported the IDE loss | Not assessed | PR comment only |

The practical distinction is that `khipp`, `bevanjkay`, `krehel`, and `chenrui333` are Homebrew
maintainers with merge or review authority. `0xCAFEBABEx0` is the contributor who authored the split
and supplied the authoritative mapping. `singularitti` and `sramekmichal` are users reporting or
asking.

`bevanjkay`'s approval on #265183 was explicit:

> "Thanks for the detailed response @0xCAFEBABEx0 - all makes sense to me."

Link: [#265183 comment](https://github.com/Homebrew/homebrew-cask/pull/265183#issuecomment-4504069865).

## What the maintainers decided

- **Three tokens, one per product.** `antigravity` is the App, `antigravity-ide` is the IDE, and
  `antigravity-cli` is the CLI.
- **No alias or replacement token.** PR #265489 was closed as unnecessary; the mapping is documented
  in the comment instead.
- **No `conflicts_with`.** The two GUI casks can be installed together.
- **No caveat about the old bundle identifier.** The current cask sources do not warn that the App
  inherited the old IDE's app path and identifier.
- **No automatic migration.** Neither cask moves old IDE settings into the new IDE's directories.

## What remains open

These questions are not answered in the sources reviewed. They are recorded so future maintainers do
not mistake silence for a decision:

- Will the App ever expose a CLI binary, or will `agy` remain exclusive to the CLI cask?
- Will the App and IDE merge back into one product or one cask?
- Will the App cask add a `caveats` warning about the pre-split bundle identifier?
- Will the App's minimum macOS stay at 13 while Google's download page says 12?
- Will either cask gain a migration helper for old IDE settings?

## Post-split issues

| Item | What happened | Link |
| --- | --- | --- |
| #280806 | `antigravity-ide` livecheck/outdated report | [Issue](https://github.com/Homebrew/homebrew-cask/issues/280806) |
| #280831 | Fix for #280806, landed in `2.5.5` | [PR](https://github.com/Homebrew/homebrew-cask/pull/280831) |
| #246183 | Historical xattr error on the pre-split cask's `agy` binary | [Issue](https://github.com/Homebrew/homebrew-cask/issues/246183) |
| #246184 | Shim-script fix for #246183 | [PR](https://github.com/Homebrew/homebrew-cask/pull/246184) |
| #265489 | The three-cask Q&A; closed as unnecessary | [PR](https://github.com/Homebrew/homebrew-cask/pull/265489) |

## Coverage outside Homebrew

- **Homebrew GitHub Discussions:** no thread. The GraphQL count for `antigravity` was zero in both
  Homebrew/brew and Homebrew/homebrew-cask.
- **GitLab, Bitbucket, Azure DevOps, Gitee:** no maintainer discussion of this split was found.
- **Third-party explainer:** a note.com article published 2026-05-24 covers the change from a user's
  perspective: <https://note.com/sojin25/n/n53cabf524d1c?hl=en>. It is not a maintainer source.

## Interpretation

- The split was intentional product alignment, not a Homebrew mistake. Google introduced a separate
  agent platform; Homebrew created a token for it and a token for the retained IDE.
- The IDE loss was a sequencing artifact. The App cask merged about 27 hours before the IDE cask, and
  the App inherited the old IDE's identity, so the upgrade replaced the IDE in place.
- The maintainers consider the three-token layout correct. The clarifying PR was closed, not merged,
  because the existing comments were deemed sufficient.
- The old 1.x `antigravity` IDE identity is historical. Do not use it to infer what the current
  `antigravity` token installs.

## Related

- [README.md](README.md) — overview and decision table
- [product-history.md](product-history.md) — full timeline
- [cask-reference.md](cask-reference.md) — current cask fields
- [sources.md](sources.md) — every source and retrieval command
