from __future__ import annotations

from pathlib import Path

from app.models import Project
from app.plugins.base import ScanPlugin
from app.schemas_finding import NormalizedFinding
from app.services.tls_inspect import inspect_targets


class TlsInspectPlugin(ScanPlugin):
    id = "tls_inspect"
    display_name = "TLS certificate check"
    description = (
        "Connects with TLS (default port 443) and reports protocol version, certificate expiry, "
        "and hostname mismatch. Does not exploit services."
    )
    requires_lab_mode = False
    uses_subprocess = False
    impact_summary = (
        "Opens a short encrypted handshake to each host on port 443 (or a port you set). "
        "No brute force and no payload — the same kind of check a browser does."
    )

    def build_command(self, project: Project, nmap_path: str) -> list[str]:
        return ["python", "-m", "app.plugins.tls_plugin", project.targets]

    def parse_output(self, xml_bytes: bytes) -> list[NormalizedFinding]:
        return []

    def run_in_process(self, project: Project, artifact_dir: Path) -> tuple[list[NormalizedFinding], str]:
        findings, log = inspect_targets(project.targets, plugin_id=self.id)
        (artifact_dir / "tls_inspect.log").write_text(log, encoding="utf-8")
        return findings, log
