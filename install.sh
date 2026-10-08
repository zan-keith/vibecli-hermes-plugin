#!/usr/bin/env bash
# Install the Vibe CLI provider plugin into Hermes's model-provider directory.
#
# Usage:
#   ./install.sh              # symlink (default; keeps the plugin synced with this clone)
#   ./install.sh --copy       # copy files instead of symlinking
#
# Environment overrides:
#   HERMES_HOME   Hermes home directory (default: ~/.hermes)
set -euo pipefail

hermes_home="${HERMES_HOME:-$HOME/.hermes}"
plugin_dir="$hermes_home/plugins/model-providers/vibe-cli-provider"
src_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mode="symlink"

if [[ "${1:-}" == "--copy" ]]; then
  mode="copy"
elif [[ -n "${1:-}" ]]; then
  printf 'Usage: %s [--copy]\n' "$0" >&2
  exit 1
fi

if [[ ! -f "$src_dir/plugin.yaml" || ! -f "$src_dir/__init__.py" ]]; then
  printf 'Error: plugin payload (plugin.yaml, __init__.py) not found in %s\n' "$src_dir" >&2
  exit 1
fi

mkdir -p "$(dirname "$plugin_dir")"

if [[ -L "$plugin_dir" ]]; then
  rm "$plugin_dir"
elif [[ -e "$plugin_dir" ]]; then
  printf 'Refusing to replace existing directory: %s\n' "$plugin_dir" >&2
  printf 'Remove it manually first, or choose a different HERMES_HOME.\n' >&2
  exit 1
fi

if [[ "$mode" == "symlink" ]]; then
  ln -s "$src_dir" "$plugin_dir"
  printf 'Installed (symlink): %s -> %s\n' "$plugin_dir" "$src_dir"
else
  mkdir -p "$plugin_dir"
  cp "$src_dir/plugin.yaml" "$src_dir/__init__.py" "$plugin_dir/"
  printf 'Installed (copy): %s\n' "$plugin_dir"
fi

if [[ ! -f "$HOME/.vibe/.env" && -z "${VIBE_API_KEY:-}" ]]; then
  printf '\nNote: no Vibe CLI key found (~/.vibe/.env missing, VIBE_API_KEY unset).\n'
  printf 'Run "vibe --setup" once to log in, or set VIBE_API_KEY manually.\n'
fi

printf '\nDone. Restart Hermes and run: hermes model\n'
printf 'Select "Mistral Vibe CLI (Vibe plan quota)".\n'
