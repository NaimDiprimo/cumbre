"""Fixtures compartidos para la suite de tests del OSB.

Configuración:
- SQLite en memoria (sin Postgres ni Redis)
- Parchea app.database.engine para que init_db() use el mismo engine de test
- Sobreescribe get_db con una sesión de test aislada
- Mockea enqueue/queue_depth para que no toquen Redis
- Fuerza OSB_ENVIRONMENT=dev para que /openapi.json esté visible
"""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

os.environ.setdefault("OSB_ENVIRONMENT", "dev")
os.environ.setdefault("OSB_DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("OSB_REDIS_URL", "redis://localhost:6379/0")

from sqlalchemy.pool import StaticPool  # noqa: E402

import app.database as _app_db  # noqa: E402
from app.main import app  # noqa: E402
from app.database import Base, get_db  # noqa: E402


@pytest.fixture
def client():
    """TestClient con SQLite en memoria y Redis mockeado."""
    # StaticPool garantiza que todas las conexiones usen el mismo in-memory DB
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with patch.object(_app_db, "engine", engine), \
         patch.object(_app_db, "SessionLocal", TestSession), \
         patch("app.routers.services.enqueue"), \
         patch("app.routers.services.queue_depth", return_value=0), \
         patch("app.routers.ui.enqueue"), \
         patch("app.routers.ui.queue_depth", return_value=0):
        with TestClient(app) as c:
            yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
