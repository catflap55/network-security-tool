#!/bin/bash
# Open the Linux folder, then run this file (Run in Terminal).
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

fail() {
  echo ""
  echo "$1"
  echo "Press Enter to close."
  read -r _
  exit 1
}

command -v python3 >/dev/null 2>&1 || fail "Install Python 3 first (see the Linux section of README.md)."
command -v npm >/dev/null 2>&1 || fail "Install Node.js / npm first (see the Linux section of README.md)."

if [ ! -d .venv ]; then
  python3 -m venv .venv || fail "Could not create a Python environment. Install python3-venv."
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -q -r backend/requirements.txt || fail "Could not install Python packages."
if [ ! -d node_modules/concurrently ]; then
  npm install || fail "npm install failed."
fi
npm run dev:full &
DEV_PID=$!
echo "Leave this window open. The browser will open when the app is ready."
ready=0
i=0
while [ "$i" -lt 180 ]; do
  if ! kill -0 "$DEV_PID" 2>/dev/null; then
    fail "The app stopped before it was ready. Scroll up for the error."
  fi
  api_ok=0
  web_ok=0
  curl -sf "http://127.0.0.1:8000/health" >/dev/null 2>&1 && api_ok=1
  curl -sf "http://127.0.0.1:5173/" >/dev/null 2>&1 && web_ok=1
  if [ "$api_ok" -eq 1 ] && [ "$web_ok" -eq 1 ]; then
    ready=1
    break
  fi
  sleep 1
  i=$((i + 1))
done
if [ "$ready" -ne 1 ]; then
  kill "$DEV_PID" 2>/dev/null || true
  fail "The app did not become ready. Read the lines above."
fi
xdg-open "http://127.0.0.1:5173/" >/dev/null 2>&1 || true
wait "$DEV_PID"
echo "Press Enter to close."
read -r _
