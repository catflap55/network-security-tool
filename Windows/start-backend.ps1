# Starts FastAPI on http://127.0.0.1:8000 (API only).
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
if (-not (Test-Path "backend\app\main.py")) {
    Write-Error "Keep this file inside the Windows folder of the unzipped app."
}
Set-Location backend
$env:PYTHONPATH = "."
python -m pip install -q -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
