from fastapi import APIRouter

from app.plugins.registry import plugin_catalog
from app.schemas_api import PluginInfo

router = APIRouter(prefix="/plugins", tags=["plugins"])


@router.get("", response_model=list[PluginInfo])
def list_plugins() -> list[PluginInfo]:
    """Every wired scanner; `available=false` means it is hidden from runs until requirements are met."""
    return [
        PluginInfo(
            id=p.id,
            display_name=p.display_name,
            description=p.description,
            requires_lab_mode=p.requires_lab_mode,
            impact_summary=p.impact_summary,
            available=ok,
            unavailable_reason=reason,
        )
        for p, ok, reason in plugin_catalog()
    ]
