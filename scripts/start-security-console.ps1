# Start API + Vite in a new window, wait until ready, open the UI in your browser.
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $RepoRoot "package.json"))) {
    Write-Error "Could not find repo root (no package.json next to scripts/)."
    exit 1
}

Set-Location $RepoRoot

$winTitle = "Security Console — web + API (close this window to stop both)"
Start-Process powershell -WorkingDirectory $RepoRoot -ArgumentList @(
    "-NoExit",
    "-NoProfile",
    "-Command",
    "`$host.ui.RawUI.WindowTitle = '$winTitle'; npm run dev:full"
)

Write-Host "Starting servers in a new window..."
Write-Host "Waiting for http://127.0.0.1:8000 and :5173 ..."

$deadline = (Get-Date).AddSeconds(90)
$apiOk = $false
$webOk = $false
while ((Get-Date) -lt $deadline) {
    if (-not $apiOk) {
        try {
            Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 2 | Out-Null
            $apiOk = $true
        } catch {}
    }
    if (-not $webOk) {
        try {
            Invoke-WebRequest -Uri "http://127.0.0.1:5173/" -UseBasicParsing -TimeoutSec 2 | Out-Null
            $webOk = $true
        } catch {}
    }
    if ($apiOk -and $webOk) { break }
    Start-Sleep -Milliseconds 600
}

if ($apiOk -and $webOk) {
    Start-Process "http://127.0.0.1:5173/"
    Write-Host "Opened http://127.0.0.1:5173/ — use Stop-Security-Console to shut down ports 5173 and 8000."
} else {
    Write-Warning "Servers did not respond in time. Check the other PowerShell window for errors."
    Write-Host "Opening the page anyway — refresh if it loads empty."
    Start-Process "http://127.0.0.1:5173/"
}
