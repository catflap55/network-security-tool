from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import ensure_console_token, require_console_token
from app.config import get_settings
from app.db import init_db
from app.routers import jobs, playbooks, plugins, projects, schedules, settings
from app.services.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_console_token()
    init_db()
    start_scheduler()
    yield


app = FastAPI(
    title=get_settings().app_name,
    description="Personal use only. Scan only a home network that you own. Do not scan work, school, public Wi-Fi, neighbours, clients, or the public internet.",
    lifespan=lifespan,
    dependencies=[Depends(require_console_token)],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_origin_regex=r"^http://(127\.0\.0\.1|localhost)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(settings.router)
app.include_router(plugins.router)
app.include_router(projects.router)
app.include_router(jobs.router)
app.include_router(playbooks.router)
app.include_router(schedules.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
