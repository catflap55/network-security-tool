"""Validate scan targets so jobs cannot pass shell metacharacters or huge ranges."""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass

_HOSTNAME = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
)
_UNSAFE = re.compile(r"[;|&`$<>\\'\n\r\t]")
_BLOCKED_IPS = {
    ipaddress.ip_address("169.254.169.254"),
}


class TargetError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedTarget:
    raw: str
    kind: str
    host: str
    port: int | None
    host_count: int


def split_targets(text: str) -> list[str]:
    if not text or not str(text).strip():
        raise TargetError("Enter at least one target (IP, hostname, or CIDR).")
    if _UNSAFE.search(text):
        raise TargetError("Targets cannot contain shell characters such as ; | & ` $ < > \\.")
    parts = [p.strip() for p in re.split(r"[\s,]+", text) if p.strip()]
    if not parts:
        raise TargetError("Enter at least one target (IP, hostname, or CIDR).")
    return parts


def _strip_scheme(token: str) -> str:
    lower = token.lower()
    for prefix in ("https://", "http://"):
        if lower.startswith(prefix):
            token = token[len(prefix) :]
            return token.split("/")[0]
    return token


def _split_host_port(token: str) -> tuple[str, int | None]:
    if token.startswith("["):
        inside, _, rest = token[1:].partition("]")
        port = None
        if rest.startswith(":") and rest[1:].isdigit():
            port = int(rest[1:])
        return inside, port
    if token.count(":") == 1:
        host, port_s = token.rsplit(":", 1)
        if port_s.isdigit():
            port = int(port_s)
            if port < 1 or port > 65535:
                raise TargetError(f"Port out of range: {port}")
            return host, port
    return token, None


def parse_one(token: str, *, max_cidr_hosts: int) -> ParsedTarget:
    token = _strip_scheme(token.strip())
    if not token:
        raise TargetError("Empty target.")
    if _UNSAFE.search(token) or any(c in token for c in ("*", "?", "!", "#")):
        raise TargetError(f"Rejected target: {token!r}")

    host, port = _split_host_port(token)

    if "/" in host:
        try:
            net = ipaddress.ip_network(host, strict=False)
        except ValueError as exc:
            raise TargetError(f"Invalid CIDR: {host}") from exc
        if net.prefixlen == 0:
            raise TargetError("Scanning the whole internet is not allowed.")
        count = int(net.num_addresses)
        if net.version == 4 and count > max_cidr_hosts:
            raise TargetError(
                f"CIDR {host} covers {count} addresses; the limit is {max_cidr_hosts}. "
                "Use a tighter range (for example 192.168.1.0/24) or set LAB_MODE=true for larger lab nets."
            )
        return ParsedTarget(raw=token, kind="cidr", host=str(net), port=port, host_count=count)

    try:
        ip = ipaddress.ip_address(host)
        if ip.is_multicast or ip.is_unspecified or ip in _BLOCKED_IPS:
            raise TargetError(f"Address not allowed: {host}")
        kind = "ipv4" if ip.version == 4 else "ipv6"
        return ParsedTarget(raw=token, kind=kind, host=str(ip), port=port, host_count=1)
    except TargetError:
        raise
    except ValueError:
        pass

    if not _HOSTNAME.match(host):
        raise TargetError(
            f"Not a valid IP, CIDR, or hostname: {token!r}. Example: 192.168.1.1 or nas.home"
        )
    return ParsedTarget(raw=token, kind="hostname", host=host, port=port, host_count=1)


def validate_targets(
    text: str,
    *,
    max_targets: int = 64,
    max_cidr_hosts: int = 256,
) -> list[ParsedTarget]:
    parts = split_targets(text)
    if len(parts) > max_targets:
        raise TargetError(f"Too many targets ({len(parts)}). Maximum is {max_targets}.")
    parsed = [parse_one(p, max_cidr_hosts=max_cidr_hosts) for p in parts]
    total = sum(p.host_count for p in parsed)
    cap = max(max_cidr_hosts * 4, max_cidr_hosts)
    if total > cap:
        raise TargetError(f"Combined address count {total} is too large. Shrink the ranges.")
    return parsed


def nmap_target_args(text: str, *, max_targets: int = 64, max_cidr_hosts: int = 256) -> list[str]:
    parsed = validate_targets(text, max_targets=max_targets, max_cidr_hosts=max_cidr_hosts)
    args: list[str] = []
    for p in parsed:
        if p.kind == "cidr":
            args.append(p.host)
        else:
            args.append(p.host)
    return args or ["127.0.0.1"]
