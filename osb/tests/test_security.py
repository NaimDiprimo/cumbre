"""Tests de seguridad: SSRF, validaciones de esquema, path traversal."""

VALID_PAYLOAD = {
    "name": "test-service",
    "team": "platform",
    "upstream_host": "api.example.com",
    "upstream_port": 8080,
    "public_path": "/test",
    "requires_auth": False,
    "rate_limit_rpm": 100,
}


def _post(client, overrides: dict, name: str = "test-service"):
    """Helper: crea un payload con overrides y hace POST."""
    payload = {**VALID_PAYLOAD, "name": name, **overrides}
    return client.post("/v1/services", json=payload)


# ---------------------------------------------------------------------------
# SSRF — hostnames internos bloqueados
# ---------------------------------------------------------------------------

def test_ssrf_bloquea_redis(client):
    r = _post(client, {"upstream_host": "redis"})
    assert r.status_code == 422


def test_ssrf_bloquea_postgres(client):
    r = _post(client, {"upstream_host": "postgres"})
    assert r.status_code == 422


def test_ssrf_bloquea_sovereign(client):
    r = _post(client, {"upstream_host": "sovereign"})
    assert r.status_code == 422


def test_ssrf_bloquea_localhost(client):
    r = _post(client, {"upstream_host": "localhost"})
    assert r.status_code == 422


def test_ssrf_bloquea_metadata_google(client):
    r = _post(client, {"upstream_host": "metadata.google.internal"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# SSRF — IPs privadas / de loopback
# ---------------------------------------------------------------------------

def test_ssrf_bloquea_ip_privada_10(client):
    r = _post(client, {"upstream_host": "10.0.0.1"})
    assert r.status_code == 422


def test_ssrf_bloquea_ip_privada_192(client):
    r = _post(client, {"upstream_host": "192.168.1.100"})
    assert r.status_code == 422


def test_ssrf_bloquea_ip_privada_172(client):
    r = _post(client, {"upstream_host": "172.16.0.1"})
    assert r.status_code == 422


def test_ssrf_bloquea_ip_localhost(client):
    r = _post(client, {"upstream_host": "127.0.0.1"})
    assert r.status_code == 422


def test_ssrf_bloquea_ip_loopback_ipv6(client):
    r = _post(client, {"upstream_host": "::1"})
    assert r.status_code == 422


def test_ssrf_bloquea_link_local(client):
    r = _post(client, {"upstream_host": "169.254.169.254"})
    assert r.status_code == 422


def test_ssrf_permite_host_externo(client):
    r = _post(client, {"upstream_host": "api.stripe.com"})
    assert r.status_code == 202


def test_ssrf_permite_otro_host_externo(client):
    r = _post(client, {"upstream_host": "payments.example.org"})
    assert r.status_code == 202


# ---------------------------------------------------------------------------
# Validación de nombre (NameStr: min_length=3, pattern=^[a-z][a-z0-9-]*$)
# ---------------------------------------------------------------------------

def test_nombre_muy_corto(client):
    """Nombres de menos de 3 chars deben ser rechazados."""
    r = _post(client, {"name": "ab"})
    assert r.status_code == 422


def test_nombre_con_mayusculas(client):
    r = _post(client, {"name": "MyService"})
    assert r.status_code == 422


def test_nombre_con_espacios(client):
    r = _post(client, {"name": "my service"})
    assert r.status_code == 422


def test_nombre_con_guion_bajo(client):
    """El patrón solo permite letras minúsculas, dígitos y guion medio."""
    r = _post(client, {"name": "my_service"})
    assert r.status_code == 422


def test_nombre_empieza_con_digito(client):
    """El patrón ^[a-z] exige que empiece con letra minúscula."""
    r = _post(client, {"name": "1service"})
    assert r.status_code == 422


def test_nombre_valido_con_guion(client):
    r = _post(client, {"name": "mi-servicio-99"})
    assert r.status_code == 202


# ---------------------------------------------------------------------------
# Validación de public_path
# ---------------------------------------------------------------------------

def test_public_path_traversal(client):
    r = _post(client, {"public_path": "/../etc/passwd"})
    assert r.status_code == 422


def test_public_path_doble_slash(client):
    r = _post(client, {"public_path": "//admin"})
    assert r.status_code == 422


def test_public_path_sin_slash(client):
    r = _post(client, {"public_path": "api"})
    assert r.status_code == 422


def test_public_path_dotdot_en_medio(client):
    r = _post(client, {"public_path": "/api/../admin"})
    assert r.status_code == 422


def test_public_path_valido(client):
    r = _post(client, {"public_path": "/api/v2/payments"})
    assert r.status_code == 202


# ---------------------------------------------------------------------------
# Validación de labels
# ---------------------------------------------------------------------------

def test_labels_mas_de_10_claves(client):
    labels = {f"key{i}": f"val{i}" for i in range(11)}
    r = _post(client, {"labels": labels})
    assert r.status_code == 422


def test_labels_exactamente_10_claves(client):
    labels = {f"key{i}": f"val{i}" for i in range(10)}
    r = _post(client, {"labels": labels})
    assert r.status_code == 202


def test_labels_clave_muy_larga(client):
    labels = {"x" * 65: "valor"}
    r = _post(client, {"labels": labels})
    assert r.status_code == 422


def test_labels_valor_muy_largo(client):
    labels = {"clave": "v" * 65}
    r = _post(client, {"labels": labels})
    assert r.status_code == 422


def test_labels_vacio_es_valido(client):
    r = _post(client, {"labels": {}})
    assert r.status_code == 202


# ---------------------------------------------------------------------------
# Validación de upstream_port
# ---------------------------------------------------------------------------

def test_upstream_port_fuera_de_rango_cero(client):
    r = _post(client, {"upstream_port": 0})
    assert r.status_code == 422


def test_upstream_port_fuera_de_rango_alto(client):
    r = _post(client, {"upstream_port": 65536})
    assert r.status_code == 422


def test_upstream_port_valido_minimo(client):
    r = _post(client, {"upstream_port": 1})
    assert r.status_code == 202


def test_upstream_port_valido_maximo(client):
    r = _post(client, {"upstream_port": 65535, "name": "svc-port-max"})
    assert r.status_code == 202


# ---------------------------------------------------------------------------
# Validación de description
# ---------------------------------------------------------------------------

def test_description_muy_larga(client):
    r = _post(client, {"description": "x" * 501})
    assert r.status_code == 422


def test_description_exactamente_500_chars(client):
    r = _post(client, {"description": "x" * 500})
    assert r.status_code == 202


def test_description_nula_es_valida(client):
    r = _post(client, {"description": None})
    assert r.status_code == 202


# ---------------------------------------------------------------------------
# Validación de rate_limit_rpm
# ---------------------------------------------------------------------------

def test_rate_limit_rpm_cero(client):
    r = _post(client, {"rate_limit_rpm": 0})
    assert r.status_code == 422


def test_rate_limit_rpm_negativo(client):
    r = _post(client, {"rate_limit_rpm": -1})
    assert r.status_code == 422


def test_rate_limit_rpm_sobre_maximo(client):
    r = _post(client, {"rate_limit_rpm": 1_000_001})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Validación de team
# ---------------------------------------------------------------------------

def test_team_muy_corto(client):
    r = _post(client, {"team": "x"})
    assert r.status_code == 422


def test_team_valido_minimo(client):
    r = _post(client, {"team": "ab"})
    assert r.status_code == 202
