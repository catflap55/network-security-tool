import unittest

from app.services.targets import TargetError, nmap_target_args, validate_targets


class TestTargets(unittest.TestCase):
    def test_localhost(self) -> None:
        parsed = validate_targets("127.0.0.1")
        self.assertEqual(parsed[0].host, "127.0.0.1")

    def test_rejects_shell(self) -> None:
        with self.assertRaises(TargetError):
            validate_targets("127.0.0.1; nmap")

    def test_rejects_internet(self) -> None:
        with self.assertRaises(TargetError):
            validate_targets("0.0.0.0/0")

    def test_rejects_huge_cidr(self) -> None:
        with self.assertRaises(TargetError):
            validate_targets("10.0.0.0/8")

    def test_allows_slash24(self) -> None:
        parsed = validate_targets("192.168.1.0/24")
        self.assertEqual(parsed[0].kind, "cidr")
        self.assertEqual(nmap_target_args("192.168.1.0/24"), ["192.168.1.0/24"])

    def test_hostname(self) -> None:
        parsed = validate_targets("nas.home")
        self.assertEqual(parsed[0].kind, "hostname")

    def test_metadata_blocked(self) -> None:
        with self.assertRaises(TargetError):
            validate_targets("169.254.169.254")
