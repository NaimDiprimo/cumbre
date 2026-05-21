"""Smoke tests del OSB.

Usa el fixture `client` de conftest.py (SQLite en memoria, Redis mockeado)
para que puedan correr sin Postgres ni Redis.
"""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_openapi_disponible(client):
    """El schema OpenAPI solo se expone en entorno dev.
    conftest.py setea OSB_ENVIRONMENT=dev antes de importar app.main,
    por lo que /openapi.json debe responder 200.
    """
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert spec["info"]["title"] == "Cumbre OSB"
    # Endpoints clave existen en el schema
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
