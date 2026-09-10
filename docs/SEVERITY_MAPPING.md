# Severity mapping conventions

Normalized findings use: `critical` | `high` | `medium` | `low` | `info`.

## Nmap-derived findings (MVP)

| Condition | Severity | `remediation_key` |
|-----------|----------|-------------------|
| Open TCP port with script output suggesting vuln / default cred (future NSE) | `high`–`critical` | `SERVICE_DETECTED` |
| Open TCP port, service unknown or generic | `medium` | `OPEN_TCP_PORT` |
| Open UDP port | `medium` | `OPEN_UDP_PORT` |
| Host up (discovery only) | `info` | `HOST_UP` |
| Parse or tool error | `low` | `SCAN_ERROR` |

MVP Nmap parser without aggressive NSE: open ports default to **`medium`**; filtered/closed are not emitted as findings; host up as **`info`**.

## Global rules

- **Do not upgrade** severity without evidence (CVE, unsafe protocol version, etc.).
- **Synthetic** findings (diff, coverage) use `info` or `low` unless they indicate exposure change (`PORT_NEW` → `medium` in Phase 2).
