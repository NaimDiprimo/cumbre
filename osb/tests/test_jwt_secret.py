"""Tests del guard de arranque sobre el secreto de firma de JWT.

La regla que se prueba: en un entorno productivo, el servicio tiene que negarse
a arrancar si el secreto falta, es uno de los valores públicos del repo, o es
demasiado corto. En desarrollo, avisa pero deja seguir.
"""
import pytest

from app.security import es_entorno_productivo, require_jwt_secret

SECRETO_VALIDO = "a" * 64


def test_en_dev_sin_secreto_deja_arrancar(monkeypatch):
    monkeypatch.setenv("OSB_ENVIRONMENT", "dev")
    monkeypatch.delenv("CUMBRE_JWT_SECRET", raising=False)
    assert require_jwt_secret()  # devuelve el default de desarrollo


def test_en_produccion_sin_secreto_no_arranca(monkeypatch):
    monkeypatch.setenv("OSB_ENVIRONMENT", "production")
    monkeypatch.delenv("CUMBRE_JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="no está definida"):
        require_jwt_secret()


@pytest.mark.parametrize(
    "publico",
    [
        "dev-only-secret-change-me-min-32-chars!!",
        "dev-only-secret-change-me",
        "cumbre-dev-change-in-prod",
    ],
)
def test_en_produccion_rechaza_los_secretos_publicos_del_repo(monkeypatch, publico):
    monkeypatch.setenv("OSB_ENVIRONMENT", "production")
    monkeypatch.setenv("CUMBRE_JWT_SECRET", publico)
    with pytest.raises(RuntimeError):
        require_jwt_secret()


def test_en_produccion_rechaza_secreto_corto(monkeypatch):
    monkeypatch.setenv("OSB_ENVIRONMENT", "production")
    monkeypatch.setenv("CUMBRE_JWT_SECRET", "corto")
    with pytest.raises(RuntimeError, match="mínimo"):
        require_jwt_secret()


def test_en_produccion_acepta_secreto_propio_y_largo(monkeypatch):
    monkeypatch.setenv("OSB_ENVIRONMENT", "production")
    monkeypatch.setenv("CUMBRE_JWT_SECRET", SECRETO_VALIDO)
    assert require_jwt_secret() == SECRETO_VALIDO


@pytest.mark.parametrize(
    ("entorno", "esperado"),
    [("dev", False), ("test", False), ("DEV", False), ("production", True), ("staging", True)],
)
def test_deteccion_de_entorno_productivo(monkeypatch, entorno, esperado):
    monkeypatch.setenv("OSB_ENVIRONMENT", entorno)
    assert es_entorno_productivo() is esperado
