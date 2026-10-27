# Sources and Verification Record

> **Retrieved:** 2026-10-27 · **Tap HEAD:** `896f63b6900bcf77a396b171525a221e1e379c9e` ·
> **Method:** Homebrew JSON API, Ruby source, and GitHub API

This page lists every source used in this folder, the retrieval date, and the commands used to verify
the cask facts. It also separates verified facts from inferences.

## Homebrew cask pages

- `antigravity`: <https://formulae.brew.sh/cask/antigravity>
- `antigravity-ide`: <https://formulae.brew.sh/cask/antigravity-ide>
- `antigravity-cli` (cross-reference): <https://formulae.brew.sh/cask/antigravity-cli>

## Homebrew JSON APIs

- `antigravity`: <https://formulae.brew.sh/api/cask/antigravity.json>
- `antigravity-ide`: <https://formulae.brew.sh/api/cask/antigravity-ide.json>
- `antigravity-cli` (cross-reference): <https://formulae.brew.sh/api/cask/antigravity-cli.json>

The JSON API is the machine-readable source for `version`, `url`, `sha256`, `variations`, `artifacts`,
`depends_on`, `auto_updates`, `analytics`, `tap_git_head`, `ruby_source_path`, and
`ruby_source_checksum`.

## Ruby sources at tap HEAD

- `antigravity`:
  <https://github.com/Homebrew/homebrew-cask/blob/896f63b6900bcf77a396b171525a221e1e379c9e/Casks/a/antigravity.rb>
- `antigravity-ide`:
  <https://github.com/Homebrew/homebrew-cask/blob/896f63b6900bcf77a396b171525a221e1e379c9e/Casks/a/antigravity-ide.rb>
- `antigravity-cli` (cross-reference):
  <https://github.com/Homebrew/homebrew-cask/blob/896f63b6900bcf77a396b171525a221e1e379c9e/Casks/a/antigravity-cli.rb>

Raw forms:

- `antigravity`:
  <https://raw.githubusercontent.com/Homebrew/homebrew-cask/896f63b6900bcf77a396b171525a221e1e379c9e/Casks/a/antigravity.rb>
- `antigravity-ide`:
  <https://raw.githubusercontent.com/Homebrew/homebrew-cask/896f63b6900bcf77a396b171525a221e1e379c9e/Casks/a/antigravity-ide.rb>

## Pull requests

| PR | Subject | Link |
| --- | --- | --- |
| #237135 | Original `antigravity` cask, added 2025-11-18 | <https://github.com/Homebrew/homebrew-cask/pull/237135> |
| #265182 | `antigravity` `2.0.1`, the App split | <https://github.com/Homebrew/homebrew-cask/pull/265182> |
| #265183 | `antigravity-cli` `1.0.0`, the CLI split | <https://github.com/Homebrew/homebrew-cask/pull/265183> |
| #265184 | `antigravity-ide` `2.0.2`, the IDE split | <https://github.com/Homebrew/homebrew-cask/pull/265184> |
| #265489 | Three-cask Q&A; closed as unnecessary | <https://github.com/Homebrew/homebrew-cask/pull/265489> |
| #246184 | Historical shim fix for the pre-split `agy` binary | <https://github.com/Homebrew/homebrew-cask/pull/246184> |
| #280831 | Livecheck/outdated fix for `antigravity-ide` (`2.5.5`) | <https://github.com/Homebrew/homebrew-cask/pull/280831> |

## Issues

| Issue | Subject | Link |
| --- | --- | --- |
| #246183 | Historical xattr error on the pre-split cask's `agy` binary | <https://github.com/Homebrew/homebrew-cask/issues/246183> |
| #280806 | `antigravity-ide` livecheck/outdated report | <https://github.com/Homebrew/homebrew-cask/issues/280806> |

## Commits

| Commit | Subject |
| --- | --- |
| `3f7175924f` | Cask path rename from `Casks/g/google-antigravity.rb` to `Casks/a/antigravity.rb` |
| `72cab260f1` | Last pre-split release, `1.23.2` |
| `896f63b6900bcf77a396b171525a221e1e379c9e` | Tap HEAD used for the current cask facts |

## Google official sources

