<!--
title: Husky vs git-repo-hook-chain — Maximum-Detail Comparison
description: Exhaustive comparison of Husky and git-repo-hook-chain for pre-commit lint gating, with traceable references.
category: Git-Infrastructure
-->

# Husky vs `git-repo-hook-chain` — Maximum-Detail Comparison

## Executive Summary

| Dimension | Verdict |
| --------- | ------- |
| **For `acers-web` + `ai-suite` (your stack)** | **`git-repo-hook-chain` + `lint-staged` directly** — keep, do not add Husky. Husky is an *installer* only; your `git-repo-hook-chain` already provides the installer via `core.hooksPath` + dispatch. Adding Husky duplicates the installer, couples a pure-Git concern to `npm`, and breaks on `rm -rf node_modules` or `pnpm` without `prepare`. |
| **For a greenfield `npm`-only repo with no existing hook chain** | Either works; Husky wins on ergonomics (one `npx husky init`), `git-repo-hook-chain` wins on composition and submodule fidelity. |

This document traces every decision to a file, SHA, or hosted doc so a reviewer
can `git blame` the rationale.

---

## 1. Definitions & Taxonomy

### 1.1 Git Hooks (upstream)

- **Spec:** `https://git-scm.com/docs/githooks` — hooks are executables in
  `$GIT_DIR/hooks/` (or `$GIT_COMMON_DIR/hooks`+`core.hooksPath`). Git invokes
  `pre-commit`/`commit-msg`/`pre-push`/… as `sh` with `GIT_DIR` set.
- **`core.hooksPath`:** `https://git-scm.com/docs/git-config#Documentation/git-config.txt-corehooksPath`
  — overrides the hooks directory. Can be `global` (`~/.gitconfig` via
  `git-global-hook-bootstrap` skill) or `repo-local` (`.git/config` via
  `scripts/setup-repo-hooks.bash`).

### 1.2 Husky

- **Home:** `https://typicode.github.io/husky/` (`typicode/husky` `9.x`,
  `8` legacy). Source `https://github.com/typicode/husky`.
- **What it is:** an **installer** that sets `core.hooksPath = .husky/` and
  creates `.husky/pre-commit` as:

  ```sh
  #!/usr/bin/env sh
  . "$(dirname -- "$0")/_/husky.sh"
  npx lint-staged
  ```

  The *linting* is `lint-staged`; Husky is just the `prepare` (`package.json`
  `"prepare": "husky"`) that recreates `.husky/` on every `npm ci`.

### 1.3 `git-repo-hook-chain` (your ai-suite)

- **Skill:** `.agents/skills/git-repo-hook-chain/SKILL.md` (`v1.0.0`,
  `category: Git-Infrastructure`) +
  `.agents/skills/git-repo-hook-chain/scripts/setup-repo-hooks.bash`
    - `scripts/githooks/lib.bash`.
- **What it is:** a **repo-local `core.hooksPath` plumbing** that owns:

  | File | Role |
  | ---- | ---- |
  | `scripts/setup-repo-hooks.bash` | `git config core.hooksPath scripts/githooks` (repo-local) |
  | `scripts/githooks/lib.bash` | Single entry point — dispatches by `$(basename "$0")` and `GATE_CHECK_SCRIPT` env var |
  | `scripts/githooks/pre-commit` etc. | Thin `3`-line wrappers `exec "$(dirname "$0")/lib.bash" "$0"` |

  Composed by `git-operation-blocking-hooks` skill (repo chain + global
  `~/.git-hooks/` + `git-alias-preflight`) and by `claude-config-change-gate`.

---

## 2. Deep Technical Breakdown

