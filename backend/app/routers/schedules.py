from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Project, ScanSchedule
from app.plugins.registry import get_plugin
from app.schemas_api import ScheduleCreate, ScheduleRead

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("", response_model=list[ScheduleRead])
def list_schedules(session: Session = Depends(get_session)) -> list[ScanSchedule]:
    return list(session.exec(select(ScanSchedule)))


@router.post("", response_model=ScheduleRead)
def create_schedule(body: ScheduleCreate, session: Session = Depends(get_session)) -> ScanSchedule:
    project = session.get(Project, body.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if get_plugin(body.plugin_id) is None:
        raise HTTPException(status_code=400, detail="Unknown or locked plugin.")
    hours = max(1, min(body.interval_hours, 24 * 30))
    row = ScanSchedule(
        project_id=body.project_id,
        plugin_id=body.plugin_id,
        interval_hours=hours,
        enabled=body.enabled,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, session: Session = Depends(get_session)) -> dict[str, str]:
    row = session.get(ScanSchedule, schedule_id)
    if not row:
        raise HTTPException(status_code=404, detail="Schedule not found")
    session.delete(row)
    session.commit()
    return {"status": "deleted"}
