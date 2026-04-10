# One-off helper: list folders under paths that look like git repos
$paths = @(
    'C:\Users\kelvi\.cursor\worktrees',
    'C:\Users\kelvi\Documents',
    'C:\Users\kelvi\source',
    'C:\Users\kelvi\Projects',
    'C:\Users\kelvi\repos',
    'C:\Users\kelvi\dev',
    'C:\Users\kelvi\github'
)
$found = [System.Collections.Generic.HashSet[string]]::new()
foreach ($base in $paths) {
    if (-not (Test-Path $base)) { continue }
    Get-ChildItem -Path $base -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $p = $_.FullName
        $git = Join-Path $p '.git'
        if (-not (Test-Path $git)) { return }
        Push-Location $p
        try {
            $remote = git remote get-url origin 2>$null
        } finally {
            Pop-Location
        }
        if ($found.Add($p)) {
            [PSCustomObject]@{ Path = $p; Origin = $remote }
        }
    }
}
