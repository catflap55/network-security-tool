from __future__ import annotations

from typing import Optional

from app.config import get_settings
from app.plugins.base import ScanPlugin
from app.plugins.nmap_plugins import (
    LabAggressivePlaceholderPlugin,
    NmapQuickPlugin,
    NmapSafeFullPlugin,
)

_BASE_PLUGINS: list[ScanPlugin] = [
    NmapQuickPlugin(),
    NmapSafeFullPlugin(),
]


def plugin_catalog() -> list[tuple[ScanPlugin, bool, str | None]]:
    """All wired plugins: (plugin, available_for_use, reason_if_unavailable)."""
    s = get_settings()
    entries: list[tuple[ScanPlugin, bool, str | None]] = [
        (p, True, None) for p in _BASE_PLUGINS
    ]
    lab = LabAggressivePlaceholderPlugin()
    if s.lab_mode:
        entries.append((lab, True, None))
    else:
        entries.append(
            (
                lab,
                False,
                "Set environment variable LAB_MODE=true on the API process and restart "
                "(see docs/AUTO_FIX_POLICY.md).",
            ),
        )
    return entries


def all_plugins() -> list[ScanPlugin]:
    """Plugins that can be run now (same as before)."""
    return [p for p, ok, _ in plugin_catalog() if ok]


def get_plugin(plugin_id: str) -> Optional[ScanPlugin]:
    for p, ok, _ in plugin_catalog():
        if p.id == plugin_id and ok:
            return p
    return None
