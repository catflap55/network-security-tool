import os
import shutil
from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Security Console"
    data_dir: Path = Field(
        default=Path(__file__).resolve().parent.parent.parent / "data",
        validation_alias=AliasChoices("DATA_DIR", "data_dir"),
    )
    database_url: str = "sqlite:///./data/console.db"
    host: str = "127.0.0.1"
    port: int = 8000
    lab_mode: bool = False
    nmap_path: str = Field(
        default="nmap",
        validation_alias=AliasChoices("NMAP_PATH", "nmap_path"),
    )
    job_timeout_seconds: int = 3600
    console_token: str = Field(default="", validation_alias=AliasChoices("CONSOLE_TOKEN", "console_token"))
    allow_nonlocal_bind: bool = False
    max_targets: int = 64
    max_cidr_hosts: int = 256
    max_concurrent_jobs: int = 2

    @field_validator("host")
    @classmethod
    def localhost_only(cls, v: str) -> str:
        raw = (v or "127.0.0.1").strip()
        allow = os.environ.get("ALLOW_NONLOCAL_BIND", "").lower() in ("1", "true", "yes")
        if raw not in ("127.0.0.1", "localhost", "::1") and not allow:
            raise ValueError(
                "API host must be 127.0.0.1 unless ALLOW_NONLOCAL_BIND=true "
                "(never expose this console on the internet without a reverse proxy and TLS)."
            )
        return raw


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
