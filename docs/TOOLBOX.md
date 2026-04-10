# Toolbox

Curated engines the console can wrap. **Do not run** tools against systems you do not own or lack written permission to test.

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

## TLS / SSL

| Tool | Role | When not to run |
|------|------|-----------------|
| **testssl.sh** / **sslscan** | Cipher/protocol posture | Against services with strict rate limits or mutual TLS you cannot satisfy. |

## Wireless (separate module, legal caution)

| Tool | Role | When not to run |
|------|------|-----------------|
| **Kismet** / **airodump-ng** |802.11 survey | Any network you do not own; jurisdictions vary. |

## Password testing (lab + explicit consent only)

| Tool | Role | When not to run |
|------|------|-----------------|
| **Hydra** / **hashcat** | Credential strength | Default in console: **blocked** unless `LAB_MODE=true` and extra acknowledgment. |

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

The shipped MVP integrates **Nmap** only (`nmap_quick`, `nmap_safe_full`). Other tools are documented here for roadmap alignment.
