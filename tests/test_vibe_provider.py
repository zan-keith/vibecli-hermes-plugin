"""Tests for the Vibe CLI provider plugin.

Most tests are standalone: they stub the Hermes provider-registry imports so no
Hermes checkout is required. Set HERMES_SRC to a Hermes Agent checkout to run
against the real runtime instead.

    HERMES_SRC=/path/to/hermes-agent python3 -m pytest tests/ -v
"""

from __future__ import annotations

import importlib
import os
import sys
import types
from pathlib import Path

import pytest

PLUGIN_DIR = Path(__file__).resolve().parent.parent


class FakeBase:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def _load_plugin(monkeypatch, tmp_path, env_file_content=None, extra_env=None):
    """Import the plugin with a stubbed Hermes provider registry."""
    fake_providers = types.ModuleType("providers")
    registered = []
    fake_providers.register_provider = lambda profile: registered.append(profile)
    fake_base = types.ModuleType("providers.base")
    fake_base.ProviderProfile = FakeBase
    fake_providers.base = fake_base

    env_file = tmp_path / ".env"
    if env_file_content is not None:
        env_file.write_text(env_file_content, encoding="utf-8")

    monkeypatch.setenv("VIBE_ENV_FILE", str(env_file))
    for var in ("VIBE_API_KEY", "MISTRAL_VIBE_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    for key, value in (extra_env or {}).items():
        monkeypatch.setenv(key, value)

    sys.modules.pop("providers", None)
    sys.modules.pop("providers.base", None)
    sys.modules.setdefault("providers", fake_providers)
    sys.modules.setdefault("providers.base", fake_base)

    spec = importlib.util.spec_from_file_location("vibe_plugin_test", PLUGIN_DIR / "__init__.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, registered


def test_registers_vibe_cli_profile(monkeypatch, tmp_path):
    _, registered = _load_plugin(monkeypatch, tmp_path)
    assert len(registered) == 1
    profile = registered[0]
    assert profile.name == "vibe-cli"
    assert "vibe" in profile.aliases
    assert "mistral-vibe" in profile.aliases
    assert profile.base_url == "https://api.mistral.ai/v1"
    assert "VIBE_API_KEY" in profile.env_vars


def test_reads_key_from_vibe_env_file(monkeypatch, tmp_path):
    _, registered = _load_plugin(
        monkeypatch, tmp_path, env_file_content="MISTRAL_API_KEY=vibe-key-xyz\n"
    )
    assert os.environ.get("VIBE_API_KEY") == "vibe-key-xyz"


def test_env_file_missing_is_tolerated(monkeypatch, tmp_path):
    _, registered = _load_plugin(monkeypatch, tmp_path, env_file_content=None)
    assert os.environ.get("VIBE_API_KEY") is None


def test_explicit_env_var_not_overwritten(monkeypatch, tmp_path):
    _, _ = _load_plugin(
        monkeypatch,
        tmp_path,
        env_file_content="MISTRAL_API_KEY=file-key\n",
        extra_env={"VIBE_API_KEY": "explicit-key"},
    )
    assert os.environ.get("VIBE_API_KEY") == "explicit-key"


def test_env_file_comments_and_quotes(monkeypatch, tmp_path):
    _, _ = _load_plugin(
        monkeypatch,
        tmp_path,
        env_file_content='# comment\nOTHER=x\nMISTRAL_API_KEY="quoted-key"\n',
    )
    assert os.environ.get("VIBE_API_KEY") == "quoted-key"


@pytest.mark.parametrize(
    "model,effort,expected",
    [
        ("zai-glm-5-3", "high", "high"),
        ("zai-glm-5-3", "max", "max"),
        ("zai-glm-5-3", "medium", "low"),
        ("zai-glm-5-3", "none", "low"),
        ("mistral-medium-latest", "high", "high"),
        ("mistral-medium-latest", "medium", "high"),
        ("mistral-small-latest", "low", "high"),
        ("mistral-large-4", "minimal", "high"),
        ("mistral-vibe-cli-latest", "medium", "high"),
    ],
)
def test_reasoning_effort_mapping(monkeypatch, tmp_path, model, effort, expected):
    module, registered = _load_plugin(monkeypatch, tmp_path)
    profile = registered[0]
    extra_body, top_level = profile.build_api_kwargs_extras(
        reasoning_config={"effort": effort}, model=model
    )
    assert top_level == {"reasoning_effort": expected}
    assert extra_body == {}


@pytest.mark.parametrize(
    "model",
    [
        "codestral-latest",
        "devstral-2-latest",
        "ministral-8b-latest",
        "pixtral-12b-latest",
        "voxtral-small-latest",
        "unknown-model",
        None,
        "",
    ],
)
def test_non_reasoning_models_skip_param(monkeypatch, tmp_path, model):
    module, registered = _load_plugin(monkeypatch, tmp_path)
    profile = registered[0]
    extra_body, top_level = profile.build_api_kwargs_extras(
        reasoning_config={"effort": "high"}, model=model
    )
    assert top_level == {}
    assert extra_body == {}


def test_no_reasoning_config_is_noop(monkeypatch, tmp_path):
    _, registered = _load_plugin(monkeypatch, tmp_path)
    profile = registered[0]
    extra_body, top_level = profile.build_api_kwargs_extras(
        reasoning_config=None, model="zai-glm-5-3"
    )
    assert top_level == {}
    assert extra_body == {}


def test_fallback_models_are_tool_capable_catalog(monkeypatch, tmp_path):
    _, registered = _load_plugin(monkeypatch, tmp_path)
    profile = registered[0]
    for model in ("mistral-medium-latest", "mistral-small-latest", "zai-glm-5-3"):
        assert model in profile.fallback_models
    assert profile.default_aux_model == "mistral-small-latest"
    assert profile.supports_vision is True
