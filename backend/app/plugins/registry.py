from __future__ import annotations

from typing import Optional

from app.config import get_settings
from app.plugins.base import ScanPlugin
from app.plugins.http_headers_plugin import HttpHeadersPlugin
from app.plugins.nmap_plugins import (
    LabDiscoveryPlugin,
    NmapQuickPlugin,
    NmapSafeFullPlugin,
)
from app.plugins.tls_plugin import TlsInspectPlugin

_ALWAYS: list[ScanPlugin] = [
    NmapQuickPlugin(),
    NmapSafeFullPlugin(),
    TlsInspectPlugin(),
    HttpHeadersPlugin(),
]


def plugin_catalog() -> list[tuple[ScanPlugin, bool, str | None]]:
    s = get_settings()
    entries: list[tuple[ScanPlugin, bool, str | None]] = [(p, True, None) for p in _ALWAYS]
    lab = LabDiscoveryPlugin()
    if s.lab_mode:
        entries.append((lab, True, None))
    else:
        entries.append(
            (
                lab,
                False,
                "Set LAB_MODE=true on the API and restart for lab-only host discovery.",
            )
        )
    return entries


def all_plugins() -> list[ScanPlugin]:
    return [p for p, ok, _ in plugin_catalog() if ok]


def get_plugin(plugin_id: str) -> Optional[ScanPlugin]:
    for p, ok, _ in plugin_catalog():
        if p.id == plugin_id and ok:
            return p
    return None
