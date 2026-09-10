from __future__ import annotations

import json
import subprocess
import threading
import time
from datetime import datetime, timezone

from sqlmodel import Session

from app.config import get_settings, resolve_nmap_path
from app.db import engine
from app.models import FindingRow, Job, Project
from app.plugins.registry import get_plugin
from app.schemas_finding import NormalizedFinding
from app.services.job_control import (
    clear_cancel,
    is_cancel_requested,
    register_active_proc,
    unregister_active_proc,
)
from app.services.targets import TargetError, validate_targets


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _update_job_log(job_id: int, text: str) -> None:
    """Best-effort live log while nmap runs (separate session / thread)."""
    try:
        with Session(engine) as session:
            j = session.get(Job, job_id)
            if j is None or j.status != "running":
                return
            j.log_text = text
            session.add(j)
            session.commit()
    except Exception:
        pass


def _finalize_cancelled(
    session: Session,
    job: Job,
    *,
    log_body: str,
) -> None:
    job.status = "cancelled"
    job.finished_at = utcnow()
    job.error_message = "Stopped by operator."
    job.log_text = log_body
    session.add(job)
    session.commit()


def start_job_background(job_id: int, project_id: int) -> None:
    def worker() -> None:
        with Session(engine) as session:
            job = session.get(Job, job_id)
            project = session.get(Project, project_id)
            if job is None or project is None:
                return
            try:
                run_job_sync(session, job, project)
            finally:
                clear_cancel(job_id)

    threading.Thread(target=worker, daemon=True, name=f"scan-job-{job_id}").start()


