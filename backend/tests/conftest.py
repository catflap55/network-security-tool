import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_tmp = tempfile.mkdtemp(prefix="sc-test-")
os.environ["CONSOLE_TOKEN"] = "pytest-console-token"
os.environ["DATA_DIR"] = _tmp
os.environ["LAB_MODE"] = "false"
os.environ["HOST"] = "127.0.0.1"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth() -> dict[str, str]:
    return {"X-Console-Token": "pytest-console-token"}
