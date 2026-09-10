from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.config import get_settings
from app.db import get_session
from app.schemas_api import SettingsRead, SettingsUpdate
from app.services.settings_store import get_authorization_acknowledged, set_authorization_acknowledged

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsRead)
def read_settings(session: Session = Depends(get_session)) -> SettingsRead:
    s = get_settings()
    return SettingsRead(
        authorization_acknowledged=get_authorization_acknowledged(session),
        lab_mode_enabled=s.lab_mode,
        bind_host=s.host,
        token_required=True,
    )


@router.put("", response_model=SettingsRead)
def update_settings(
    body: SettingsUpdate,
    session: Session = Depends(get_session),
) -> SettingsRead:
    set_authorization_acknowledged(session, body.authorization_acknowledged)
    return read_settings(session)
