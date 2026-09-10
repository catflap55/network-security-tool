const { spawnSync } = require("node:child_process");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const req = path.join("backend", "requirements.txt");

function findPython() {
  const names = process.platform === "win32" ? ["python", "python3"] : ["python3", "python"];
  for (const name of names) {
    const r = spawnSync(name, ["-c", "import sys"], { encoding: "utf8" });
    if (r.status === 0) return name;
  }
  return null;
}

function run(py, args) {
  const r = spawnSync(py, args, { stdio: "inherit", cwd: root, shell: false });
  if (r.error) {
    console.error(`Could not run ${py}: ${r.error.message}`);
    process.exit(1);
  }
  if (r.status !== 0) process.exit(r.status ?? 1);
}

const py = findPython();
if (!py) {
  console.error(
    "Python was not found. Install Python 3.11+ from https://www.python.org/downloads/ (Windows: tick Add python.exe to PATH), then try again.",
  );
  process.exit(1);
}

run(py, ["-m", "pip", "install", "-q", "-r", req]);
if (process.argv.includes("--install-only")) process.exit(0);
run(py, [
  "-m",
  "uvicorn",
  "app.main:app",
  "--reload",
  "--host",
  "127.0.0.1",
  "--port",
  "8000",
  "--app-dir",
  "backend",
]);
