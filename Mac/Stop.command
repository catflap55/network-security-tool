#!/bin/bash
# Right-click this file in Finder → Open to stop the console.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

echo "Stopping the Security Console..."
for port in 5173 8000; do
  pids=$(lsof -ti tcp:"$port" 2>/dev/null || true)
  if [ -n "$pids" ]; then
    # shellcheck disable=SC2086
    kill $pids 2>/dev/null || true
    echo "Stopped what was using port $port."
  else
    echo "Nothing was using port $port."
  fi
done
echo ""
echo "Done. You can close this window."
echo "Press Return to close."
read -r _
