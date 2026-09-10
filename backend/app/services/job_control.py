"""In-memory cancel flags and active subprocess handles (per API process)."""

from __future__ import annotations

import subprocess
import threading

_LOCK = threading.Lock()
_CANCEL_REQUESTED: set[int] = set()
_ACTIVE_PROCS: dict[int, subprocess.Popen] = {}


def request_job_cancel(job_id: int) -> None:
    with _LOCK:
        _CANCEL_REQUESTED.add(job_id)
        proc = _ACTIVE_PROCS.get(job_id)
    if proc is not None:
        try:
            proc.kill()
        except OSError:
            pass


def is_cancel_requested(job_id: int) -> bool:
    with _LOCK:
        return job_id in _CANCEL_REQUESTED


def register_active_proc(job_id: int, proc: subprocess.Popen) -> None:
    with _LOCK:
        _ACTIVE_PROCS[job_id] = proc


def unregister_active_proc(job_id: int) -> None:
    with _LOCK:
        _ACTIVE_PROCS.pop(job_id, None)


def clear_cancel(job_id: int) -> None:
    with _LOCK:
        _CANCEL_REQUESTED.discard(job_id)