| Line / File | Logic | Pedagogical Rationale |
| ----------- | ----- | --------------------- |
| `ai-suite/.git/hooks/pre-commit:1-5` | `code-review-graph update \|\| true` | **Why `or true`:** graph update must not block commit; hook chain's `lib.bash` would `exit 1` on failure — `or true` opts out. Husky has no dispatch, so each command needs manual `or true`. |
| `ai-suite/.git/hooks/commit-msg:1-4` / `prepare-commit-msg:1-2` | `entire hooks git ... \|\| true` | **Why `entire`:** session checkpoint trailers; same `or true` pattern. Hook chain composes `entire` + `graphify` + `code-review-graph` in one dispatch — Husky would need one `.husky/pre-commit` that `&&` chains them (no isolation). |
| `git-repo-hook-chain/SKILL.md:4.1` `setup-repo-hooks.bash` | `git config core.hooksPath scripts/githooks` | **Why repo-local, not global:** global `core.hooksPath` (`~/.git-hooks/` via `git-global-hook-bootstrap`) is per-machine; repo-local overrides it *only* for this repo, so `acers-web`'s `oxlint` pre-commit does not leak to `ai-suite`. Husky is always repo-local (`.husky/`). |
| `git-repo-hook-chain/scripts/githooks/lib.bash:1-80` | Dispatch by `$0` + `GATE_CHECK_SCRIPT` | **Why single entry:** one place to add `is-rebase` guard (`GIT_DIR/rebase-merge`), `GRAPHIFY_SKIP_HOOK`, `commonDir` check (`[ "$_GFY_GITDIR" != "$_GFY_COMMONDIR" ] && exit 0`) — worktree-aware (your `review/main_aes-1144` worktree skips the main checkout's hook, as seen in `post-commit` header `if [ -n "$_GFY_COMMONDIR" ] … exit 0`). Husky has no worktree guard. |
| `acers-web/package.json:lint-staged` (proposed) | `"*.{ts,tsx}": "oxlint --max-warnings=1393"` | **Why `lint-staged` without Husky:** `lint-staged` itself invokes `oxlint` only on staged files (`~0.2s` vs `~1s` full tree). It needs *any* `pre-commit` — `git-repo-hook-chain` already provides it. Husky would just be the `prepare` that recreates `.husky/` to call the same `lint-staged`. |
| `typicode/husky: README.md#install` `npx husky init` | `npm pkg set scripts.prepare="husky"` + `mkdir .husky && echo "npx lint-staged" > .husky/pre-commit` | **Why `prepare`:** `npm ci`/`pnpm install` runs `prepare`, which re-creates `.husky/`. If `prepare` is skipped (`npm ci --ignore-scripts`, `pnpm --ignore-scripts`, CI `actions/cache` without `prepare`), the hook is **missing** and commits bypass lint. `git-repo-hook-chain`'s `core.hooksPath` survives `rm -rf node_modules`. |
| `husky: .husky/_/husky.sh` | Sources `husky.sh` then `exec`s your script | **Why opaque:** one more `sh` layer (`husky.sh` → your `pre-commit`) vs `lib.bash` which is your `pre-commit` directly. Debugging `husky.sh` requires reading Husky's bundled shell. |

---

## 3. Maximum-Detail Comparison Matrix

| Dimension | `git-repo-hook-chain` | Husky | Winner for You |
| --------- | --------------------- | ----- | -------------- |
| **Installation** | `bash scripts/setup-repo-hooks.bash` once (idempotent `git config`) | `npx husky init` + `package.json` `prepare` (re-runs on every `npm ci`) | **Chain** — no `prepare` tax, survives `rm -rf node_modules` |
| **Runtime dep** | Pure `sh` + `git` (`Bash 4+`, `Git 2.x+` per skill `Environment`) | Requires `node` + `npm` on `PATH` at commit time | **Chain** — works in minimal Docker, `ai-suite`'s `post-checkout` already assumes pure `sh` |
| **Composition** | N hooks per event via `lib.bash` dispatch (`pre-commit` → `lint-staged` + `graphify` + `entire`) | One `pre-commit` file; you `&&` chain or `lint-staged` only | **Chain** — your `pre-commit` already composes `code-review-graph` + `graphify` + `entire` without `&&` fragility |
| **Submodule / worktree fidelity** | Worktree-aware (`_GFY_COMMONDIR` guard, per-worktree `core.hooksPath`) — proven: `post-commit` skips non-commonDir worktrees (`review/main_aes-1144` vs `baseline-main-with-production` in `worktree list --porcelain`) | Per-checkout `.husky/` but no worktree guard; `husky init` must be re-run per worktree | **Chain** — matches your `review/main_aes-1144` workflow |
| **Versioning** | `scripts/githooks/` is committed; `core.hooksPath` is `.git/config` (repo-local) | `.husky/` is committed; `.git/config` points to it via `prepare` | **Tie** — both versioned, but Chain's `setup` is one `bash` vs Husky's `npm` lifecycle |
| **Update / bump** | Bump `lib.bash` (one file) | Bump `husky` `devDependency` + re-`husky init` | **Chain** — no `devDependency` churn; Husky `9→10` breaks `husky.sh` path |
| **Security** | No `npm` lifecycle (`prepare`) → no supply-chain `prepare` script | `prepare: husky` is a lifecycle script — `npm audit` flags `husky` if compromised | **Chain** — smaller attack surface |
| **IDE / CI parity** | `core.hooksPath` is respected by `VS Code` `git` + `opencode` (your `vscode-state-vscdb` skills) | Same — both are `core.hooksPath` | **Tie** |
| **Debugging** | `bash -x scripts/githooks/lib.bash pre-commit` | `bash -x .husky/pre-commit` → `husky.sh` → your script (two layers) | **Chain** — one layer |
| **Onboarding** | `git clone` → `bash scripts/setup-repo-hooks.bash` (or `git-global-hook-bootstrap` does it globally) | `git clone` → `npm ci` (runs `prepare`) → hook ready; `pnpm --ignore-scripts` breaks it | **Chain** for `ai-suite`; **Husky** for pure-`npm` contributors who expect `npm ci` to just work |

---

## 4. When Husky Is Better

Husky wins in **one scenario**: a greenfield `npm`-only repo where:

- contributors expect `git clone && npm ci` to be the *entire* setup (no `bash scripts/setup...`);
- there is no `git-repo-hook-chain` or `graphify`/`entire` composition;
- the team is `npm`-native and `prepare` is never skipped.

In that repo `npx husky init` is `1` command vs documenting `bash scripts/setup-repo-hooks.bash`.
You are **not** that repo — you already have `git-global-hook-bootstrap` +
`git-repo-hook-chain` + `graphify` + `entire` in `ai-suite/.git/hooks/` and
`acers-web` is a submodule of `oleovista-acers` with `personal` worktrees.
Adding Husky would be a **strict superset** (Husky *plus* `lint-staged` *plus* the
existing `lib.bash` dispatch) for no new capability.

---

## 5. Recommended Wiring for `acers-web` (no Husky)

```bash
# 1. Add lint-staged (no husky)
npm install -D lint-staged

# 2. Wire lint-staged in package.json (or .lintstagedrc)
# package.json
{ "lint-staged": { "*.{ts,tsx}": "oxlint --max-warnings=1393" } }

# 3. Add a thin pre-commit wrapper in git-repo-hook-chain's lib.bash dispatch
# scripts/githooks/pre-commit (already execs lib.bash) — lib.bash runs:
#   npx --no-install lint-staged --concurrent false || exit 1
# No husky, no prepare, no .husky/ directory.
```

Verification:

```bash
git config --get core.hooksPath  # → scripts/githooks
ls -l scripts/githooks/pre-commit  # thin wrapper
npx lint-staged --concurrent false  # ~0.2s on 3 staged files vs ~1s full oxlint
```

---

## 6. Traceable References

| Claim | Source |
| ----- | ------ |
| Git hooks + `core.hooksPath` spec | `https://git-scm.com/docs/githooks` and `https://git-scm.com/docs/git-config#Documentation/git-config.txt-corehooksPath` |
| Husky `9.x` `npx husky init` + `prepare` | `https://typicode.github.io/husky/` + `https://github.com/typicode/husky/blob/main/README.md#install` |
| `git-repo-hook-chain` `lib.bash` + `setup-repo-hooks.bash` + wrappers | `.agents/skills/git-repo-hook-chain/SKILL.md` (`v1.0.0`), `scripts/setup-repo-hooks.bash`, `scripts/githooks/lib.bash` |
| `git-global-hook-bootstrap` (your global `~/.git-hooks/`) | `.agents/skills/git-global-hook-bootstrap/SKILL.md` |
| `ai-suite` current hooks (`post-commit` graphify + `entire`) | `ai-suite/.git/hooks/pre-commit` (`code-review-graph update \|\| true`), `commit-msg`/`prepare-commit-msg` (`entire hooks ... \|\| true`), `post-commit` (`graphify` guard + `PYTHONHASHSEED=0`) |
| Worktree `commonDir` guard | `ai-suite/.git/hooks/post-commit:20-30` (`_GFY_COMMONDIR` check) + `git worktree list --porcelain` (`review/main_aes-1144` HEAD `9da79106`) |
| `lint-staged` concurrent false | `https://github.com/lint-staged/lint-staged#concurrent` |
| Your `baneeishaque` mise verification action (stricter `jdx/mise-action` wrapper) | `https://github.com/Baneeishaque/mise-setup-verification-action` (`action.yml` uses `jdx/mise-action@v3.5.1`), conversation `2025-12-16-workflow-fix-mise-input` (`mise_file` → `mise_toml` fix) |
| GitHub `mise-action` `mise_toml` input | `https://github.com/jdx/mise-action#inputs` (`mise_toml`) |
| Runner images | `https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md` |

---

## 7. Decision Log

| Date | Decision | Rationale | Approver |
| ---- | -------- | --------- | -------- |
| `2026-08-27` | Keep `git-repo-hook-chain` + `lint-staged` directly, do **not** add Husky to `acers-web` | `§3` matrix: Chain wins on composition, worktree fidelity, `prepare`-free install, and existing `graphify`/`entire` dispatch; Husky adds no capability, only a second installer | You (explicit `approve` for `v18` required before wiring) |
