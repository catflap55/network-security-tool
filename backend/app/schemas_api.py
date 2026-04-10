from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str
    targets: str
    environment: str = "mixed"


class ProjectRead(BaseModel):
    id: int
    name: str
    targets: str
    environment: str
    created_at: datetime

    model_config = {"from_attributes": True}


class JobCreate(BaseModel):
    plugin_id: str


class JobRead(BaseModel):
    id: int
    project_id: int
    plugin_id: str
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    log_text: str = ""
    error_message: Optional[str] = None
    artifact_dir: Optional[str] = None

    model_config = {"from_attributes": True}


class FindingRead(BaseModel):
    finding_id: str
    severity: str
    title: str
    description: str = ""
    remediation_key: str
    plugin_id: str
    target: str
    evidence: dict[str, Any]
    first_seen: Optional[datetime] = None


class SettingsRead(BaseModel):
    authorization_acknowledged: bool
    lab_mode_enabled: bool


class SettingsUpdate(BaseModel):
    authorization_acknowledged: bool


class PluginInfo(BaseModel):
    id: str
    display_name: str
    description: str
    requires_lab_mode: bool
    impact_summary: str
    available: bool = True
    unavailable_reason: Optional[str] = None


class PlaybookRead(BaseModel):
    remediation_key: str
    markdown: str
