# Stops whatever is listening on dev ports (Vite 5173, API 8000).
$ports = @(5173, 8000)
foreach ($port in $ports) {
    try {
        $listeners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    } catch {
        $listeners = @()
    }
    if (-not $listeners) {
        Write-Host "Nothing listening on port $port."
        continue
    }
    $procIds = $listeners | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($procId in $procIds) {
        try {
            $p = Get-Process -Id $procId -ErrorAction SilentlyContinue
            if ($p) {
                Write-Host "Stopping $($p.ProcessName) (PID $procId) on port $port"
                Stop-Process -Id $procId -Force -ErrorAction Stop
            }
        } catch {
            Write-Warning "Could not stop PID $procId : $_"
        }
    }
}

Write-Host "Done. Ports 5173 and 8000 should be free."
