"""Pydantic models aligned with schemas/finding.schema.json."""

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class NormalizedFinding(BaseModel):
    finding_id: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    title: str
    description: str = ""
    remediation_key: str
    plugin_id: str
    target: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    first_seen: Optional[datetime] = None

    model_config = {"extra": "forbid"}
