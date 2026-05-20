"""Auth sidecar — valida JWTs antes de dejar pasar el request al backend.

En la arquitectura de Vasilios este sidecar está escrito en Rust por performance.
Lo dejamos en Python para velocidad de iteración; tenemos un task abierto
para reescribirlo en Rust (ver docs/DECISIONES.md).

Envoy invoca este servicio vía ext_authz HTTP.
Convención:
  - 200 OK  => permite el request
  - 401     => no autenticado
  - 403     => autenticado pero no autorizado
"""
import logging
import os

import jwt
from fastapi import FastAPI, Header, HTTPException

JWT_SECRET = os.getenv("CUMBRE_JWT_SECRET", "dev-only-secret-change-me")
JWT_ALGORITHMS = ["HS256"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
log = logging.getLogger("cumbre.auth")

app = FastAPI(title="Cumbre Auth Sidecar", version="0.1.0")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.api_route("/", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
def authorize(full_path: str = "", authorization: str | None = Header(default=None)):
    """Envoy nos pega aquí con cada request. Validamos y devolvemos 200 o 401."""
    if authorization is None:
        log.info("Rechazado: sin header Authorization (path=%s)", full_path)
        raise HTTPException(status_code=401, detail="missing Authorization header")

    if not authorization.lower().startswith("bearer "):
        log.info("Rechazado: header mal formado")
        raise HTTPException(status_code=401, detail="malformed Authorization header")

    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHMS)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"invalid token: {e}")

    # Validaciones de negocio mínimas
    if "sub" not in payload:
        raise HTTPException(status_code=401, detail="token missing subject")

    log.info("Autorizado sub=%s path=%s", payload.get("sub"), full_path)
    return {"sub": payload["sub"]}
