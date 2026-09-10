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
    "TLS_OK": """## TLS looks healthy

Keep certificates on a renewal calendar. Prefer TLS 1.2+ only.
""",
    "TLS_LEGACY_PROTOCOL": """## Legacy TLS

Disable SSLv3, TLS 1.0, and TLS 1.1 on the service. Keep TLS 1.2 or 1.3.
""",
    "TLS_CERT_EXPIRED": """## Expired certificate

Replace the certificate immediately. Browsers and APIs will reject the host.
""",
    "TLS_CERT_EXPIRING": """## Certificate expiring soon

Renew before the not-after date. Automate renewal (ACME) where you can.
""",
    "TLS_UNREACHABLE": """## No TLS listener

Nothing accepted a TLS handshake on this port. Expected for hosts that are not web/TLS servers.
""",
    "HTTP_HEADERS_MISSING": """## Missing HTTP security headers

Add HSTS, CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, and Permissions-Policy at the reverse proxy or app.
""",
    "HTTP_HEADERS_OK": """## HTTP security headers present

Keep them in sync when you change the site.
""",
    "HTTP_UNREACHABLE": """## No HTTP response

The host did not answer on 80/443. Fine for printers, IoT, or firewalled devices.
""",
}


def get_playbook_markdown(key: str) -> str | None:
    return PLAYBOOKS.get(key)
