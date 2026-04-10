from __future__ import annotations

from app.models import Project
from app.parsers.nmap_xml import parse_nmap_xml
from app.plugins.base import ScanPlugin
from app.schemas_finding import NormalizedFinding


def _targets_arg(project: Project) -> list[str]:
    parts = [t.strip() for t in project.targets.replace(",", " ").split() if t.strip()]
    return parts if parts else ["127.0.0.1"]


class NmapQuickPlugin(ScanPlugin):
    id = "nmap_quick"
    display_name = "Nmap quick"
    description = "Fast scan: top ports (-F), timing T3, XML to stdout."
    requires_lab_mode = False
    impact_summary = (
        "Sends TCP connect/SYN probes to ~100 common ports per live host. "
        "Brief; may still disturb fragile IoT—use small targets or maintenance windows."
    )

    def build_command(self, project: Project, nmap_path: str) -> list[str]:
        # -v sends progress to stderr so the Jobs panel can update while the scan runs
        return [nmap_path, "-v", "-T3", "-F", "--open", "-oX", "-", *_targets_arg(project)]

    def parse_output(self, xml_bytes: bytes) -> list[NormalizedFinding]:
        return parse_nmap_xml(xml_bytes, self.id)


class NmapSafeFullPlugin(ScanPlugin):
    id = "nmap_safe_full"
    display_name = "Nmap safe breadth"
    description = "Throttled scan of top 1000 TCP ports (T2), no intrusive NSE scripts."
    requires_lab_mode = False
    impact_summary = (
        "Probes up to 1000 TCP ports per host with slower timing (-T2). "
        "Longer runtime and more packets than quick scan; reduce scope if needed."
    )

    def build_command(self, project: Project, nmap_path: str) -> list[str]:
        return [
            nmap_path,
            "-v",
            "-T2",
            "--top-ports",
            "1000",
            "--open",
            "-oX",
            "-",
            *_targets_arg(project),
        ]

    def parse_output(self, xml_bytes: bytes) -> list[NormalizedFinding]:
        return parse_nmap_xml(xml_bytes, self.id)


class LabAggressivePlaceholderPlugin(ScanPlugin):
    """Registered only when LAB_MODE is true; documents aggressive path."""

    id = "lab_aggressive_placeholder"
    display_name = "Lab aggressive (placeholder)"
    description = "Example plugin requiring LAB_MODE. Does not run destructive tests in MVP."
    requires_lab_mode = True
    impact_summary = (
        "Placeholder: future heavy NSE or UDP sweeps. Requires LAB_MODE=true and explicit UI opt-in."
    )

    def build_command(self, project: Project, nmap_path: str) -> list[str]:
        return [nmap_path, "-v", "-sn", "-oX", "-", *_targets_arg(project)]

    def parse_output(self, xml_bytes: bytes) -> list[NormalizedFinding]:
        return parse_nmap_xml(xml_bytes, self.id)
