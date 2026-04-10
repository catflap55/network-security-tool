from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings


def _sqlite_url() -> str:
    s = get_settings()
    s.data_dir.mkdir(parents=True, exist_ok=True)
    db_path = s.data_dir / "console.db"
    return f"sqlite:///{db_path.as_posix()}"


engine = create_engine(
    _sqlite_url(),
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
