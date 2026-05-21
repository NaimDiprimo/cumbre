"""Tests de integración para los endpoints CRUD de servicios (/v1/services)."""

VALID_PAYLOAD = {
    "name": "test-service",
    "team": "platform",
    "upstream_host": "api.example.com",
    "upstream_port": 8080,
    "public_path": "/test",
    "requires_auth": False,
    "rate_limit_rpm": 100,
}


# ---------------------------------------------------------------------------
# POST /v1/services
# ---------------------------------------------------------------------------

def test_crear_servicio_valido(client):
    r = client.post("/v1/services", json=VALID_PAYLOAD)
    assert r.status_code == 202
    body = r.json()
    assert body["name"] == "test-service"
    assert body["team"] == "platform"
    assert body["status"] == "pending"
    assert "id" in body
    assert "created_at" in body


def test_crear_servicio_nombre_duplicado(client):
    client.post("/v1/services", json=VALID_PAYLOAD)
    r = client.post("/v1/services", json=VALID_PAYLOAD)
    assert r.status_code == 409
    assert "test-service" in r.json()["detail"]


def test_crear_servicio_devuelve_campos_completos(client):
    r = client.post("/v1/services", json=VALID_PAYLOAD)
    assert r.status_code == 202
    body = r.json()
    expected_keys = {
        "id", "name", "team", "description", "upstream_host", "upstream_port",
        "public_path", "requires_auth", "rate_limit_rpm", "status",
        "last_error", "labels", "created_at", "updated_at",
    }
    assert expected_keys.issubset(body.keys())


def test_crear_servicio_con_labels(client):
    payload = {**VALID_PAYLOAD, "labels": {"env": "staging", "owner": "alice"}}
    r = client.post("/v1/services", json=payload)
    assert r.status_code == 202
    assert r.json()["labels"] == {"env": "staging", "owner": "alice"}


def test_crear_servicio_con_descripcion(client):
    payload = {**VALID_PAYLOAD, "description": "Servicio de pagos"}
    r = client.post("/v1/services", json=payload)
    assert r.status_code == 202
    assert r.json()["description"] == "Servicio de pagos"


# ---------------------------------------------------------------------------
# GET /v1/services
# ---------------------------------------------------------------------------

def test_listar_servicios_vacio(client):
    r = client.get("/v1/services")
    assert r.status_code == 200
    assert r.json() == []


def test_listar_servicios_con_datos(client):
    payload_a = {**VALID_PAYLOAD, "name": "servicio-alpha"}
    payload_b = {**VALID_PAYLOAD, "name": "servicio-beta", "team": "data"}
    client.post("/v1/services", json=payload_a)
    client.post("/v1/services", json=payload_b)

    r = client.get("/v1/services")
    assert r.status_code == 200
    names = {s["name"] for s in r.json()}
    assert names == {"servicio-alpha", "servicio-beta"}


def test_filtrar_por_equipo(client):
    client.post("/v1/services", json={**VALID_PAYLOAD, "name": "svc-plat", "team": "platform"})
    client.post("/v1/services", json={**VALID_PAYLOAD, "name": "svc-data", "team": "data"})

    r = client.get("/v1/services", params={"team": "platform"})
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["name"] == "svc-plat"


def test_filtrar_por_equipo_sin_resultados(client):
    client.post("/v1/services", json={**VALID_PAYLOAD, "name": "svc-plat", "team": "platform"})

    r = client.get("/v1/services", params={"team": "equipo-inexistente"})
    assert r.status_code == 200
    assert r.json() == []


def test_filtrar_por_status(client):
    client.post("/v1/services", json={**VALID_PAYLOAD, "name": "svc-pending"})

    r = client.get("/v1/services", params={"status": "pending"})
    assert r.status_code == 200
    assert len(r.json()) == 1

    r2 = client.get("/v1/services", params={"status": "ready"})
    assert r2.status_code == 200
    assert r2.json() == []


def test_listar_ordenado_por_fecha_desc(client):
    client.post("/v1/services", json={**VALID_PAYLOAD, "name": "svc-primero"})
    client.post("/v1/services", json={**VALID_PAYLOAD, "name": "svc-segundo"})

    r = client.get("/v1/services")
    names = [s["name"] for s in r.json()]
    # El más reciente debe aparecer primero
    assert names[0] == "svc-segundo"


# ---------------------------------------------------------------------------
# GET /v1/services/{id}
# ---------------------------------------------------------------------------

def test_obtener_servicio_por_id(client):
    created = client.post("/v1/services", json=VALID_PAYLOAD).json()
    service_id = created["id"]

    r = client.get(f"/v1/services/{service_id}")
    assert r.status_code == 200
    assert r.json()["id"] == service_id
    assert r.json()["name"] == "test-service"


def test_obtener_servicio_no_existe(client):
    r = client.get("/v1/services/id-que-no-existe")
    assert r.status_code == 404
    assert "detail" in r.json()


# ---------------------------------------------------------------------------
# PATCH /v1/services/{id}
# ---------------------------------------------------------------------------

def test_actualizar_servicio(client):
    created = client.post("/v1/services", json=VALID_PAYLOAD).json()
    service_id = created["id"]

    r = client.patch(
        f"/v1/services/{service_id}",
        json={"description": "Descripción actualizada", "rate_limit_rpm": 200},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["description"] == "Descripción actualizada"
    assert body["rate_limit_rpm"] == 200
    # El update cambia el status a provisioning
    assert body["status"] == "provisioning"


def test_actualizar_servicio_no_existe(client):
    r = client.patch("/v1/services/id-inexistente", json={"rate_limit_rpm": 50})
    assert r.status_code == 404


def test_actualizar_servicio_parcial(client):
    """PATCH solo modifica los campos enviados, el resto queda igual."""
    created = client.post("/v1/services", json={**VALID_PAYLOAD, "rate_limit_rpm": 300}).json()
    service_id = created["id"]

    r = client.patch(f"/v1/services/{service_id}", json={"requires_auth": True})
    assert r.status_code == 200
    body = r.json()
    assert body["requires_auth"] is True
    assert body["rate_limit_rpm"] == 300  # no cambia


# ---------------------------------------------------------------------------
# DELETE /v1/services/{id}
# ---------------------------------------------------------------------------

def test_eliminar_servicio(client):
    created = client.post("/v1/services", json=VALID_PAYLOAD).json()
    service_id = created["id"]

    r = client.delete(f"/v1/services/{service_id}")
    assert r.status_code == 202
    body = r.json()
    assert body["id"] == service_id
    assert "detail" in body


def test_eliminar_servicio_no_existe(client):
    r = client.delete("/v1/services/id-inexistente")
    assert r.status_code == 404


def test_eliminar_cambia_status_a_deleting(client):
    created = client.post("/v1/services", json=VALID_PAYLOAD).json()
    service_id = created["id"]

    client.delete(f"/v1/services/{service_id}")

    r = client.get(f"/v1/services/{service_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "deleting"


# ---------------------------------------------------------------------------
# GET /v1/queue
# ---------------------------------------------------------------------------

def test_queue_status(client):
    r = client.get("/v1/queue")
    assert r.status_code == 200
    body = r.json()
    assert "depth" in body
    assert body["depth"] == 0
