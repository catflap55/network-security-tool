from __future__ import annotations

import hmac
import secrets
from pathlib import Path

from fastapi import Header, HTTPException, Request, status

from app.config import get_settings

_PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


def ensure_console_token() -> str:
    """Return CONSOLE_TOKEN, generating and persisting one if missing."""
    s = get_settings()
    token = (s.console_token or "").strip()
    if token:
        return token
    token = secrets.token_urlsafe(32)
    env_path = Path(__file__).resolve().parent.parent / ".env"
    existing = env_path.read_text(encoding="utf-8") if env_path.is_file() else ""
    if "CONSOLE_TOKEN=" not in existing:
        with env_path.open("a", encoding="utf-8") as fh:
            if existing and not existing.endswith("\n"):
                fh.write("\n")
            fh.write(f"CONSOLE_TOKEN={token}\n")
    s.console_token = token
    print(
        "\n*** Security Console ***\n"
        "Generated CONSOLE_TOKEN and saved it to backend/.env\n"
        "Paste this token in the web UI (it is not committed to git):\n"
        f"  {token}\n"
    )
    return token


def extract_token(request: Request, x_console_token: str | None) -> str:
    if x_console_token:
        return x_console_token.strip()
    auth = request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return ""


def require_console_token(
    request: Request,
    x_console_token: str | None = Header(default=None, alias="X-Console-Token"),
) -> None:
    if request.url.path in _PUBLIC_PATHS or request.method == "OPTIONS":
        return
    expected = (get_settings().console_token or "").strip()
    if not expected:
        expected = ensure_console_token()
    provided = extract_token(request, x_console_token)
    if not provided or not hmac.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid console token. Open backend/.env, copy CONSOLE_TOKEN, and paste it in the UI.",
            headers={"WWW-Authenticate": "Bearer"},
        )
