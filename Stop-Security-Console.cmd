@echo off
REM === Double-click this file (or run in cmd.exe). NOT for pasting into PowerShell. ===
REM From PowerShell:  cd to this folder, then:  .\Stop-Security-Console.ps1
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\stop-security-console.ps1"
