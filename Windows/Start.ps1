# From PowerShell, you can also run this file inside the Windows folder:
#   .\Start.ps1
#
# Do not paste .cmd file lines here - those only work in Command Prompt / double-click.

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$inner = Join-Path $RepoRoot "scripts\start-security-console.ps1"
if (-not (Test-Path $inner)) {
    Write-Error "Missing scripts\start-security-console.ps1 - keep this file inside the Windows folder of the unzipped app."
    exit 1
}
& $inner
