from __future__ import annotations

from app.config import get_settings
from app.models import Project
from app.parsers.nmap_xml import parse_nmap_xml
from app.plugins.base import ScanPlugin
from app.schemas_finding import NormalizedFinding
from app.services.targets import nmap_target_args


def _targets_arg(project: Project) -> list[str]:
    s = get_settings()
    cap = 4096 if s.lab_mode else s.max_cidr_hosts
    return nmap_target_args(project.targets, max_targets=s.max_targets, max_cidr_hosts=cap)


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


class LabDiscoveryPlugin(ScanPlugin):
    """Lab-only ping/host discovery. No exploit scripts."""

    id = "lab_host_discovery"
    display_name = "Lab host discovery"
    description = "Nmap ping scan (-sn) to list live hosts. Requires LAB_MODE. Does not run exploit scripts."
    requires_lab_mode = True
    impact_summary = (
        "Sends host-discovery probes only (no port blast). For lab inventory. Requires LAB_MODE=true."
    )

    def build_command(self, project: Project, nmap_path: str) -> list[str]:
        return [nmap_path, "-v", "-sn", "-oX", "-", *_targets_arg(project)]

    def parse_output(self, xml_bytes: bytes) -> list[NormalizedFinding]:
        return parse_nmap_xml(xml_bytes, self.id)
