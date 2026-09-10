from __future__ import annotations

import json
from typing import Any

from sqlmodel import Session, select

from app.models import FindingRow


def _key(row: FindingRow) -> tuple[str, str, str]:
    return (row.target, row.remediation_key, row.title)


def diff_jobs(session: Session, old_job_id: int, new_job_id: int) -> dict[str, Any]:
    old_rows = list(session.exec(select(FindingRow).where(FindingRow.job_id == old_job_id)))
    new_rows = list(session.exec(select(FindingRow).where(FindingRow.job_id == new_job_id)))
    old_map = {_key(r): r for r in old_rows}
    new_map = {_key(r): r for r in new_rows}
    added = [new_map[k] for k in new_map.keys() - old_map.keys()]
    removed = [old_map[k] for k in old_map.keys() - new_map.keys()]
    unchanged = [new_map[k] for k in new_map.keys() & old_map.keys()]

    def slim(r: FindingRow) -> dict[str, Any]:
        return {
            "finding_id": r.finding_id,
            "severity": r.severity,
            "title": r.title,
            "target": r.target,
            "remediation_key": r.remediation_key,
            "plugin_id": r.plugin_id,
        }

    return {
        "old_job_id": old_job_id,
        "new_job_id": new_job_id,
        "added": [slim(r) for r in added],
        "removed": [slim(r) for r in removed],
        "unchanged_count": len(unchanged),
        "summary": (
            f"{len(added)} new finding(s), {len(removed)} gone, "
            f"{len(unchanged)} unchanged."
        ),
    }
