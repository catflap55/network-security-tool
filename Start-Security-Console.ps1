# Run from THIS repo folder in PowerShell:
#   cd C:\path\to\security-tool
#   .\Start-Security-Console.ps1
#
# Do not paste .cmd file lines here — those only work in Command Prompt / double-click.

$ErrorActionPreference = "Stop"
$inner = Join-Path $PSScriptRoot "scripts\start-security-console.ps1"
if (-not (Test-Path $inner)) {
    Write-Error "Missing scripts\start-security-console.ps1 — run from the security-tool repo root."
    exit 1
}
& $inner
