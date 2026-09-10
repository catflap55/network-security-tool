@echo off
REM Open the Windows folder, then double-click this file to stop the console.
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\scripts\stop-security-console.ps1"
if errorlevel 1 (
  echo.
  echo Stop did not finish. Read the message above.
  echo.
  echo Press any key to close this window.
  if not defined GITHUB_ACTIONS pause
  exit /b 1
)
