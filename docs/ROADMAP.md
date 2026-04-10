# Roadmap

Aligned with the master plan. **Out of scope** lines clarify boundaries until the listed phase.

## Phase 0 — Documentation and threat model (complete with repo)

- Architecture, toolbox, scan profiles, playbooks, auto-fix policy, severity mapping ([SEVERITY_MAPPING.md](SEVERITY_MAPPING.md)), Phase 2 extensions, this roadmap.

## Phase 1 — MVP console (current implementation target)

- FastAPI backend: projects, jobs, SQLite, plugin registry.
- Nmap plugins: `nmap_quick`, `nmap_safe_full`; XML parser; normalized findings.
- React UI: authorization gate, job runner, logs, findings, export JSON / SARIF subset.
- Safety: acknowledgment, `LAB_MODE`, job impact summaries.

**Out of scope until Phase 2:** Nuclei, TLS scanners, schedules, diff-between-runs.

## Phase 2 — Breadth and comparison

- Nuclei with **pinned** template set; sslscan or testssl.sh wrapper.
- Scheduled scans and **diff** between two job runs (new/removed/changed open ports).
- See [PHASE2_EXTENSIONS.md](PHASE2_EXTENSIONS.md).

**Out of scope until Phase 3:** OpenVAS, fleet agents.

## Phase 3 — Depth

- Host inventory: OSQuery bundle or PowerShell inventory; CVE context where CPE available.
- OpenVAS/Greenbone via Docker/WSL with documented resource needs.

**Out of scope until Phase 4:** Passive DNS ingest, IDS.

## Phase 4 — Passive and egress

- Import DNS logs (Pi-hole, AdGuard, router export); basic anomaly hints (volume, NXDOMAIN spikes) with false-positive warnings.
- Optional Suricata/Zeek on span.

## Phase 5 — Enterprise-style (only if needed)

- Multi-tenant, remote sensors, RBAC, SIEM forwarding.

## What the MVP explicitly does not claim

- Detection of novel/zero-day vulnerabilities without behavioral baselines.
- Full cloud/identity posture without cloud API integrations.
- Silent fleet-wide remediation.
