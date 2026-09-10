#!/bin/bash
# Right-click this file in Finder -> Open. You do not need to type commands.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

# Finder does not use the same PATH as Terminal. Add the usual install locations.
export PATH="/usr/local/bin:/opt/homebrew/bin:/opt/homebrew/opt/node/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${HOME}/.local/bin:${PATH}"

pause() {
  echo ""
  echo "Press Return to close this window."
  read -r _
}

fail() {
  echo ""
  echo "$1"
  echo ""
  echo "Safari cannot open the app until this window is running without errors."
  pause
  exit 1
}

if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
  fail "Python is not installed. Open https://www.python.org/downloads/ , install it, then open this file again."
fi
if ! command -v npm >/dev/null 2>&1; then
  fail "Node.js is not installed (that program provides npm). Open https://nodejs.org/ , install it, then open this file again. Quit this window first."
fi
if ! command -v nmap >/dev/null 2>&1; then
  echo "Nmap was not found. Port scans will not work until you install it from https://nmap.org/download.html"
  echo "Certificate and HTTP header checks still work."
  echo ""
fi

echo "Leave this window open. Safari will open by itself when the app is ready."
echo "The first start can take a few minutes. If Safari says it cannot connect, wait or read this window."
echo ""

if [ ! -d node_modules/concurrently ]; then
  echo "Installing JavaScript packages..."
  npm install || fail "npm install failed. Confirm Node.js is installed, then try again."
fi

if [ ! -d .venv ]; then
  python3 -m venv .venv 2>/dev/null || python -m venv .venv || fail "Could not create a Python environment. Install Python from python.org."
fi
# shellcheck disable=SC1091
source .venv/bin/activate || fail "Could not start the Python environment."
python -m pip install -q -r backend/requirements.txt || fail "Could not install Python packages."

npm run dev:full &
DEV_PID=$!

ready=0
i=0
while [ "$i" -lt 180 ]; do
  if ! kill -0 "$DEV_PID" 2>/dev/null; then
    fail "The app stopped before it was ready. Scroll up in this window for the error."
  fi
  api_ok=0
  web_ok=0
  curl -sf "http://127.0.0.1:8000/health" >/dev/null 2>&1 && api_ok=1
  curl -sf "http://127.0.0.1:5173/" >/dev/null 2>&1 && web_ok=1
  curl -sf "http://localhost:5173/" >/dev/null 2>&1 && web_ok=1
  if [ "$api_ok" -eq 1 ] && [ "$web_ok" -eq 1 ]; then
    ready=1
    break
  fi
  sleep 1
  i=$((i + 1))
done

if [ "$ready" -ne 1 ]; then
  kill "$DEV_PID" 2>/dev/null || true
  fail "The app did not become ready in time. Keep this window open and read the lines above. Do not use Safari until this works."
fi

echo "Ready. Opening the app. If the page fails, try http://localhost:5173 then http://127.0.0.1:5173 (same app)."
open "http://localhost:5173/"
wait "$DEV_PID"
pause
