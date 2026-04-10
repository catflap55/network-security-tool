from sqlmodel import Session

from app.models import SettingKV

AUTH_KEY = "authorization_acknowledged"


def get_authorization_acknowledged(session: Session) -> bool:
    row = session.get(SettingKV, AUTH_KEY)
    if row is None:
        return False
    return row.value.lower() in ("1", "true", "yes")


def set_authorization_acknowledged(session: Session, value: bool) -> None:
    row = session.get(SettingKV, AUTH_KEY)
    v = "true" if value else "false"
    if row is None:
        session.add(SettingKV(key=AUTH_KEY, value=v))
    else:
        row.value = v
    session.commit()
