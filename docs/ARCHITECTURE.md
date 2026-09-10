# Architecture

## Purpose

Security Console is a **local control plane** that orchestrates trusted checks (Nmap, TLS, HTTP headers), normalizes results into a single finding model, and links findings to remediation guidance. It does not replace a SOC, EDR, or commercial VM platform.

## Threat model

### Assets

- **Console host**: runs API, UI, SQLite, and stores raw scan artifacts (XML, logs).
- **Scan credentials**: this console does not store SSH/WMI passwords. Tools run as the OS user who started the API.
- **Findings database**: may contain hostnames, IPs, service banners (sensitive on shared machines).

### Trust boundaries

| Zone | Trust level | Notes |
|------|-------------|--------|
| Operator (you) | High | Can start jobs, read all data, export results. |
| Console process | High | Invokes `nmap` and other tools with your privileges. |
| Target network | Variable | Treat as untrusted input (banner data, HTTP titles). |
| External tools (Nmap, etc.) | Medium | Supply chain risk; pin versions where possible. |

### Assumptions

- The operator has **legal authorization** to scan configured targets.
- The console binds to **localhost** by default to reduce exposure.
- No multi-tenant isolation in MVP; single operator per instance.

## Deployment modes

### Mode A: Single Windows admin station (MVP default)

- Backend: Python + Uvicorn on `127.0.0.1`.
- Frontend: Vite dev server or static build served separately; API proxy optional.
- **Nmap**: Install [Nmap for Windows](https://nmap.org/download.html) and ensure `nmap` is on `PATH` (or set `NMAP_PATH`).

### Mode B: Linux sensor (future)

- Same codebase; prefer non-root scans or dedicated scan user with capabilities.
- Optional: mirror port for passive ingestion (Suricata/Zeek) in Phase 4.

### Mode C: WSL2

- Run backend in WSL; scanning from WSL uses Linux `nmap`. Windows targets on the LAN are reachable; bridge networking quirks may apply—document in runbooks.

## Data flow

1. Operator creates a **project** (targets + environment tag).
2. Operator acknowledges **authorization** and starts a **job** (plugin + parameters).
3. **Execution layer** runs the plugin subprocess with timeout; stdout/stderr streamed to logs.
4. **Parser** converts tool output to **normalized findings**; **risk** rules assign severity.
5. UI displays findings, playbook links, and export (JSON / SARIF subset).

## Storage

- **SQLite** (`data/console.db`): projects, jobs, findings, settings.
- **File artifacts** (`data/artifacts/<job_id>/`): raw XML, logs for audit and re-parse.

## Extension points

See [ROADMAP.md](ROADMAP.md) and [PHASE2_EXTENSIONS.md](PHASE2_EXTENSIONS.md) for Nuclei, TLS scanners, OpenVAS, and diff-between-runs.

## Privacy and retention

- Logs may contain banners and URLs. Default: retain artifacts until deleted with job; export before sharing.
- Document household/PII risk in operational procedures; avoid uploading raw scans to untrusted clouds.

## Quick start (development)

### One-click (Windows)

- **Double-click** **[Start-Security-Console.cmd](../Start-Security-Console.cmd)** in the repo root (uses `cmd.exe`). It opens a **second** window running `npm run dev:full`, waits for the API and Vite, then opens **http://127.0.0.1:5173/**.
- **If you already use PowerShell:** `cd` into the repo folder, then run **`.\Start-Security-Console.ps1`** (not the `.cmd` contents — those are batch syntax and will error if pasted into PowerShell).
- **Stop:** double-click **[Stop-Security-Console.cmd](../Stop-Security-Console.cmd)**, or in PowerShell **`.\Stop-Security-Console.ps1`**. Either frees ports **5173** and **8000**. You can also close the **second** window running `npm run dev:full`.
- Optional: run `powershell -ExecutionPolicy Bypass -File scripts/create-desktop-shortcuts.ps1` once to put **Start** / **Stop** shortcuts on your Desktop (with icons).

---

1. Install Python 3.11+, Node 20+, and [Nmap](https://nmap.org/download.html) on the machine that runs scans.
2. Backend: from the **repo root**:
   - **`npm run api`** — runs `pip install` (quiet) for `backend/requirements.txt` using the same **`python`** on your PATH, then starts Uvicorn. Activate a venv first if you want dependencies isolated. Install only: **`npm run api:install`**.
   - **Manual:** `cd backend`, set `PYTHONPATH=.` (PowerShell: `$env:PYTHONPATH="."`), `python -m pip install -r requirements.txt`, `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.
   - **Windows:** `.\start-backend.ps1` (also installs requirements then starts Uvicorn).
3. Frontend: from the **repo root**, `npm install` then `npm run dev`. The dev server **proxies** `/api` → `http://127.0.0.1:8000`, so the UI does not depend on CORS for normal use. To run UI + API together: `npm run dev:full` (after `npm install` so `concurrently` is present).
4. Open the printed URL (Vite defaults to port 5173).
5. Optional: set environment variables on the backend process: `LAB_MODE=true`, `NMAP_PATH` to the `nmap` executable if it is not on `PATH`.
