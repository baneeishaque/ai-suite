#!/usr/bin/env bash
# studio-settings--setup.bash — One-time setup for YouTube Studio settings skill.
#
# Creates persistent Chrome profile directory and symlink, and enables
# JXA automation support on macOS.
#
# Usage:
#   bash studio-settings--setup.bash

set -euo pipefail

PROFILE_DIR="$HOME/Lab_Data/configurations-private/youtube-studio-settings-chrome-profile"
SYMLINK_DIR="$HOME/.cache/studio-chrome-profile"

echo "==> Creating profile directory: $PROFILE_DIR"
mkdir -p "$PROFILE_DIR"

if [ -L "$SYMLINK_DIR" ]; then
    echo "==> Symlink already exists: $SYMLINK_DIR"
elif [ -d "$SYMLINK_DIR" ]; then
    echo "==> Warning: $SYMLINK_DIR is a real directory, not a symlink"
    echo "    Remove it and re-run to create symlink: rm -rf '$SYMLINK_DIR'"
else
    echo "==> Creating symlink: $SYMLINK_DIR → $PROFILE_DIR"
    ln -s "$PROFILE_DIR" "$SYMLINK_DIR"
fi

# Enable JXA (JavaScript for Automation) Chrome support on macOS
if [ "$(uname)" = "Darwin" ]; then
    echo "==> Enabling Chrome JavaScript from Apple Events..."
    defaults write com.google.Chrome AppleScriptEnabled -bool YES
    echo "    Also ensure Chrome menu: View → Developer → Allow JavaScript from Apple Events"
    echo "    (Or run: open -a 'Google Chrome' and check the menu item)"
fi

echo ""
echo "Setup complete."
echo "Profile: $PROFILE_DIR"
echo "Symlink: $SYMLINK_DIR"
