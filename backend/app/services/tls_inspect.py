from __future__ import annotations

import hashlib
import socket
import ssl
from datetime import datetime, timezone
from typing import Any

from app.schemas_finding import NormalizedFinding
from app.services.targets import TargetError, validate_targets


def _fid(plugin_id: str, target: str, kind: str) -> str:
    return hashlib.sha256(f"{plugin_id}:{target}:{kind}".encode()).hexdigest()[:24]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def inspect_one(host: str, port: int, plugin_id: str) -> tuple[list[NormalizedFinding], str]:
    findings: list[NormalizedFinding] = []
    lines = [f"TLS check {host}:{port}"]
    target = f"{host}:{port}"
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with socket.create_connection((host, port), timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                version = ssock.version() or "unknown"
                cipher = ssock.cipher()
                cert = ssock.getpeercert()
                der = ssock.getpeercert(binary_form=True)
    except OSError as exc:
        findings.append(
            NormalizedFinding(
                finding_id=_fid(plugin_id, target, "unreachable"),
                severity="info",
                title=f"No TLS service on {target}",
                description=str(exc),
                remediation_key="TLS_UNREACHABLE",
                plugin_id=plugin_id,
                target=target,
                evidence={"error": str(exc)},
                first_seen=_now(),
            )
        )
        return findings, lines[0] + f" — not reachable ({exc})\n"

    lines.append(f"  protocol={version} cipher={cipher}")
    if version in ("SSLv2", "SSLv3", "TLSv1", "TLSv1.1"):
        findings.append(
            NormalizedFinding(
                finding_id=_fid(plugin_id, target, "legacy"),
                severity="high",
                title=f"Legacy TLS protocol {version} on {target}",
                description="TLS 1.0/1.1 and SSL are deprecated. Offer TLS 1.2 or 1.3 only.",
                remediation_key="TLS_LEGACY_PROTOCOL",
                plugin_id=plugin_id,
                target=target,
                evidence={"version": version, "cipher": cipher},
                first_seen=_now(),
            )
        )
    else:
        findings.append(
            NormalizedFinding(
                finding_id=_fid(plugin_id, target, "proto"),
                severity="info",
                title=f"{version} accepted on {target}",
                description="Modern TLS protocol negotiated.",
                remediation_key="TLS_OK",
                plugin_id=plugin_id,
                target=target,
                evidence={"version": version, "cipher": cipher},
                first_seen=_now(),
            )
        )

    not_after = None
    subject = ""
    san: list[str] = []
    if cert:
        not_after = cert.get("notAfter")
        subject = str(cert.get("subject", ""))
        san = [v for (k, v) in cert.get("subjectAltName", ()) if k == "DNS"]
    expiry = None
    if not_after:
        try:
            expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        except ValueError:
            expiry = None
    if expiry:
        days = (expiry - _now()).days
        ev: dict[str, Any] = {"not_after": not_after, "days_remaining": days, "subject": subject, "san": san}
        if days < 0:
            findings.append(
                NormalizedFinding(
                    finding_id=_fid(plugin_id, target, "expired"),
                    severity="high",
                    title=f"TLS certificate expired on {target}",
                    description=f"Expired {abs(days)} day(s) ago ({not_after}).",
                    remediation_key="TLS_CERT_EXPIRED",
                    plugin_id=plugin_id,
                    target=target,
                    evidence=ev,
                    first_seen=_now(),
                )
            )
        elif days < 21:
            findings.append(
                NormalizedFinding(
                    finding_id=_fid(plugin_id, target, "expiring"),
                    severity="medium",
                    title=f"TLS certificate expires in {days} days on {target}",
                    description="Renew the certificate before it expires.",
                    remediation_key="TLS_CERT_EXPIRING",
                    plugin_id=plugin_id,
                    target=target,
                    evidence=ev,
                    first_seen=_now(),
                )
            )
        else:
            findings.append(
                NormalizedFinding(
                    finding_id=_fid(plugin_id, target, "cert"),
                    severity="info",
                    title=f"TLS certificate valid ({days} days left) on {target}",
                    description=subject or "Certificate presented.",
                    remediation_key="TLS_OK",
                    plugin_id=plugin_id,
                    target=target,
                    evidence=ev,
                    first_seen=_now(),
                )
            )
    elif der:
        findings.append(
            NormalizedFinding(
                finding_id=_fid(plugin_id, target, "cert-bin"),
                severity="low",
                title=f"TLS certificate present on {target} (details limited)",
                description="A certificate was presented but dates could not be parsed from the peer cert dict.",
                remediation_key="TLS_OK",
                plugin_id=plugin_id,
                target=target,
                evidence={"bytes": len(der)},
                first_seen=_now(),
            )
        )

    return findings, "\n".join(lines) + "\n"


def inspect_targets(text: str, plugin_id: str) -> tuple[list[NormalizedFinding], str]:
    try:
        parsed = validate_targets(text)
    except TargetError as exc:
        err = NormalizedFinding(
            finding_id=_fid(plugin_id, "*", "bad-target"),
            severity="low",
            title="Invalid targets",
            description=str(exc),
            remediation_key="SCAN_ERROR",
            plugin_id=plugin_id,
            target="*",
            evidence={"error": str(exc)},
            first_seen=_now(),
        )
        return [err], str(exc)
    all_f: list[NormalizedFinding] = []
    logs = []
    for p in parsed:
        port = p.port or 443
        f, log = inspect_one(p.host, port, plugin_id)
        all_f.extend(f)
        logs.append(log)
    return all_f, "\n".join(logs)
