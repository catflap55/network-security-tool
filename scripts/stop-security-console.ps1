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
    $pids = $listeners | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid in $pids) {
        try {
            $p = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($p) {
                Write-Host "Stopping $($p.ProcessName) (PID $pid) on port $port"
                Stop-Process -Id $pid -Force -ErrorAction Stop
            }
        } catch {
            Write-Warning "Could not stop PID $pid : $_"
        }
    }
}

Write-Host "Done. Ports 5173 and 8000 should be free."
