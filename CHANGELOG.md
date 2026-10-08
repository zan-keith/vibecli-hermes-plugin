# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-10-08

### Added

- Initial release: `vibe-cli` model-provider profile for Hermes Agent.
- Zero-config key loading from the Vibe CLI's `~/.vibe/.env`.
- Vibe plan model catalog with per-model capabilities and context windows.
- Reasoning-effort pass-through with per-family mapping and clamping
  (GLM low/high/max; high/none-only models clamp low/medium/minimal to high).
- Aliases: `vibe`, `mistral-vibe`, `vibe-cli-provider`.
- `install.sh` / `uninstall.sh` helper scripts (symlink or copy mode).
- Standalone test suite.
