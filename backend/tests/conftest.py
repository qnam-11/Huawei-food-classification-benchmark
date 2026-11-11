import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def checkpoints_present() -> bool:
    if not settings.models_path.exists():
        return False
    entries = json.loads(settings.models_path.read_text(encoding="utf-8"))
    return all(settings.resolve(entry["path"]).exists() for entry in entries)


@pytest.fixture(scope="session")
def client():
    if not checkpoints_present():
        pytest.skip("checkpoints not present")
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def kb():
    from app.services.knowledge_base import KnowledgeBase

    return KnowledgeBase(settings.kb_file)
