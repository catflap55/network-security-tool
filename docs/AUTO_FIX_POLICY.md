# Auto-fix policy

## Principles

1. **No silent production changes.** Any automated action must be **visible**, **confirmable**, and **reversible**.
2. **Allowlist only.** Only actions in the allowlist below may be offered as one-click or generated scripts.
3. **Audit.** Log who/when/what for any applied change (future RBAC; MVP: local operator).

## Allowlist (MVP)

| Action | Form | Rollback |
|--------|------|----------|
| Generate Windows firewall block rule | PowerShell snippet in UI (copy/paste) | Operator removes rule by name |
| Generate `ufw deny` suggestion | Text snippet | `ufw delete` equivalent rule |
| Export findings JSON/SARIF | Read-only | N/A |

## Out of scope for auto-fix (human required)

- Disabling OS services remotely across fleet
- Changing router ACLs without device API integration and tests
- Credential rotation on third-party SaaS
- Patch installation (use WSUS/Intune/patch management)

## LAB_MODE

When `LAB_MODE=true` on the server:

- Enables registration of **aggressive** plugins (e.g., future password spraying harness) if separately enabled in UI.
- Does **not** bypass authorization acknowledgment.

## Future

- Signed **remediation plugins** with capability manifests.
- Integration with ticketing (Jira/ServiceNow) for approval gates.
