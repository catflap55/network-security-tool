@echo off
REM Open the Windows folder, then double-click this file. Do not paste it into PowerShell.
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\scripts\start-security-console.ps1"
if errorlevel 1 (
  echo.
  echo The console did not start. Read the message above.
  echo If it mentioned python, install Python and tick Add python.exe to PATH.
  echo If it mentioned npm, install Node.js from https://nodejs.org/
  echo.
  echo Press any key to close this window.
  if not defined GITHUB_ACTIONS pause
  exit /b 1
)
