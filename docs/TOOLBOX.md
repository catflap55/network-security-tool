# Toolbox

Curated engines the console can wrap. **Personal use only.** Run these only against a **home network that you own**. Do not run them against work, school, public Wi-Fi, neighbours, clients, or the public internet.

## Discovery and ports

| Tool | Role | Windows | WSL/Linux | When not to run |
|------|------|---------|-----------|-----------------|
| **Nmap** | Host discovery, port scan, service/version detection | Native .exe | Package manager | IoT/medical/OT without gentle profile; production during peak hours without change window. |

**Install**

- Windows: https://nmap.org/download.html — add to PATH.
- **Npcap** (e.g. 1.87+): bundled with the Windows Nmap installer or from [npcap.com](https://npcap.com/). Lets Nmap use raw sockets for SYN scans and better discovery. If an older tool expects WinPcap, enable **“Install Npcap in WinPcap API-compatible mode”** during setup. Run elevated (**Run as administrator**) when Nmap says it needs admin for raw capture.
- Debian/Ubuntu: `sudo apt install nmap`
- Optional env: **`NMAP_PATH`** = full path to `nmap.exe` if `nmap` is not on PATH (common on Windows). The API also tries **`Program Files (x86)\Nmap`** and **`Program Files\Nmap`** automatically. Set in `backend/.env` or the shell that starts Uvicorn, then restart the API.

## Web and application exposure (Phase 2+)

| Tool | Role | When not to run |
|------|------|-----------------|
| **Nuclei** | Template-based checks | Without scope control; unreviewed templates against prod. |
| **Nikto** | Web server issues | Legacy apps that crash on probes. |
| **OWASP ZAP** | Baseline DAST | Without isolated test URLs. |

## Vulnerability management (Phase 3+)

| Tool | Role | When not to run |
|------|------|-----------------|
| **OpenVAS / Greenbone** | Network VM, credentialed where configured | Without resource plan (heavy); fragile VLANs. |
| **Nessus** | Commercial VM | Licensing and scope per vendor policy. |

## TLS / HTTP (shipped)

| Check | Role | When not to run |
|------|------|-----------------|
| **TLS inspect** (built-in) | Certificate expiry and protocol version | Against hosts you do not operate |
| **HTTP headers** (built-in) | Missing browser security headers | Against sites you do not operate |

External `testssl.sh` / `sslscan` are optional later wrappers; the console already ships a Python TLS check so you do not need those binaries.

## Not included (and not planned)

Credential guessing (Hydra, hashcat), wireless cracking, and exploit payloads will not ship in this console.

## Traffic visibility (Phase 4+)

| Tool | Role | When not to run |
|------|------|-----------------|
| **Suricata** / **Zeek** | IDS/NSM on span/tap | Without mirror port; privacy review for household traffic. |

## Host integrity

| Tool | Role | When not to run |
|------|------|-----------------|
| **OSQuery** | Fleet queries | Without endpoint policy approval. |
| **Lynis** | Linux hardening audit | Production during freeze without approval. |
| **Defender / WMI** | Windows patch posture | Requires appropriate rights. |
| **Trivy** / **Grype** | Container/image CVEs | For images you build or mirror. |

## Secrets on disk (optional integrations)

| Tool | Role |
|------|------|
| **gitleaks** / **trufflehog** | Repo and path scanning for secrets |

## MVP console

The shipped console integrates **Nmap**, **TLS inspect**, and **HTTP security headers**. Other tools stay on the roadmap.
