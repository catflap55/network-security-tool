# Remediation playbooks

Findings include a `remediation_key` that maps to this document. Automation candidates are noted; MVP ships **guidance** and optional **script previews** only—no silent changes.

## `OPEN_TCP_PORT`

- **Summary**: A TCP port accepted a connection during scanning.
- **Steps**:
  1. Identify the service (banner, manual `nmap -sV` on single host if needed).
  2. If unintended, stop/disable the service or restrict with host firewall.
  3. If intended, ensure patching, strong auth, and least-privilege network access (segmentation).
- **Automation candidate**: Generate host firewall rule **preview** (PowerShell/`ufw`) for explicit deny of port—operator applies manually.

## `OPEN_UDP_PORT`

- **Summary**: UDP port appeared open or responsive.
- **Steps**: Confirm protocol (SNMP, mDNS, etc.); close if unused; filter at edge if only LAN-internal needed.

## `SERVICE_DETECTED`

- **Summary**: Service fingerprint or version hint observed.
- **Steps**: Match to vendor support lifecycle; patch or replace; remove deprecated TLS/ciphers via server config.

## `HOST_UP`

- **Summary**: Host responded to discovery (informational).
- **Steps**: Add to asset inventory; tag owner and criticality.

## `SCAN_ERROR`

- **Summary**: Tool failed partially or fully.
- **Steps**: Check PATH, privileges, target reachability, and firewall on scan host.

## `UNSUPPORTED_PLUGIN`

- **Summary**: Plugin requires `LAB_MODE` or missing binary.
- **Steps**: Install tool, adjust env, or enable lab mode per [AUTO_FIX_POLICY.md](AUTO_FIX_POLICY.md).

## `COVERAGE_GAP`

- **Summary**: No authenticated or passive data—findings are incomplete.
- **Steps**: Plan credentialed scan, agent inventory, or DNS/flow export for egress visibility.

---

Playbook snippets may be embedded in the API as `remediation_markdown` for the UI. Keep steps short; link to vendor docs for version-specific clicks.
