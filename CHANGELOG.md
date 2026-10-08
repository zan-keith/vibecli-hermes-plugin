# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Changed

- Rewrote the README for a concise quick-start flow.
- Clarified Vibe CLI system dependencies for headless Linux installs.
- Fixed Hermes `0.21.x` provider registration by assigning compatibility
  metadata after constructing the provider profile.

## [1.0.0] - 2026-10-08

### Added

- Initial release: `vibe-cli` model-provider profile for Hermes Agent.
- Zero-config key loading from the Vibe CLI's `~/.vibe/.env`.
- Vibe plan model catalog with per-model capabilities and context windows.
- Reasoning-effort pass-through with per-family mapping and clamping.
- Aliases: `vibe`, `mistral-vibe`, `vibe-cli-provider`.
- `install.sh` / `uninstall.sh` helper scripts.
- Standalone test suite.
