# Auto-fix policy

## Principles

1. **No silent production changes.** Any automated action must be **visible**, **confirmable**, and **reversible**.
2. **Allowlist only.** Only actions in the allowlist below may be offered as one-click or generated scripts.
3. **Audit.** Log who/when/what for any applied change (future RBAC; MVP: local operator).

## Allowlist

| Action | Form | Rollback |
|--------|------|----------|
| Generate Windows firewall block rule | PowerShell snippet in UI (copy/paste) | Operator removes rule by name |
| Generate `ufw deny` suggestion | Text snippet | `ufw delete` equivalent rule |
| Export findings JSON/SARIF | Read-only | N/A |

## Out of scope (human required)

- Disabling OS services remotely
- Changing router ACLs without a device API and tests
- Credential rotation on third-party SaaS
- Patch installation (use WSUS/Intune/patch management)
- Any credential guessing or exploit payload

## LAB_MODE

When `LAB_MODE=true` on the server:

- Unlocks **lab host discovery** (Nmap `-sn` inventory).
- Does **not** bypass authorization acknowledgment or the console token.
- Does **not** enable password spraying or similar attacks — those are not part of this project.
