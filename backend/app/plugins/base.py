from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Project
    from app.schemas_finding import NormalizedFinding


class ScanPlugin(ABC):
    id: str
    display_name: str
    description: str
    requires_lab_mode: bool = False
    uses_subprocess: bool = True
    impact_summary: str = ""

    @abstractmethod
    def build_command(self, project: "Project", nmap_path: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def parse_output(self, xml_bytes: bytes) -> list["NormalizedFinding"]:
        raise NotImplementedError

    def run_in_process(self, project: "Project", artifact_dir):
        raise NotImplementedError
