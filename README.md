# Hermes Agent — Mistral Vibe CLI Provider

A model-provider plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent)
that routes requests through your **Mistral Vibe CLI plan key**, so usage counts
against the Vibe subscription quota instead of pay-as-you-go API credits.

It uses the same key the official [Vibe CLI](https://github.com/mistralai/mistral-vibe)
stores in `~/.vibe/.env` after `vibe --setup`, sends standard
`Authorization: Bearer` requests to the official Mistral API
(`https://api.mistral.ai/v1`), and requires no proxy or extra service.
Mistral has publicly confirmed third-party use of the Vibe key (the Vibe plan
budget is consumed before any pay-as-you-go credits).

## How it works

1. At import time the plugin reads `MISTRAL_API_KEY` from the Vibe CLI's
   `~/.vibe/.env` and exposes it as `VIBE_API_KEY` (Hermes's credential
   resolver picks it up from there). No manual key copying.
2. Hermes sends normal OpenAI-compatible chat-completions requests to the
   official Mistral API with that key — every request bills against the Vibe
   plan quota, exactly like a Vibe CLI request.
3. Reasoning-effort pass-through is handled per model family: GLM accepts
   `low`/`high`/`max` (others map down to `low`); Mistral reasoning models
   accept `none`/`high` (low/medium/minimal clamp up to `high`); known
   non-reasoning models skip the parameter entirely to avoid HTTP 400.

## Requirements

- [Hermes Agent](https://github.com/NousResearch/hermes-agent)
- A Mistral Vibe plan with coding included (Pro, Team or Enterprise)
- The official Vibe CLI, installed and logged in — or a manually copied key
  (see [Setup](#setup))

## Install

### Option A — install script (recommended)

```bash
./install.sh           # symlink (default; stays synced with this clone)
./install.sh --copy    # copy files instead
```

The script installs into
`${HERMES_HOME:-$HOME/.hermes}/plugins/model-providers/vibe-cli-provider/`,
refuses to clobber an existing installation, and warns when no Vibe key is
detectable. `uninstall.sh` removes it.

### Option B — `hermes plugins install`

```bash
hermes plugins install <this-repo-url>
```

Provider discovery imports any plugin in `$HERMES_HOME/plugins/` whose
`plugin.yaml` declares `kind: model-provider`. On Hermes versions predating
the model-provider install-routing fix (upstream issues #76372 / PR #76387),
the command can report success without making the provider discoverable —
use Option A in that case.

## Setup

Nothing to configure if the Vibe CLI is logged in (`vibe --setup` once):

```bash
vibe --setup    # browser login; stores the plan key in ~/.vibe/.env
```

If you don't want the Vibe CLI installed, copy the **Vibe API Key** from
Vibe → Code → Extensions → Advanced (the panel also shows your monthly usage
and lets you rotate the key) and set it manually:

```bash
export VIBE_API_KEY=...
```

Then restart Hermes and run `hermes model` to select
**Mistral Vibe CLI (Vibe plan quota)**.

### Configuration

| Variable | Default | Meaning |
|---|---|---|
| `VIBE_API_KEY` | auto-loaded from `~/.vibe/.env` | The Vibe plan key. Set it to override the file. |
| `MISTRAL_VIBE_API_KEY` | unset | Alternative env var, checked second. |
| `VIBE_ENV_FILE` | `~/.vibe/.env` | Where the plugin looks for the CLI's key. |

## Models

Models included in the Vibe plan (verified via the plan key, Oct 2026):

| Model ID | Also available as | Context | Reasoning effort |
|---|---|---|---|
| `mistral-large-4` | `mistral-large-4-0` | 1M | `none`, `high` |
| `mistral-medium-latest` | `mistral-vibe-cli-latest` | 256K | `none`, `high` |
| `mistral-small-latest` | `mistral-vibe-cli-fast` | 256K | `none`, `high` |
| `zai-glm-5-3` | `zai-glm-latest`, `zai-glm-5` | 1M | `low`, `high`, `max` |
| `codestral-latest` | | 256K | — |

`curl https://api.mistral.ai/v1/models` with your key always lists what the
plan currently includes. The plugin also registers short aliases for
`/model`: `vibe` → `mistral-vibe-cli-latest`, `fast` → `mistral-vibe-cli-fast`,
`glm` → `zai-glm-5-3`.

## Repository layout

```
hermes-vibe-provider/
├── __init__.py     # plugin payload: registers the vibe-cli ProviderProfile
├── plugin.yaml     # Hermes plugin manifest (kind: model-provider)
├── install.sh      # symlink/copy installer
├── uninstall.sh    # removal script
├── tests/          # standalone pytest suite (no Hermes checkout needed)
├── CHANGELOG.md
├── LICENSE          # MIT
└── README.md
```

## Development

### Run the tests

```bash
python3 -m pytest tests/ -v        # standalone (stubs the Hermes registry)
```

Against a real Hermes checkout (optional; exercises the actual
`ProviderProfile` base class and discovery):

```bash
git clone https://github.com/NousResearch/hermes-agent
HERMES_SRC=../hermes-agent PYTHONPATH=.. python3 -m pytest tests/ -v
```

Syntax check without any dependencies:

```bash
python3 -m compileall -q __init__.py tests/
```

### Releasing a new version

1. Bump `version:` in `plugin.yaml`.
2. Add a `CHANGELOG.md` entry.
3. Tag `vX.Y.Z`.

## Terms-of-service notes

- The key comes from Mistral's own login flow and calls the same public API
  endpoint with the same standard header the CLI uses; nothing is scraped,
  impersonated, or reverse-engineered.
- The Vibe plan is a personal/seat subscription: keep the key private, don't
  share it, and don't expose any proxy in front of it beyond loopback.
- Mistral can change its terms at any time; re-check them if usage patterns
  change.

## License

[MIT](LICENSE)
