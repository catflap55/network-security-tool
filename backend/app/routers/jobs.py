from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import desc
from sqlmodel import Session, select

from app.db import get_session
from app.models import FindingRow, Job, Project
from app.schemas_api import FindingRead, JobCreate, JobRead
from app.services.job_control import request_job_cancel
from app.services.job_runner import start_job_background
from app.services.settings_store import get_authorization_acknowledged

router = APIRouter(prefix="/projects", tags=["jobs"])


def _job_to_read(job: Job) -> JobRead:
    return JobRead.model_validate(job)


@router.post("/{project_id}/jobs", response_model=JobRead)
def start_job(
    project_id: int,
    body: JobCreate,
    session: Session = Depends(get_session),
) -> JobRead:
    if not get_authorization_acknowledged(session):
        raise HTTPException(
            status_code=403,
            detail="Authorization not acknowledged. Enable it in Settings before scanning.",
        )

    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    job = Job(project_id=project_id, plugin_id=body.plugin_id, status="pending")
    session.add(job)
    session.commit()
    session.refresh(job)

    start_job_background(job.id, project_id)
    session.refresh(job)
    return _job_to_read(job)


@router.get("/{project_id}/jobs", response_model=list[JobRead])
def list_jobs(project_id: int, session: Session = Depends(get_session)) -> list[Job]:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    stmt = select(Job).where(Job.project_id == project_id).order_by(desc(Job.id))
    return list(session.exec(stmt))


@router.get("/{project_id}/jobs/{job_id}", response_model=JobRead)
def get_job(project_id: int, job_id: int, session: Session = Depends(get_session)) -> Job:
    job = session.get(Job, job_id)
    if not job or job.project_id != project_id:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{project_id}/jobs/{job_id}/cancel", response_model=JobRead)
def cancel_job(
    project_id: int,
    job_id: int,
    session: Session = Depends(get_session),
) -> Job:
    job = session.get(Job, job_id)
    if not job or job.project_id != project_id:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in ("pending", "running"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job status is '{job.status}'; only pending or running jobs can be stopped.",
        )
    request_job_cancel(job_id)
    session.refresh(job)
    return job


@router.get("/{project_id}/jobs/{job_id}/findings", response_model=list[FindingRead])
def list_findings(project_id: int, job_id: int, session: Session = Depends(get_session)) -> list[FindingRead]:
    job = session.get(Job, job_id)
    if not job or job.project_id != project_id:
        raise HTTPException(status_code=404, detail="Job not found")
    stmt = select(FindingRow).where(FindingRow.job_id == job_id)
    rows = list(session.exec(stmt))
    out: list[FindingRead] = []
    for r in rows:
        evidence = json.loads(r.evidence_json) if r.evidence_json else {}
        out.append(
            FindingRead(
                finding_id=r.finding_id,
                severity=r.severity,
                title=r.title,
                description=r.description,
                remediation_key=r.remediation_key,
                plugin_id=r.plugin_id,
                target=r.target,
                evidence=evidence,
                first_seen=r.created_at,
            )
        )
    return out


def _severity_to_sarif_level(sev: str) -> str:
    if sev in ("critical", "high"):
        return "error"
    if sev == "medium":
        return "warning"
    if sev == "low":
        return "note"
    return "note"


@router.get("/{project_id}/jobs/{job_id}/export.json")
def export_json(project_id: int, job_id: int, session: Session = Depends(get_session)) -> JSONResponse:
    job = session.get(Job, job_id)
    if not job or job.project_id != project_id:
        raise HTTPException(status_code=404, detail="Job not found")
    stmt = select(FindingRow).where(FindingRow.job_id == job_id)
    rows = list(session.exec(stmt))
    payload: list[dict[str, Any]] = []
    for r in rows:
        payload.append(
            {
                "finding_id": r.finding_id,
                "severity": r.severity,
                "title": r.title,
                "description": r.description,
                "remediation_key": r.remediation_key,
                "plugin_id": r.plugin_id,
                "target": r.target,
                "evidence": json.loads(r.evidence_json) if r.evidence_json else {},
            }
        )
    return JSONResponse({"job_id": job_id, "plugin_id": job.plugin_id, "findings": payload})


@router.get("/{project_id}/jobs/{job_id}/export.sarif")
def export_sarif(project_id: int, job_id: int, session: Session = Depends(get_session)) -> PlainTextResponse:
    job = session.get(Job, job_id)
    if not job or job.project_id != project_id:
        raise HTTPException(status_code=404, detail="Job not found")
    stmt = select(FindingRow).where(FindingRow.job_id == job_id)
    rows = list(session.exec(stmt))

    results: list[dict[str, Any]] = []
    for i, r in enumerate(rows):
        results.append(
            {
                "ruleId": r.remediation_key,
                "level": _severity_to_sarif_level(r.severity),
                "message": {"text": r.title + ("\n" + r.description if r.description else "")},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": f"network://{r.target}"},
                        }
                    }
                ],
                "properties": {
                    "finding_id": r.finding_id,
                    "plugin_id": r.plugin_id,
                    "evidence": json.loads(r.evidence_json) if r.evidence_json else {},
                },
            }
        )

    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Security Console",
                        "informationUri": "https://example.local/security-console",
                        "rules": [],
                    }
                },
                "results": results,
            }
        ],
    }
    return PlainTextResponse(json.dumps(sarif, indent=2), media_type="application/json")
