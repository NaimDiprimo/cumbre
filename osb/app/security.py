"""Validaciones de seguridad que corren al arrancar el servicio.

La idea es que un despliegue mal configurado **no arranque**, en vez de
arrancar aparentemente bien y quedar abierto. Un servicio caído se nota en
cinco minutos; un servicio firmando tokens con un secreto público no se nota
hasta que es tarde.
"""
import logging
import os

log = logging.getLogger("cumbre.security")

LARGO_MINIMO_SECRETO = 32

# Valores que están publicados en este repo (en .env.example, en el Makefile y
# en la documentación). Sirven para desarrollo local y para nada más: cualquiera
# que lea el repo puede firmar tokens con ellos.
SECRETOS_PUBLICOS = frozenset({
    "dev-only-secret-change-me-min-32-chars!!",
    "dev-only-secret-change-me",
    "cumbre-dev-change-in-prod",
    "change-me",
})


def es_entorno_productivo() -> bool:
    """True salvo que estemos explícitamente en desarrollo o en tests."""
    return os.getenv("OSB_ENVIRONMENT", "dev").strip().lower() not in ("dev", "test")


def require_jwt_secret() -> str:
    """Devuelve el secreto de firma de JWT, o revienta si no sirve.

    En producción exige un secreto propio, largo y que no sea uno de los
    valores públicos del repo. En desarrollo deja seguir con un default, pero
    avisa por log.
    """
    secreto = os.getenv("CUMBRE_JWT_SECRET", "")
    productivo = es_entorno_productivo()

    if not secreto:
        if productivo:
            raise RuntimeError(
                "CUMBRE_JWT_SECRET no está definida y OSB_ENVIRONMENT no es 'dev'. "
                "Sin un secreto propio, cualquiera puede firmar tokens válidos. "
                "Generá uno con: python3 -c \"import secrets; print(secrets.token_hex(32))\""
            )
        log.warning(
            "CUMBRE_JWT_SECRET no está definida. Usando el secreto de desarrollo, "
            "que es público. NUNCA levantes esto en producción así."
        )
        return "dev-only-secret-change-me-min-32-chars!!"

    if productivo and secreto in SECRETOS_PUBLICOS:
        raise RuntimeError(
            "CUMBRE_JWT_SECRET tiene uno de los valores de ejemplo que están "
            "publicados en este repositorio. Es equivalente a no tener secreto. "
            "Generá uno propio con: "
            "python3 -c \"import secrets; print(secrets.token_hex(32))\""
        )

    if len(secreto) < LARGO_MINIMO_SECRETO:
        mensaje = (
            f"CUMBRE_JWT_SECRET tiene {len(secreto)} caracteres; el mínimo es "
            f"{LARGO_MINIMO_SECRETO}. Un secreto corto se puede romper por fuerza bruta."
        )
        if productivo:
            raise RuntimeError(mensaje)
        log.warning("%s (se permite porque el entorno es de desarrollo)", mensaje)

    return secreto
