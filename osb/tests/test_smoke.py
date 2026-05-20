"""Smoke tests del OSB. Requieren Postgres + Redis arriba."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_openapi_disponible(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert spec["info"]["title"] == "Cumbre OSB"
    # Endpoints clave existen
    assert "/v1/services" in spec["paths"]
    assert "/health" in spec["paths"]


def test_validacion_de_nombres(client):
    bad = {
        "name": "MAYUSCULAS",
        "team": "x",
        "upstream_host": "h",
    }
    r = client.post("/v1/services", json=bad)
    assert r.status_code in (400, 422)
