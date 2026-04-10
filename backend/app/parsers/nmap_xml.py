"""Parse Nmap XML (-oX) into NormalizedFinding list."""

from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any

from app.schemas_finding import NormalizedFinding


def _fid(plugin_id: str, target: str, kind: str, extra: str) -> str:
    raw = f"{plugin_id}:{target}:{kind}:{extra}".encode()
    return hashlib.sha256(raw).hexdigest()[:24]


def parse_nmap_xml(xml_bytes: bytes, plugin_id: str) -> list[NormalizedFinding]:
    if not xml_bytes.strip():
        return [
            NormalizedFinding(
                finding_id=_fid(plugin_id, "*", "error", "empty"),
                severity="low",
                title="Empty Nmap output",
                description="No XML was produced. Check that nmap is installed and targets are reachable.",
                remediation_key="SCAN_ERROR",
                plugin_id=plugin_id,
                target="*",
                evidence={"error": "empty_xml"},
                first_seen=datetime.now(timezone.utc),
            )
        ]

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        return [
            NormalizedFinding(
                finding_id=_fid(plugin_id, "*", "error", "parse"),
                severity="low",
                title="Nmap XML parse error",
                description=str(e),
                remediation_key="SCAN_ERROR",
                plugin_id=plugin_id,
                target="*",
                evidence={"error": "parse_error", "detail": str(e)},
                first_seen=datetime.now(timezone.utc),
            )
        ]

    findings: list[NormalizedFinding] = []
    now = datetime.now(timezone.utc)

    for host in root.findall("host"):
        addr_el = host.find("address")
        if addr_el is None:
            continue
        target = addr_el.get("addr", "")

        status = host.find("status")
        state = status.get("state") if status is not None else None
        if state == "up":
            findings.append(
                NormalizedFinding(
                    finding_id=_fid(plugin_id, target, "host", "up"),
                    severity="info",
                    title=f"Host up: {target}",
                    description="Host responded during discovery.",
                    remediation_key="HOST_UP",
                    plugin_id=plugin_id,
                    target=target,
                    evidence={"state": "up"},
                    first_seen=now,
                )
            )

        ports_el = host.find("ports")
        if ports_el is None:
            continue

        for port in ports_el.findall("port"):
            proto = port.get("protocol", "tcp")
            portid = port.get("portid", "")
            state_el = port.find("state")
            port_state = state_el.get("state") if state_el is not None else ""

            if port_state != "open":
                continue

            service_el = port.find("service")
            svc_name = service_el.get("name") if service_el is not None else ""
            product = service_el.get("product") if service_el is not None else ""
            version = service_el.get("version") if service_el is not None else ""
            extrainfo = service_el.get("extrainfo") if service_el is not None else ""

            evidence: dict[str, Any] = {
                "port": portid,
                "protocol": proto,
                "state": port_state,
                "service_name": svc_name or None,
                "product": product or None,
                "version": version or None,
                "extrainfo": extrainfo or None,
            }

            if proto == "udp":
                rem = "OPEN_UDP_PORT"
                title = f"Open UDP {portid} on {target}"
            else:
                rem = "OPEN_TCP_PORT"
                title = f"Open TCP {portid} on {target}"

            if product or version:
                rem = "SERVICE_DETECTED"
                bits = " ".join(x for x in (product, version, extrainfo) if x)
                title = f"Service on {target}:{portid} — {bits or svc_name or 'unknown'}"

            desc_parts = [f"{proto.upper()} port {portid} is open."]
            if svc_name:
                desc_parts.append(f"Service: {svc_name}.")
            if product:
                desc_parts.append(f"Product: {product} {version or ''}.".strip())

            findings.append(
                NormalizedFinding(
                    finding_id=_fid(plugin_id, target, "port", f"{proto}:{portid}"),
                    severity="medium",
                    title=title.strip(),
                    description=" ".join(desc_parts),
                    remediation_key=rem,
                    plugin_id=plugin_id,
                    target=target,
                    evidence=evidence,
                    first_seen=now,
                )
            )

    if not findings:
        runstats = root.find("runstats")
        finished = runstats.find("finished") if runstats is not None else None
        summary = finished.get("summary") if finished is not None else "No hosts or open ports found."
        findings.append(
            NormalizedFinding(
                finding_id=_fid(plugin_id, "*", "info", "empty"),
                severity="info",
                title="Scan completed — no open ports in scope",
                description=summary,
                remediation_key="COVERAGE_GAP",
                plugin_id=plugin_id,
                target="*",
                evidence={"nmap_summary": summary},
                first_seen=now,
            )
        )

    return findings
