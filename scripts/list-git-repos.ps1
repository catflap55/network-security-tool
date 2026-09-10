# Optional helper: list git repos under your user profile (no hardcoded usernames).
$roots = @(
    (Join-Path $env:USERPROFILE 'Documents'),
    (Join-Path $env:USERPROFILE 'source'),
    (Join-Path $env:USERPROFILE 'Projects'),
    (Join-Path $env:USERPROFILE 'repos'),
    (Join-Path $env:USERPROFILE 'dev'),
    (Join-Path $env:USERPROFILE 'github')
)
$found = [System.Collections.Generic.HashSet[string]]::new()
foreach ($base in $roots) {
    if (-not (Test-Path $base)) { continue }
    Get-ChildItem -Path $base -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $p = $_.FullName
        if (-not (Test-Path (Join-Path $p '.git'))) { return }
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
