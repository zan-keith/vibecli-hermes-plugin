# Mistral Vibe CLI Provider for Hermes Agent — Setup Guide

A complete walkthrough for installing, configuring, and using the Vibe CLI provider plugin in Hermes Agent.

---

## What this plugin does

Hermes Agent normally talks to Mistral through a **pay-as-you-go API key** — every request bills your Studio credit balance. If you have a **Mistral Vibe subscription** (Pro, Team, or Enterprise), that plan includes a generous monthly coding quota that regular API requests can't touch.

This plugin closes that gap. It registers a new provider in Hermes — **"Mistral Vibe CLI (Vibe plan quota)"** — that authenticates with the same plan key the official [Vibe CLI](https://github.com/mistralai/mistral-vibe) uses. Requests go straight to the official Mistral API (`https://api.mistral.ai/v1`) with that key, so:

- **Usage counts against your Vibe subscription quota** — the plan budget is consumed before any pay-as-you-go credits.
- **No proxy, gateway, or background service** — it's a plain Hermes plugin, two files.
- **Zero-config key handling** — the plugin reads the key the Vibe CLI already saved in `~/.vibe/.env`. Nothing to copy or paste.
- **Official API, official key** — the key comes from Mistral's own login flow and sends the same standard `Authorization: Bearer` header the CLI uses. Mistral has publicly confirmed third-party use of the Vibe key, including with Hermes specifically.

On top of routing, the plugin handles the wire-format details Mistral models need: reasoning-effort pass-through per model family (GLM accepts `low`/`high`/`max`, Mistral reasoning models accept `none`/`high`, non-reasoning models skip the parameter entirely to avoid HTTP 400 errors), the Vibe plan's model catalog with context windows and vision capabilities, and short model aliases (`vibe`, `fast`, `glm`).

### Models you get

| Model ID | Also available as | Context | Reasoning effort |
|---|---|---|---|
| `mistral-large-4` | `mistral-large-4-0` | 1M | `none`, `high` |
| `mistral-medium-latest` | `mistral-vibe-cli-latest` | 256K | `none`, `high` |
| `mistral-small-latest` | `mistral-vibe-cli-fast` | 256K | `none`, `high` |
| `zai-glm-5-3` | `zai-glm-latest`, `zai-glm-5` | 1M | `low`, `high`, `max` |
| `codestral-latest` | | 256K | — |

Mistral rotates the line-up occasionally; `curl https://api.mistral.ai/v1/models` with your key always lists what your plan currently includes.

---

## Prerequisites

Before installing, make sure you have:

1. **Hermes Agent** — installed and working ([NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)).
2. **A Mistral Vibe plan with coding included** — Pro, Team, or Enterprise ([mistral.ai/vibe](https://mistral.ai/vibe)).
3. **One of the following for the key:**
   - The official **Vibe CLI** installed and logged in (recommended), **or**
   - A manually copied **Vibe API Key** (no CLI needed).

---

## Step 1 — Get the plugin

```bash
git clone https://github.com/zan-keith/vibecli-hermes-plugin.git
cd vibecli-hermes-plugin
```

## Step 2 — Install it into Hermes

From inside the cloned repo:

```bash
./install.sh
```

What this does:

- Creates (if needed) `~/.hermes/plugins/model-providers/`
- Symlinks the repo as `~/.hermes/plugins/model-providers/vibe-cli-provider/`
- Refuses to clobber an existing installation at that path
- Warns you if it can't find a Vibe key

**Variants:**

```bash
./install.sh --copy        # copy files instead of symlinking (survives deleting the clone)
HERMES_HOME=/custom/path ./install.sh   # non-default Hermes home
```

**No install script?** Do it manually — the entire plugin payload is two files:

```bash
mkdir -p ~/.hermes/plugins/model-providers/vibe-cli-provider
cp plugin.yaml __init__.py ~/.hermes/plugins/model-providers/vibe-cli-provider/
```

**Alternatively**, on Hermes versions with the model-provider install-routing fix:

```bash
hermes plugins install zan-keith/vibecli-hermes-plugin
```

## Step 3 — Provide the Vibe plan key

### Option A — Vibe CLI installed (recommended, zero config)

Log in once with the official CLI:

```bash
vibe --setup
```

Pick **browser login** and sign in with your Mistral account. The CLI stores the plan key in `~/.vibe/.env`. The plugin reads it automatically at startup — you never touch the key.

> Install the CLI if needed: `curl -LsSf https://mistral.ai/vibe/install.sh | bash`

### Option B — Manual key (no Vibe CLI)

1. In the Vibe app, go to **Code → Extensions**, expand **Advanced** on the Vibe CLI card, and copy the **Vibe API Key** (the same panel shows your monthly usage and lets you rotate the key).
2. Export it:

```bash
export VIBE_API_KEY=your-key-here
```

To make it permanent, add it to your shell profile or to Hermes's own `~/.hermes/.env`:

```bash
echo 'VIBE_API_KEY=your-key-here' >> ~/.hermes/.env
```

## Step 4 — Select the provider in Hermes

**Start a fresh Hermes process** — plugin discovery runs at startup, so a Hermes that was already running won't see the new provider.

```bash
hermes model
```

In the provider list, pick **"Mistral Vibe CLI (Vibe plan quota)"**, then choose a model such as `mistral-medium-latest` or `zai-glm-5-3`.

Or set it directly in `~/.hermes/config.yaml`:

```yaml
model:
  provider: vibe-cli
  name: mistral-medium-latest
```

## Step 5 — Verify

```bash
hermes doctor
```

You should see the `vibe-cli` provider reported as configured, with key source `VIBE_API_KEY`. Then just chat as usual — every request now bills against your Vibe plan quota.

Quick smoke test from the shell:

```bash
curl https://api.mistral.ai/v1/models -H "Authorization: Bearer $(grep MISTRAL_API_KEY ~/.vibe/.env | cut -d= -f2)"
```

If that lists your plan's models, the key works.

---

## Configuration reference

| Variable | Default | Meaning |
|---|---|---|
| `VIBE_API_KEY` | auto-loaded from `~/.vibe/.env` | The Vibe plan key. Set it to override the file. |
| `MISTRAL_VIBE_API_KEY` | unset | Alternative env var, checked second. |
| `VIBE_ENV_FILE` | `~/.vibe/.env` | Where the plugin looks for the CLI's key file. |
| `HERMES_HOME` | `~/.hermes` | Hermes home; determines the plugin install path. |

## Model aliases

Inside Hermes's `/model` picker:

| Alias | Resolves to |
|---|---|
| `vibe` | `mistral-vibe-cli-latest` |
| `fast` | `mistral-vibe-cli-fast` |
| `glm` | `zai-glm-5-3` |

## Updating and removing

```bash
cd vibecli-hermes-plugin
git pull            # symlink installs pick up changes on the next Hermes restart
```

```bash
./uninstall.sh      # removes the plugin (symlink or copy)
```

## Troubleshooting

**Provider doesn't appear in `hermes model`**
- Restart Hermes completely — discovery runs at startup.
- Check the install path: `ls ~/.hermes/plugins/model-providers/vibe-cli-provider/` should show `plugin.yaml` and `__init__.py`.
- Confirm the manifest: `plugin.yaml` must contain `kind: model-provider`.

**Provider appears but isn't configured**
- Run `vibe --setup` once, or set `VIBE_API_KEY` manually.
- If `~/.vibe/.env` lives elsewhere, point the plugin at it: `export VIBE_ENV_FILE=/path/to/.env`.

**HTTP 400 on reasoning models**
- Make sure you pulled the latest plugin version — older revisions clamped reasoning efforts differently. The current version maps GLM to `low`/`high`/`max` and Mistral reasoning models to `none`/`high`.

**HTTP 401/402 — key rejected or plan budget spent**
- Rotate the key from Vibe → Code → Extensions → Advanced and update `~/.vibe/.env` or `VIBE_API_KEY`.
- 402 means the plan budget is exhausted; requests will bill pay-as-you-go only if a Studio key is also configured.

**TypeError about unexpected constructor arguments (older Hermes)**
- You're on Hermes 0.21.x or older with a pre-fix plugin revision — `git pull` the latest, which sets compatibility metadata as instance attributes.

## Terms-of-service notes

- The key comes from Mistral's own login flow and calls the same public API endpoint with the same standard header the CLI uses — nothing is scraped, impersonated, or reverse-engineered.
- Mistral has publicly confirmed third-party use of the Vibe key ("you are currently able to freely use the Vibe key with any software, including Hermes"; the Vibe plan budget is consumed before any pay-as-you-go).
- The Vibe plan is a personal/seat subscription: keep the key private, don't share it, and don't expose any proxy in front of it beyond loopback.
- Mistral can change its terms at any time; re-check them if usage patterns change.

## License

MIT — see [LICENSE](LICENSE).
