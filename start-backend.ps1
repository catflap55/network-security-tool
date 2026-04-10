# Run from repo root. Starts FastAPI on http://127.0.0.1:8000
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path "backend\app\main.py")) {
    Write-Error "Run this script from the security-tool repo root."
}
Set-Location backend
$env:PYTHONPATH = "."
python -m pip install -q -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
