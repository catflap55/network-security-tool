import unittest
from pathlib import Path

from app.parsers.nmap_xml import parse_nmap_xml

FIXTURE = Path(__file__).parent / "fixtures" / "sample_nmap.xml"


class TestNmapParser(unittest.TestCase):
    def test_parses_open_ports_and_host_up(self) -> None:
        xml_bytes = FIXTURE.read_bytes()
        findings = parse_nmap_xml(xml_bytes, "nmap_quick")
        keys = {f.remediation_key for f in findings}
        self.assertIn("HOST_UP", keys)
        self.assertIn("OPEN_TCP_PORT", keys)
        self.assertIn("SERVICE_DETECTED", keys)
        by_port = {
            f.evidence.get("port"): f.remediation_key
            for f in findings
            if f.evidence.get("port")
        }
        self.assertEqual(by_port.get("22"), "SERVICE_DETECTED")
        self.assertEqual(by_port.get("8080"), "OPEN_TCP_PORT")
        ssh = next(f for f in findings if f.evidence.get("port") == "22")
        self.assertEqual(ssh.target, "127.0.0.1")
        self.assertEqual(ssh.severity, "medium")

    def test_empty_xml(self) -> None:
        findings = parse_nmap_xml(b"", "nmap_quick")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].remediation_key, "SCAN_ERROR")

    def test_malformed_xml(self) -> None:
        findings = parse_nmap_xml(b"not xml", "nmap_quick")
        self.assertEqual(findings[0].remediation_key, "SCAN_ERROR")


if __name__ == "__main__":
    unittest.main()
