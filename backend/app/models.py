from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    targets: str = Field(sa_column=Column(Text))  # comma-separated CIDR/hosts
    environment: str = Field(default="mixed")  # home | lab | office | mixed
    created_at: datetime = Field(default_factory=utcnow)


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    plugin_id: str = Field(index=True)
    status: str = Field(default="pending")  # pending | running | completed | failed
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    log_text: str = Field(default="", sa_column=Column(Text))
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    artifact_dir: Optional[str] = None


class FindingRow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id", index=True)
    finding_id: str = Field(index=True)
    severity: str
    title: str
    description: str = Field(default="", sa_column=Column(Text))
    remediation_key: str = Field(index=True)
    plugin_id: str
    target: str = Field(index=True)
    evidence_json: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=utcnow)


class SettingKV(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str = Field(sa_column=Column(Text))
