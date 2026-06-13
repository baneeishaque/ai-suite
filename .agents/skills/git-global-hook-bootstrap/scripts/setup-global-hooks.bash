#!/bin/bash
# One-time machine setup: symlink ~/.git-hooks/ to repo dotfiles/git-hooks/
# then set git --global core.hooksPath.
#
# Usage: bash setup-global-hooks.bash <path-to-dotfiles/git-hooks>
#   Example: bash setup-global-hooks.bash "$PWD/dotfiles/git-hooks"
#
# Idempotent: safe to run multiple times; second run overwrites the
# same symlink and git config value with no side effects.
#
# Tier: 2 (Bash) — shell glue: creates symlink, runs git config.
# See scripting-language-selection-rules.md section 3.4.

set -euo pipefail

DOTFILES_DIR="${1:-}"

if [ -z "$DOTFILES_DIR" ]; then
  echo "Usage: bash setup-global-hooks.bash <path-to-dotfiles/git-hooks>"
  echo "Example: bash setup-global-hooks.bash \"\$PWD/dotfiles/git-hooks\""
  exit 1
fi

if [ ! -d "$DOTFILES_DIR" ]; then
  echo "Error: '$DOTFILES_DIR' does not exist or is not a directory"
  exit 1
fi

# Idempotent: -f replaces existing symlink
ln -sf "$DOTFILES_DIR" ~/.git-hooks
echo "[global-hooks] Symlinked: ~/.git-hooks -> $DOTFILES_DIR"

# Idempotent: setting same value again is harmless
git config --global core.hooksPath ~/.git-hooks
echo "[global-hooks] Set: core.hooksPath = ~/.git-hooks"

echo "[global-hooks] Done. Every checkout will auto-bootstrap repo hooks."
