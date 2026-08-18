"""Tests de la interfaz web del OSB.

Existen porque una actualización de starlette rompió el renderizado de las
plantillas (cambió el orden de los argumentos de TemplateResponse) y la suite
no se dio cuenta: todos los tests pegaban a la API, ninguno al dashboard.

El dashboard es lo primero que ve un cliente en una demo. Si se rompe, tiene
que fallar un test, no la demo.
"""


def test_dashboard_renderiza(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_dashboard_muestra_los_servicios_creados(client):
    client.post(
        "/v1/services",
        json={
            "name": "servicio-visible",
            "team": "platform",
            "upstream_host": "backend",
            "upstream_port": 8080,
            "public_path": "/visible",
            "requires_auth": False,
            "rate_limit_rpm": 100,
        },
    )
    r = client.get("/")
    assert r.status_code == 200
    assert "servicio-visible" in r.text


def test_formulario_de_alta_renderiza(client):
    r = client.get("/ui/new")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_el_dashboard_manda_las_cabeceras_de_seguridad(client):
    r = client.get("/")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["Cache-Control"] == "no-store"


def test_entrada_de_demo_funciona_en_dev(client):
    r = client.get("/auth/dev/login", follow_redirects=False)
    assert r.status_code == 303
    assert "cumbre_token" in r.cookies


def test_entrada_de_demo_no_existe_en_produccion(client, monkeypatch):
    monkeypatch.setenv("OSB_ENVIRONMENT", "production")
    r = client.get("/auth/dev/login", follow_redirects=False)
    assert r.status_code == 404
