from __future__ import annotations

import threading
import time
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.config import get_settings
from app.db import engine
from app.models import Job, ScanSchedule
from app.services.job_runner import start_job_background
from app.services.settings_store import get_authorization_acknowledged

_started = False


def _due(row: ScanSchedule, now: datetime) -> bool:
    if not row.enabled:
        return False
    if row.last_run_at is None:
        return True
    last = row.last_run_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return now - last >= timedelta(hours=max(row.interval_hours, 1))


def scheduler_loop() -> None:
    while True:
        time.sleep(60)
        now = datetime.now(timezone.utc)
        try:
            with Session(engine) as session:
                if not get_authorization_acknowledged(session):
                    continue
                running = list(session.exec(select(Job).where(Job.status == "running")))
                pending = list(session.exec(select(Job).where(Job.status == "pending")))
                if len(running) + len(pending) >= get_settings().max_concurrent_jobs:
                    continue
                rows = list(session.exec(select(ScanSchedule)))
                for row in rows:
                    if not _due(row, now):
                        continue
                    job = Job(project_id=row.project_id, plugin_id=row.plugin_id, status="pending")
                    session.add(job)
                    row.last_run_at = now
                    session.add(row)
                    session.commit()
                    session.refresh(job)
                    start_job_background(job.id, row.project_id)
                    break
        except Exception:
            continue


def start_scheduler() -> None:
    global _started
    if _started:
        return
    _started = True
    threading.Thread(target=scheduler_loop, daemon=True, name="scan-scheduler").start()
