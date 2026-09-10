from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlmodel import Session, select

from app.config import get_settings
from app.db import get_session
from app.models import FindingRow, Job, Project, ScanSchedule
from app.schemas_api import ProjectCreate, ProjectRead
from app.services.targets import TargetError, validate_targets

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead)
def create_project(body: ProjectCreate, session: Session = Depends(get_session)) -> Project:
    settings = get_settings()
    cap = 4096 if settings.lab_mode else settings.max_cidr_hosts
    try:
        validate_targets(body.targets, max_targets=settings.max_targets, max_cidr_hosts=cap)
    except TargetError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    p = Project(name=body.name.strip(), targets=body.targets.strip(), environment=body.environment)
    session.add(p)
    session.commit()
    session.refresh(p)
    return p


@router.get("", response_model=list[ProjectRead])
def list_projects(session: Session = Depends(get_session)) -> list[Project]:
    stmt = select(Project).order_by(desc(Project.created_at))
    return list(session.exec(stmt))


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, session: Session = Depends(get_session)) -> Project:
    p = session.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p


@router.delete("/{project_id}")
def delete_project(project_id: int, session: Session = Depends(get_session)) -> dict[str, str]:
    p = session.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    jobs = list(session.exec(select(Job).where(Job.project_id == project_id)))
    for j in jobs:
        findings = list(session.exec(select(FindingRow).where(FindingRow.job_id == j.id)))
        for f in findings:
            session.delete(f)
        session.delete(j)
    for row in session.exec(select(ScanSchedule).where(ScanSchedule.project_id == project_id)):
        session.delete(row)
    session.delete(p)
    session.commit()
    return {"status": "deleted"}
