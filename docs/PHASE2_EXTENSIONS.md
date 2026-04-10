# Phase 2 extension points

This document describes how to extend the console beyond MVP without rewriting the core.

## Plugin interface

Plugins implement:

- `id`, `display_name`, `description`
- `requires_lab_mode: bool`
- `impact_summary: str` — shown before job start
- `build_command(project, extra_args) -> list[str]`
- `parse_output(raw_paths, job_meta) -> list[NormalizedFinding]`

Register new plugins in `backend/app/plugins/registry.py` (or equivalent).

## Nuclei (planned)

- **Binary**: `nuclei` on PATH; templates directory pinned via env `NUCLEI_TEMPLATES_DIR`.
- **Command pattern**: `nuclei -json-export -target <host>` with **strict** template list (`-t` file/dir) to avoid unreviewed RCE templates.
- **Parser**: JSON lines → findings with `remediation_key` mapped to template severity/tags.
- **Safety**: Never run default full template pack against prod; ship curated `policies/nuclei-home.txt` list.

## TLS scanners

- **sslscan**: XML or text parse → findings for weak cipher/TLS version (`remediation_key`: `TLS_WEAK_PROTOCOL`).
- **testssl.sh**: CSV/JSON output modes; map IDs to normalized schema.

## OpenVAS / Greenbone (Phase 3)

- **Integration style**: spawn `gvm-cli` or use HTTPS API from optional sidecar container.
- **Normalization**: map GMP result XML to `finding_id` + CVE references in `evidence.cves`.

## Diff between runs

- **Data model**: add `Job.compare_to_job_id` optional field; after parse, load prior job’s findings for same project.
- **Algorithm**: key findings by `(target, port, protocol, plugin_id)`; emit synthetic findings:
  - `PORT_NEW`, `PORT_CLOSED`, `SERVICE_CHANGED` with `evidence.before` / `evidence.after`.
- **UI**: timeline selector for “baseline” vs “current” job.

## Scheduling

- Replace synchronous job runner with APScheduler or Celery + Redis; persist `next_run_at` on project or job template.
- Windows: document Task Scheduler as alternative for firing `curl` to local API.

## Webhooks

- POST JSON payload on job completion; HMAC signature optional.

## SARIF evolution

- Map normalized severities to SARIF `level`; include `reportingDescriptor` per `remediation_key` for GitHub Advanced Security compatibility.
