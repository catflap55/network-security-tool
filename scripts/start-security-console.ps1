# Start API + Vite in a new window, wait until ready, open the UI in your browser.
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $RepoRoot "package.json"))) {
    Write-Error "Could not find repo root (no package.json next to scripts/). Open the unzipped app, go into the Windows folder, then double-click Start.cmd."
    exit 1
}

Set-Location $RepoRoot

function Assert-Runnable([string]$name, [string]$arg, [string]$hint) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Write-Error "Cannot find '$name' on PATH. $hint Close this window, open a new one after installing, and try again."
        exit 1
    }
    & $name $arg 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Found '$name' but it did not run (exit $LASTEXITCODE). $hint On Windows, turn off the Microsoft Store python alias: Settings -> Apps -> Advanced app settings -> App execution aliases -> off for python.exe."
        exit 1
    }
}

Assert-Runnable python "--version" "Install Python 3.11+ from https://www.python.org/downloads/ and tick 'Add python.exe to PATH'."
Assert-Runnable npm "--version" "Install Node.js 20+ from https://nodejs.org/ (that installer includes npm)."

if (-not (Get-Command nmap -ErrorAction SilentlyContinue)) {
    Write-Warning "nmap was not found on PATH. Nmap checks will fail until you install it from https://nmap.org/download.html (the API also looks in Program Files). TLS and HTTP header checks still work."
}

if (-not (Test-Path (Join-Path $RepoRoot "node_modules\concurrently"))) {
    Write-Host "First run: installing JavaScript packages (npm install). This can take a minute..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Error "npm install failed. Confirm Node.js 20+ is installed, then try Start.cmd again."
        exit 1
    }
}

$winTitle = "Security Console - web + API (close this window to stop both)"
Start-Process powershell -WorkingDirectory $RepoRoot -ArgumentList @(
    "-NoExit",
    "-NoProfile",
    "-Command",
    "`$host.ui.RawUI.WindowTitle = '$winTitle'; npm run dev:full"
)

Write-Host "Starting servers in a new window..."
Write-Host "Waiting for http://127.0.0.1:8000 and :5173 ..."

$deadline = (Get-Date).AddSeconds(180)
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
        if (-not $webOk) {
            try {
                Invoke-WebRequest -Uri "http://localhost:5173/" -UseBasicParsing -TimeoutSec 2 | Out-Null
                $webOk = $true
            } catch {}
        }
    }
    if ($apiOk -and $webOk) { break }
    Start-Sleep -Milliseconds 600
}

if (-not ($apiOk -and $webOk)) {
    Write-Error "The console did not become ready in time. Look at the other PowerShell window for the real error (python, npm, or pip). Keep that window open."
    exit 1
}

Write-Host "App is up. Try http://127.0.0.1:5173/ and http://localhost:5173/ (same app). Stop with Windows\Stop.cmd."
try {
    Start-Process "http://127.0.0.1:5173/"
} catch {
    try {
        Start-Process "http://localhost:5173/"
    } catch {
        Write-Host "Servers are running. In the browser open http://localhost:5173 or http://127.0.0.1:5173"
    }
}
