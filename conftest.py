"""Pytest bootstrap.

The plugin payload lives at the repository root as ``__init__.py`` (the layout
Hermes model-provider discovery expects). pytest imports that package during
collection, which pulls in ``providers`` / ``providers.base`` from Hermes.

When a Hermes checkout is on sys.path (``HERMES_SRC`` / ``PYTHONPATH``), the
real modules are used. Otherwise this conftest installs minimal stubs so the
test suite runs standalone. The per-test loader in
``tests/test_vibe_provider.py`` re-installs fresh stubs for isolation.
"""

from __future__ import annotations

import sys
import types


def _install_stubs() -> None:
    base = types.ModuleType("providers.base")

    class ProviderProfile:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    base.ProviderProfile = ProviderProfile
    providers = types.ModuleType("providers")
    providers.register_provider = lambda profile: None
    providers.base = base
    sys.modules["providers"] = providers
    sys.modules["providers.base"] = base


try:
    import providers.base  # noqa: F401
except ModuleNotFoundError:
    _install_stubs()
