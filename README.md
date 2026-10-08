# Vibe CLI Provider for Hermes Agent

A Hermes model-provider plugin that routes requests through your Mistral Vibe
plan key. Usage counts against your Vibe subscription quota instead of
pay-as-you-go API credits.

The plugin uses the official Mistral API at `https://api.mistral.ai/v1` with
the same key the official Vibe CLI stores in `~/.vibe/.env`. No proxy or extra
service is required.

## Requirements

- Hermes Agent
- A Mistral Vibe plan with coding included
- The official Vibe CLI, installed and logged in, or a manually configured key

## Quick start

Clone the repository:

```bash
git clone https://github.com/zan-keith/vibecli-hermes-plugin.git
cd vibecli-hermes-plugin
```

Install the plugin:

```bash
./install.sh
```

Install the Vibe CLI if needed:

```bash
uv tool install mistral-vibe
```

On headless or minimal Linux systems, the Vibe CLI build may need system
packages first:

```bash
sudo apt-get update
sudo apt-get install -y pkg-config libasound2-dev
```

Log in to Vibe:

```bash
vibe --setup
```

Restart Hermes and select the provider:

```bash
hermes model
```

Choose:

```text
Mistral Vibe CLI (Vibe plan quota)
```

## Install options

Use a symlink, so the installed plugin stays synced with your clone:

```bash
./install.sh
```

Copy the plugin files instead:

```bash
./install.sh --copy
```

Install into Hermes directly:

```bash
hermes plugins install https://github.com/zan-keith/vibecli-hermes-plugin.git
```

The plugin installs to:

```text
${HERMES_HOME:-$HOME/.hermes}/plugins/model-providers/vibe-cli-provider/
```

Remove the plugin with:

```bash
./uninstall.sh
```

## Configuration

Normally no configuration is needed after `vibe --setup`.

| Variable | Default | Purpose |
|---|---|---|
| `VIBE_API_KEY` | Loaded from `~/.vibe/.env` | Vibe plan API key |
| `MISTRAL_VIBE_API_KEY` | Unset | Alternative key variable |
| `VIBE_ENV_FILE` | `~/.vibe/.env` | Vibe CLI key file location |

If you do not want to install the Vibe CLI, set the key manually:

```bash
export VIBE_API_KEY=...
```

The plugin loads `MISTRAL_API_KEY` from the Vibe CLI env file and exposes it to
Hermes as `VIBE_API_KEY`. An explicit `VIBE_API_KEY` environment variable takes
priority.

## Models

The plugin includes these Vibe plan fallback models:

| Model | Context | Reasoning effort |
|---|---:|---|
| `mistral-large-4` | 1M | `none`, `high` |
| `mistral-medium-latest` | 256K | `none`, `high` |
| `mistral-small-latest` | 256K | `none`, `high` |
| `zai-glm-5-3` | 1M | `low`, `high`, `max` |
| `codestral-latest` | 256K | Not applicable |

Short model aliases:

| Alias | Model |
|---|---|
| `vibe` | `mistral-vibe-cli-latest` |
| `fast` | `mistral-vibe-cli-fast` |
| `glm` | `zai-glm-5-3` |

The live model list is always available from:

```bash
curl https://api.mistral.ai/v1/models
```

## How it works

1. The plugin reads the Vibe CLI key from `~/.vibe/.env` at import time.
2. Hermes sends normal OpenAI-compatible chat requests to the official Mistral
   API using that key.
3. Requests consume the Vibe plan quota.
4. Reasoning effort is mapped per model family to avoid invalid API values.

## Development

Run the standalone test suite:

```bash
uv run --with pytest python -m pytest tests/ -q
```

Run a syntax check:

```bash
python3 -m compileall -q __init__.py tests/
```

## Repository layout

```text
vibecli-hermes-plugin/
├── __init__.py     # Hermes provider registration
├── plugin.yaml     # Hermes plugin manifest
├── install.sh      # Symlink/copy installer
├── uninstall.sh    # Removes the installed plugin
├── tests/          # Standalone pytest suite
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## Security

Keep your Vibe key private. Do not paste it into chat, commit it to Git, or
expose a proxy in front of it.

## License

[MIT](LICENSE)
