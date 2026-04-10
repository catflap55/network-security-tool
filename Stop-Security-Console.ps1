# Run from THIS repo folder in PowerShell:
#   cd C:\path\to\security-tool
#   .\Stop-Security-Console.ps1

$ErrorActionPreference = "Stop"
$inner = Join-Path $PSScriptRoot "scripts\stop-security-console.ps1"
if (-not (Test-Path $inner)) {
    Write-Error "Missing scripts\stop-security-console.ps1 — run from the security-tool repo root."
    exit 1
}
& $inner
