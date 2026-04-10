"""Remediation snippets; mirrors docs/REMEDIATION_PLAYBOOKS.md for API use."""

PLAYBOOKS: dict[str, str] = {
    "OPEN_TCP_PORT": """## Open TCP port

1. Identify the service (banner or `nmap -sV` on a single host).
2. If unintended, stop the service or restrict with a host firewall.
3. If intended, patch, enforce strong authentication, and segment the network.

**Automation (preview):** Generate a firewall deny rule in the UI; apply manually after review.
""",
    "OPEN_UDP_PORT": """## Open UDP port

1. Confirm the protocol (e.g. SNMP, mDNS).
2. Close if unused; filter at the edge if only LAN access is required.
""",
    "SERVICE_DETECTED": """## Service detected

1. Map the product/version to vendor support and CVEs.
2. Upgrade or reconfigure (TLS versions, ciphers, default accounts).
""",
    "HOST_UP": """## Host up

Add the host to your asset inventory and assign an owner/criticality tag.
""",
    "SCAN_ERROR": """## Scan error

Verify `nmap` is on PATH (or set `NMAP_PATH`), targets are reachable, and firewalls allow probes from this machine.
""",
    "UNSUPPORTED_PLUGIN": """## Unsupported plugin

Install the required tool, enable `LAB_MODE` if this is a lab-only plugin, and re-run after acknowledging authorization.
""",
    "COVERAGE_GAP": """## Coverage gap

This result does not prove the host is clean—only that no open ports were found in the scanned set. Plan authenticated scans, host agents, or passive DNS/flow data for egress visibility.
""",
}


def get_playbook_markdown(key: str) -> str | None:
    return PLAYBOOKS.get(key)
