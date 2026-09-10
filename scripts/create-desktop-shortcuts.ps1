# Run once: creates Desktop shortcuts with icons (optional).
$RepoRoot = Split-Path -Parent $PSScriptRoot
$desktop = [Environment]::GetFolderPath("Desktop")

$shell = New-Object -ComObject WScript.Shell

$start = Join-Path $desktop "Security Console (Start).lnk"
$s = $shell.CreateShortcut($start)
$s.TargetPath = "powershell.exe"
$s.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$(Join-Path $RepoRoot 'Windows\Start.ps1')`""
$s.WorkingDirectory = $RepoRoot
$s.Description = "Start web UI + API and open browser"
$s.IconLocation = "$env:SystemRoot\System32\shell32.dll,13"
$s.Save()

$stop = Join-Path $desktop "Security Console (Stop).lnk"
$t = $shell.CreateShortcut($stop)
$t.TargetPath = "powershell.exe"
$t.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$(Join-Path $RepoRoot 'Windows\Stop.ps1')`""
$t.WorkingDirectory = $RepoRoot
$t.Description = "Stop processes on ports 5173 and 8000"
$t.IconLocation = "$env:SystemRoot\System32\shell32.dll,28"
$t.Save()

Write-Host "Created:"
Write-Host "  $start"
Write-Host "  $stop"
