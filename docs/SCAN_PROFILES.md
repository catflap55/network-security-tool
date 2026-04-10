# Scan profiles

Profiles map to **plugin IDs** in the console. Each profile documents **intent**, **approximate impact**, and **safeguards**.

## Environment tags

Projects carry `environment`: `home` | `lab` | `office` | `mixed`. Use tags for reporting only in MVP; future policy packs can restrict plugins by tag.

## `nmap_quick` (MVP)

- **Intent**: Fast discovery of live hosts and common TCP ports on small LANs.
- **Typical flags** (fixed in plugin): ping scan or light TCP connect/syn where appropriate, top ports or small port list, **no** aggressive version scripts by default.
- **Impact**: Low to medium; brief connection attempts.
- **IoT**: Prefer running against known-safe maintenance windows; stop if devices misbehave.

## `nmap_safe_full` (MVP)

- **Intent**: Broader TCP port coverage with **timing throttled** (`-T2` or safer) and **no** default NSE intrusion scripts.
- **Impact**: Medium; longer duration, more packets.
- **Safeguards**: Rate limiting via Nmap timing; operator sets target size responsibly.

## `HomeSafe` (conceptual — map to `nmap_safe_full` + small targets)

- Passive discovery first (future); active scan small batches.
- No UDP flood; avoid `-sU` wide sweeps on home IoT.

## `LabAggressive` (placeholder plugin)

- Registered as **`lab_aggressive_placeholder`** when `LAB_MODE=true` on the API process (restart required after changing env).
- The UI lists it as **locked** until then; see `docs/AUTO_FIX_POLICY.md`.
- Heavier NSE / intrusive checks remain future work behind explicit opt-in.

## `OfficeBalanced` (future)

- Change-window scheduling; document in change ticket.
- Split scans by subnet to avoid saturating WAN links.

## Medical / industrial / OT

- **Do not** run active scans on patient-care or safety-critical networks without vendor and clinical/engineering approval.
- Use **passive** inventory (DHCP/ARP exports, read-only SNMP) when available.

## Authorization

Every job requires the operator to maintain **authorization acknowledged** in Settings. Revoking acknowledgment blocks new jobs.