- Antigravity 2 product page: <https://antigravity.google/product/antigravity-2>
- Antigravity IDE product page: <https://antigravity.google/product/antigravity-ide>
- Antigravity CLI product page: <https://antigravity.google/product/antigravity-cli>
- Antigravity home page (the pre-split cask's homepage): <https://antigravity.google/>
- Google Antigravity support: <https://antigravity.google/support>

Google's Antigravity 2.0 announcement is dated 2026-05-19. The announcement's "there is no IDE" line
and its note that existing installs auto-update to 2.0 are quoted in
[product-history.md](product-history.md#timeline). The product pages above are the durable links; the
announcement post itself is not reproduced here.

## Third-party sources

- note.com explainer, published 2026-05-24:
  <https://note.com/sojin25/n/n53cabf524d1c?hl=en>. This is a user-facing article, not a maintainer
  source.

## GitHub search coverage

- Homebrew/homebrew-cask pull requests, issues, and commits: searched for `antigravity`.
- Homebrew/brew and Homebrew/homebrew-cask GitHub Discussions: GraphQL count was zero for
  `antigravity`.
- GitLab, Bitbucket, Azure DevOps, and Gitee: no maintainer thread found.
- Homebrew organization membership: checked with `gh api orgs/Homebrew/members/<login>`; 204 means
  member, 404 means not a member.

## Commands used

```bash
# Cask JSON, selected fields
curl -fsSL --connect-timeout 10 --max-time 30 \
  https://formulae.brew.sh/api/cask/antigravity.json \
  | jq '{token, name, desc, homepage, version, url, sha256, artifacts, depends_on, auto_updates, variations, analytics, tap_git_head, ruby_source_path, ruby_source_checksum}'
curl -fsSL --connect-timeout 10 --max-time 30 \
  https://formulae.brew.sh/api/cask/antigravity-ide.json \
  | jq '{token, name, desc, homepage, version, url, sha256, artifacts, depends_on, auto_updates, variations, analytics, tap_git_head, ruby_source_path, ruby_source_checksum}'

# Ruby sources at the recorded tap HEAD
curl -fsSL --connect-timeout 10 --max-time 30 \
  https://raw.githubusercontent.com/Homebrew/homebrew-cask/896f63b6900bcf77a396b171525a221e1e379c9e/Casks/a/antigravity.rb
curl -fsSL --connect-timeout 10 --max-time 30 \
  https://raw.githubusercontent.com/Homebrew/homebrew-cask/896f63b6900bcf77a396b171525a221e1e379c9e/Casks/a/antigravity-ide.rb

# PR and issue metadata
gh api repos/Homebrew/homebrew-cask/pulls/265182
gh api repos/Homebrew/homebrew-cask/pulls/265183
gh api repos/Homebrew/homebrew-cask/pulls/265184
gh api repos/Homebrew/homebrew-cask/pulls/265489
gh api repos/Homebrew/homebrew-cask/issues/265184/comments
gh api repos/Homebrew/homebrew-cask/issues/265489/comments
gh api repos/Homebrew/homebrew-cask/issues/280806
gh api repos/Homebrew/homebrew-cask/issues/246183

# Homebrew organization membership
gh api orgs/Homebrew/members/khipp
gh api orgs/Homebrew/members/bevanjkay
gh api orgs/Homebrew/members/krehel
gh api orgs/Homebrew/members/chenrui333
gh api orgs/Homebrew/members/0xCAFEBABEx0
gh api orgs/Homebrew/members/singularitti

# Discussions count (GraphQL)
gh api graphql -f query='{ search(query: "antigravity repo:Homebrew/homebrew-cask type:discussions", type: DISCUSSION, first: 1) { discussionCount } }'
gh api graphql -f query='{ search(query: "antigravity repo:Homebrew/brew type:discussions", type: DISCUSSION, first: 1) { discussionCount } }'

# Installed state (only if the casks are installed)
brew info --cask antigravity
brew info --cask antigravity-ide
mdls -name kMDItemCFBundleIdentifier /Applications/Antigravity.app
mdls -name kMDItemCFBundleIdentifier "/Applications/Antigravity IDE.app"
mdls -name kMDItemVersion /Applications/Antigravity.app
mdls -name kMDItemVersion "/Applications/Antigravity IDE.app"
```

## Evidence classification

| Class | Meaning | Examples in this folder |
| --- | --- | --- |
| Cask source | Read from the JSON API or the Ruby source at tap HEAD | Versions, checksums, artifacts, livecheck, zap paths |
| GitHub record | Read from the PR, issue, commit, or comment APIs | Merge times, quotes, approvals, membership |
| Vendor documentation | Read from Google's product pages or announcement | Product identity, "there is no IDE", minimum OS claim |
| Inference | Derived from cask paths or product behavior, not directly stated | Old IDE data may be read by the new App; new IDE starts with new paths |
| Locally reproduced | Reproduced on the verification machine | **None** — neither GUI cask was installed |

## Verification status

| Claim type | Status |
| --- | --- |
| Cask metadata, URLs, checksums, artifacts, livecheck | Verified against the JSON API and Ruby source on 2026-10-27 |
| App bundle names and bundle identifiers | Verified from the cask Ruby source (`app` and `uninstall quit:`) on 2026-10-27 |
| PR/issue quotes and merge times | Verified from the GitHub API on 2026-10-27 |
| Homebrew organization membership | Verified with the members endpoint on 2026-10-27 |
| Product identity and the 2.0 announcement | Verified from Google's product pages and the announcement date |
| Old 1.x cask identity | Verified from the Homebrew cask Git history |
| Runtime behavior, sign-in, settings migration | **Not reproduced** |

## Related

- [README.md](README.md) — overview and decision table
- [product-history.md](product-history.md) — timeline and the IDE-loss window
- [cask-reference.md](cask-reference.md) — current cask fields
- [maintainer-discussion.md](maintainer-discussion.md) — exact PR and issue record
