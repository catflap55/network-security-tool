# From PowerShell, you can also run this file inside the Windows folder:
#   .\Stop.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$inner = Join-Path $RepoRoot "scripts\stop-security-console.ps1"
if (-not (Test-Path $inner)) {
    Write-Error "Missing scripts\stop-security-console.ps1 - keep this file inside the Windows folder of the unzipped app."
    exit 1
}
& $inner
