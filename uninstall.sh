#!/usr/bin/env bash
# Remove the Vibe CLI provider plugin from Hermes.
#
# Usage:
#   ./uninstall.sh              # remove the installed plugin (symlink or copy)
#   ./uninstall.sh --keep-key   # also leave VIBE_API_KEY untouched (default behavior)
set -euo pipefail

hermes_home="${HERMES_HOME:-$HOME/.hermes}"
plugin_dir="$hermes_home/plugins/model-providers/vibe-cli-provider"

if [[ -L "$plugin_dir" ]]; then
  rm "$plugin_dir"
  printf 'Removed symlink: %s\n' "$plugin_dir"
elif [[ -d "$plugin_dir" ]]; then
  rm -rf "$plugin_dir"
  printf 'Removed directory: %s\n' "$plugin_dir"
else
  printf 'Not installed: %s\n' "$plugin_dir"
  exit 0
fi

printf 'Done. Restart Hermes for the change to take effect.\n'
