from fastapi import APIRouter, HTTPException

from app.schemas_api import PlaybookRead
from app.services.playbooks import get_playbook_markdown

router = APIRouter(prefix="/playbooks", tags=["playbooks"])


@router.get("/{remediation_key}", response_model=PlaybookRead)
def get_playbook(remediation_key: str) -> PlaybookRead:
    md = get_playbook_markdown(remediation_key)
    if md is None:
        raise HTTPException(status_code=404, detail="Unknown remediation key")
    return PlaybookRead(remediation_key=remediation_key, markdown=md)
