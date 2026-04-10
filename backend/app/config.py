import os
import shutil
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Always resolve .env next to the backend package (works when cwd is repo root).
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Security Console"
    data_dir: Path = Path(__file__).resolve().parent.parent.parent / "data"
    database_url: str = "sqlite:///./data/console.db"
    host: str = "127.0.0.1"
    port: int = 8000
    lab_mode: bool = False
    nmap_path: str = Field(
        default="nmap",
        validation_alias=AliasChoices("NMAP_PATH", "nmap_path"),
    )
    job_timeout_seconds: int = 3600


def get_settings() -> Settings:
    return Settings()


def resolve_nmap_path() -> str:
    """Return an nmap executable path: env/config, PATH, then common Windows installs."""
    raw = get_settings().nmap_path.strip() or "nmap"
    p = Path(raw)
    if p.is_file():
        return str(p.resolve())

    w = shutil.which(raw)
    if w:
        return w

    if os.name == "nt":
        candidates = [
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Nmap" / "nmap.exe",
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Nmap" / "nmap.exe",
        ]
        for c in candidates:
            if c.is_file():
                return str(c.resolve())

    return raw
