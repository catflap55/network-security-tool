from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlmodel import Session, select

from app.db import get_session
from app.models import FindingRow, Job, Project
from app.schemas_api import ProjectCreate, ProjectRead

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead)
def create_project(body: ProjectCreate, session: Session = Depends(get_session)) -> Project:
    p = Project(name=body.name, targets=body.targets, environment=body.environment)
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
    session.delete(p)
    session.commit()
    return {"status": "deleted"}
