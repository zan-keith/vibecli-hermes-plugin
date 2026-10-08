"""Mistral Vibe CLI provider profile.

Routes Hermes requests through the Mistral Vibe plan key: the same key the
official Vibe CLI stores in ``~/.vibe/.env`` after ``vibe --setup``. Requests
go to the official Mistral API (``https://api.mistral.ai/v1``) and are billed
against the Vibe plan's quota, not pay-as-you-go Studio credits.

Setup is zero-config when the Vibe CLI is installed: the plugin reads the key
from ``~/.vibe/.env`` at import time and exposes it as ``VIBE_API_KEY``.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from providers import register_provider
from providers.base import ProviderProfile

VIBE_ENV_FILE = Path(os.environ.get("VIBE_ENV_FILE", "")).expanduser() if os.environ.get("VIBE_ENV_FILE") else Path.home() / ".vibe" / ".env"
_BASE_URL = "https://api.mistral.ai/v1"

# Reasoning-capable models on the Vibe plan (per Mistral docs, Oct 2026).
_GLM_MODELS = frozenset({"zai-glm-5-3", "zai-glm-latest", "zai-glm-5"})
_ALWAYS_REASONING = _GLM_MODELS | frozenset({
    "mistral-medium-latest", "mistral-vibe-cli-latest",
    "mistral-small-latest", "mistral-vibe-cli-fast",
    "mistral-large-4", "mistral-large-4-0",
})
_NON_REASONING_FAMILIES = (
    "codestral", "devstral", "ministral", "pixtral", "voxtral",
    "mistral-ocr", "mistral-moderation", "mistral-tiny", "open-mistral",
)
_VERSION_PATTERN = re.compile(r"-(\d{4})(?:[-.]|$)")
_EFFORT_HIGH_NONE_ONLY = frozenset({
    "mistral-medium-latest", "mistral-vibe-cli-latest",
    "mistral-small-latest", "mistral-vibe-cli-fast",
    "mistral-large-4", "mistral-large-4-0",
})


def _load_vibe_key() -> str:
    """Read MISTRAL_API_KEY from the Vibe CLI's env file, if present."""
    try:
        text = VIBE_ENV_FILE.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or "=" not in stripped:
            continue
        name, _, value = stripped.partition("=")
        if name.strip() == "MISTRAL_API_KEY":
            return value.strip().strip("\"'")
    return ""


def _maybe_export_vibe_key() -> None:
    key = _load_vibe_key()
    if key:
        os.environ.setdefault("VIBE_API_KEY", key)


_maybe_export_vibe_key()


def _model_supports_reasoning(model: str | None) -> bool:
    m = (model or "").strip().lower()
    if not m or m.startswith(_NON_REASONING_FAMILIES):
        return False
    if m in _ALWAYS_REASONING:
        return True
    match = _VERSION_PATTERN.search(m)
    if not match:
        return False
    family = m[:match.start()].rstrip("-")
    thresholds = {"mistral-small": 2603, "mistral-medium": 2604, "mistral-large": 2600}
    threshold = thresholds.get(family)
    return threshold is not None and int(match.group(1)) >= threshold


class VibeProfile(ProviderProfile):
    """Mistral Vibe CLI plan key on the official Mistral API."""

    def build_api_kwargs_extras(
        self,
        *,
        reasoning_config: dict | None = None,
        model: str | None = None,
        **context: Any,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        extra_body: dict[str, Any] = {}
        top_level: dict[str, Any] = {}

        if not _model_supports_reasoning(model):
            return extra_body, top_level

        if isinstance(reasoning_config, dict):
            effort = (reasoning_config.get("effort") or "").strip().lower()
            if effort:
                m = (model or "").strip().lower()
                if m in _GLM_MODELS:
                    effort = {
                        "none": "low", "low": "low", "medium": "low",
                        "high": "high", "max": "max",
                    }.get(effort, "low")
                elif m in _EFFORT_HIGH_NONE_ONLY and effort in ("low", "medium", "minimal"):
                    effort = "high"
                top_level["reasoning_effort"] = effort

        return extra_body, top_level


vibe = VibeProfile(
    name="vibe-cli",
    aliases=("vibe", "mistral-vibe", "vibe-cli-provider"),
    env_vars=("VIBE_API_KEY", "MISTRAL_VIBE_API_KEY"),
    display_name="Mistral Vibe CLI (Vibe plan quota)",
    description="Mistral API via your Vibe CLI plan key — uses the Vibe subscription quota",
    signup_url="https://mistral.ai/vibe",
    base_url=_BASE_URL,
    fallback_models=(
        "mistral-medium-latest",
        "mistral-small-latest",
        "zai-glm-5-3",
        "mistral-large-4",
        "codestral-latest",
    ),
    supports_vision=True,
    default_aux_model="mistral-small-latest",
)

# Hermes 0.21.x keeps compatibility metadata as instance attributes rather
# than ProviderProfile constructor arguments. Assigning these after
# construction also remains compatible with newer runtimes that consume the
# same metadata attributes.
vibe.__dict__["model_aliases"] = {
    "vibe": "mistral-vibe-cli-latest",
    "fast": "mistral-vibe-cli-fast",
    "glm": "zai-glm-5-3",
}
vibe.__dict__["model_capabilities"] = {
    "mistral-large-4": {"supports_tools": True, "supports_vision": True, "context_window": 1_000_000},
    "zai-glm-5-3": {"supports_tools": True, "context_window": 1_000_000},
    "mistral-medium-latest": {"supports_tools": True, "supports_vision": True, "context_window": 256_000},
    "mistral-small-latest": {"supports_tools": True, "supports_vision": True, "context_window": 256_000},
    "codestral-latest": {"supports_tools": True, "context_window": 256_000},
}

register_provider(vibe)
