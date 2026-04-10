@echo off
REM === Use this file by DOUBLE-CLICKING it (or run in cmd.exe). ===
REM Do NOT paste these lines into PowerShell — they are not PowerShell commands.
REM From PowerShell instead:  cd to this folder, then:  .\Start-Security-Console.ps1
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-security-console.ps1"