def run_job_sync(session: Session, job: Job, project: Project) -> None:
    settings = get_settings()
    plugin = get_plugin(job.plugin_id)
    if plugin is None:
        job.status = "failed"
        job.finished_at = utcnow()
        job.error_message = (
            f"Unknown or unavailable plugin: {job.plugin_id}. "
            "If it appears as locked in the UI, enable LAB_MODE or check /plugins for the reason."
        )
        session.add(job)
        session.commit()
        _persist_findings(
            session,
            job.id,
            [
                NormalizedFinding(
                    finding_id="unsupported-plugin",
                    severity="low",
                    title="Unsupported plugin",
                    description=job.error_message or "",
                    remediation_key="UNSUPPORTED_PLUGIN",
                    plugin_id=job.plugin_id,
                    target="*",
                    evidence={"plugin_id": job.plugin_id},
                    first_seen=utcnow(),
                )
            ],
        )
        return

    if plugin.requires_lab_mode and not settings.lab_mode:
        job.status = "failed"
        job.finished_at = utcnow()
        job.error_message = "Plugin requires LAB_MODE=true on the server."
        session.add(job)
        session.commit()
        return

    if is_cancel_requested(job.id):
        _finalize_cancelled(session, job, log_body="Cancelled before scan started.\n")
        return

    settings = get_settings()
    cap = 4096 if settings.lab_mode else settings.max_cidr_hosts
    try:
        validate_targets(project.targets, max_targets=settings.max_targets, max_cidr_hosts=cap)
    except TargetError as exc:
        job.status = "failed"
        job.finished_at = utcnow()
        job.error_message = str(exc)
        session.add(job)
        session.commit()
        return

    artifact_root = settings.data_dir / "artifacts" / str(job.id)
    artifact_root.mkdir(parents=True, exist_ok=True)
    job.artifact_dir = str(artifact_root)
    job.status = "running"
    job.started_at = utcnow()
    job.log_text = "Starting scan…\n"
    session.add(job)
    session.commit()

    if is_cancel_requested(job.id):
        _finalize_cancelled(session, job, log_body=job.log_text + "Cancelled.\n")
        return

    if not plugin.uses_subprocess:
        try:
            findings, log_body = plugin.run_in_process(project, artifact_root)
            job.log_text = log_body
            if is_cancel_requested(job.id):
                _finalize_cancelled(session, job, log_body=log_body + "\n— stopped by operator —\n")
                return
            _persist_findings(session, job.id, findings)
            job.status = "completed"
            job.error_message = None
            job.finished_at = utcnow()
            session.add(job)
            session.commit()
        except Exception as e:  # noqa: BLE001
            job.status = "failed"
            job.error_message = str(e)
            job.log_text = str(e)
            job.finished_at = utcnow()
            session.add(job)
            session.commit()
        return

    nmap_exe = resolve_nmap_path()
    cmd = plugin.build_command(project, nmap_exe)
    log_prefix = f"$ {' '.join(cmd)}\n"

    xml_path = artifact_root / "nmap.xml"
    err_path = artifact_root / "nmap_stderr.txt"

    proc: subprocess.Popen | None = None
    stopped_by_user = False

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        register_active_proc(job.id, proc)
        stderr_acc: list[bytes] = []

        def read_stderr() -> None:
            try:
                if proc.stderr is None:
                    return
                for line in iter(proc.stderr.readline, b""):
                    stderr_acc.append(line)
            except Exception:
                pass

        threading.Thread(target=read_stderr, daemon=True).start()

        deadline = time.monotonic() + settings.job_timeout_seconds
        timed_out = False
        while proc.poll() is None:
            if is_cancel_requested(job.id):
                stopped_by_user = True
                proc.kill()
                try:
                    proc.wait(timeout=120)
                except Exception:
                    pass
                break
            if time.monotonic() > deadline:
                timed_out = True
                proc.kill()
                try:
                    proc.wait(timeout=120)
                except Exception:
                    pass
                break
            body = b"".join(stderr_acc).decode(errors="replace")
            _update_job_log(job.id, log_prefix + body + "\n— scan running —\n")
            time.sleep(0.45)

        stdout = (proc.stdout.read() if proc.stdout else b"") or b""
        stderr = b"".join(stderr_acc)
        xml_path.write_bytes(stdout)
        err_path.write_bytes(stderr)
        rc = proc.returncode if proc.returncode is not None else -1

        log_parts = [log_prefix]
        if stderr:
            log_parts.append(stderr.decode(errors="replace"))
        log_parts.append(f"\nexit_code={rc}\n")
        full_log = "".join(log_parts)

        if stopped_by_user or is_cancel_requested(job.id):
            _finalize_cancelled(
                session,
                job,
                log_body=full_log + "\n— stopped by operator —\n",
            )
            return

        job.log_text = full_log

        if timed_out:
            job.status = "failed"
            job.error_message = f"Job timed out after {settings.job_timeout_seconds}s"
            job.log_text += "\n(process killed after timeout)\n"
        elif rc != 0:
            job.status = "failed"
            job.error_message = f"scanner exited with code {rc}"
        else:
            job.status = "completed"
            job.error_message = None

        findings = plugin.parse_output(stdout)
        _persist_findings(session, job.id, findings)
        job.finished_at = utcnow()
        session.add(job)
        session.commit()

    except FileNotFoundError:
        job.status = "failed"
        job.error_message = (
            f"Executable not found: {cmd[0]!r}. "
            "Install Nmap, add its folder to PATH, or set NMAP_PATH to the full path of nmap.exe "
            r'(typical: C:\Program Files (x86)\Nmap\nmap.exe). Restart the API after changing env.'
        )
        job.log_text = log_prefix + job.error_message
        job.finished_at = utcnow()
        session.add(job)
        session.commit()
    except Exception as e:  # noqa: BLE001
        job.status = "failed"
        job.error_message = str(e)
        job.log_text = log_prefix + f"\n{e!s}\n"
        job.finished_at = utcnow()
        session.add(job)
        session.commit()
    finally:
        if proc is not None:
            unregister_active_proc(job.id)


def _persist_findings(session: Session, job_id: int, findings: list[NormalizedFinding]) -> None:
    for f in findings:
        row = FindingRow(
            job_id=job_id,
            finding_id=f.finding_id,
            severity=f.severity,
            title=f.title,
            description=f.description,
            remediation_key=f.remediation_key,
            plugin_id=f.plugin_id,
            target=f.target,
            evidence_json=json.dumps(f.evidence, default=str),
        )
        session.add(row)
    session.commit()


