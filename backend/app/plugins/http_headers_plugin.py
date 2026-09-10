from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.models import Project
from app.plugins.base import ScanPlugin
from app.schemas_finding import NormalizedFinding
from app.services.targets import TargetError, validate_targets

_HEADERS = (
    "strict-transport-security",
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
    "permissions-policy",
)


def _fid(plugin_id: str, target: str, kind: str) -> str:
    return hashlib.sha256(f"{plugin_id}:{target}:{kind}".encode()).hexdigest()[:24]


class HttpHeadersPlugin(ScanPlugin):
    id = "http_headers"
    display_name = "HTTP security headers"
    description = (
        "Fetches the home page over HTTPS (then HTTP) and notes missing browser security headers. "
        "Read-only GET; no login bypass."
    )
    requires_lab_mode = False
    uses_subprocess = False
    impact_summary = (
        "Sends one GET request per host (HTTPS first). Same as opening the site in a browser."
    )

    def build_command(self, project: Project, nmap_path: str) -> list[str]:
        return ["python", "-c", "http_headers", project.targets]

    def parse_output(self, xml_bytes: bytes) -> list[NormalizedFinding]:
        return []

    def run_in_process(self, project: Project, artifact_dir: Path) -> tuple[list[NormalizedFinding], str]:
        findings, log = check_targets(project.targets, self.id)
        (artifact_dir / "http_headers.log").write_text(log, encoding="utf-8")
        return findings, log


def check_targets(text: str, plugin_id: str) -> tuple[list[NormalizedFinding], str]:
    now = datetime.now(timezone.utc)
    try:
        parsed = validate_targets(text)
    except TargetError as exc:
        f = NormalizedFinding(
            finding_id=_fid(plugin_id, "*", "bad-target"),
            severity="low",
            title="Invalid targets",
            description=str(exc),
            remediation_key="SCAN_ERROR",
            plugin_id=plugin_id,
            target="*",
            evidence={"error": str(exc)},
            first_seen=now,
        )
        return [f], str(exc)

    out: list[NormalizedFinding] = []
    logs: list[str] = []
    for p in parsed:
        port = p.port
        schemes = [("https", port or 443), ("http", port or 80)]
        if port:
            schemes = [("https", port), ("http", port)]
        got = False
        for scheme, port_n in schemes:
            url = f"{scheme}://{p.host}:{port_n}/"
            try:
                req = Request(url, method="GET", headers={"User-Agent": "SecurityConsole/1.0"})
                with urlopen(req, timeout=8) as resp:
                    headers = {k.lower(): v for k, v in resp.headers.items()}
                    status = getattr(resp, "status", 0)
                got = True
                logs.append(f"{url} -> {status}")
                missing = [h for h in _HEADERS if h not in headers]
                if missing:
                    out.append(
                        NormalizedFinding(
                            finding_id=_fid(plugin_id, url, "missing"),
                            severity="medium",
                            title=f"Missing security headers on {url}",
                            description="Missing: " + ", ".join(missing),
                            remediation_key="HTTP_HEADERS_MISSING",
                            plugin_id=plugin_id,
                            target=url,
                            evidence={"missing": missing, "present": sorted(headers.keys())},
                            first_seen=now,
                        )
                    )
                else:
                    out.append(
                        NormalizedFinding(
                            finding_id=_fid(plugin_id, url, "ok"),
                            severity="info",
                            title=f"Core security headers present on {url}",
                            description="HSTS, CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy.",
                            remediation_key="HTTP_HEADERS_OK",
                            plugin_id=plugin_id,
                            target=url,
                            evidence={"present": list(_HEADERS)},
                            first_seen=now,
                        )
                    )
                break
            except URLError as exc:
                logs.append(f"{url} failed: {exc}")
            except OSError as exc:
                logs.append(f"{url} failed: {exc}")
        if not got:
            out.append(
                NormalizedFinding(
                    finding_id=_fid(plugin_id, p.host, "down"),
                    severity="info",
                    title=f"No HTTP(S) response from {p.host}",
                    description="Nothing answered on 80/443 (or the port you set).",
                    remediation_key="HTTP_UNREACHABLE",
                    plugin_id=plugin_id,
                    target=p.host,
                    evidence={},
                    first_seen=now,
                )
            )
    return out, "\n".join(logs) + "\n"
