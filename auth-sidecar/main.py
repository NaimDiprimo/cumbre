"""Auth sidecar hardened — valida JWTs + blacklist de tokens revocados.

Envoy invoca este servicio vía ext_authz HTTP.
Respuestas:
  200 OK  => permite el request
  401     => no autenticado / token inválido
  403     => autenticado pero token revocado (blacklist)
  429     => rate limit excedido
"""
import logging
import os
import hashlib
import time
from typing import Optional

import jwt
import redis as redis_client
from fastapi import FastAPI, Header, HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

# ── Config ────────────────────────────────────────────────
JWT_SECRET_ENV = os.getenv("CUMBRE_JWT_SECRET", "")
JWT_ALGORITHMS = ["HS256"]
REDIS_URL = os.getenv("CUMBRE_REDIS_URL", "redis://redis:6379/1")  # DB 1, separate from OSB
MIN_SECRET_LENGTH = 32  # Enforce minimum secret strength

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s"
)
log = logging.getLogger("cumbre.auth")

# ── Startup validation ────────────────────────────────────
# El sidecar y el OSB tienen que compartir exactamente el mismo secreto: uno
# firma los tokens y el otro los valida. Si no coinciden, la auth se rompe;
# si ambos caen al mismo default público, la auth es decorativa.
#
# Valores publicados en este repo. Sirven sólo para desarrollo local.
_SECRETOS_PUBLICOS = frozenset({
    "dev-only-secret-change-me-min-32-chars!!",
    "dev-only-secret-change-me",
    "cumbre-dev-change-in-prod",
    "change-me",
})
_ES_PRODUCTIVO = os.getenv("OSB_ENVIRONMENT", "dev").strip().lower() not in ("dev", "test")

if not JWT_SECRET_ENV:
    if _ES_PRODUCTIVO:
        raise RuntimeError(
            "CUMBRE_JWT_SECRET no está definida y OSB_ENVIRONMENT no es 'dev'. "
            "Sin secreto propio, cualquiera puede firmar tokens válidos."
        )
    log.warning(
        "CUMBRE_JWT_SECRET no está definida. Usando el secreto de desarrollo, "
        "que es público. NUNCA levantes esto en producción así."
    )
    # noqa justificado: es el default público de desarrollo, y el bloque de
    # arriba ya garantiza que nunca se llega acá en un entorno productivo.
    JWT_SECRET = "dev-only-secret-change-me-min-32-chars!!"  # noqa: S105
else:
    JWT_SECRET = JWT_SECRET_ENV

if _ES_PRODUCTIVO and JWT_SECRET in _SECRETOS_PUBLICOS:
    raise RuntimeError(
        "CUMBRE_JWT_SECRET tiene uno de los valores de ejemplo publicados en este "
        "repositorio. Es equivalente a no tener secreto."
    )

if len(JWT_SECRET) < MIN_SECRET_LENGTH:
    if _ES_PRODUCTIVO:
        raise RuntimeError(
            f"CUMBRE_JWT_SECRET tiene {len(JWT_SECRET)} caracteres; el mínimo es "
            f"{MIN_SECRET_LENGTH}."
        )
    log.warning(
        "CUMBRE_JWT_SECRET tiene menos de %d caracteres. "
        "Esto es inseguro para producción.", MIN_SECRET_LENGTH
    )

# ── Redis token blacklist ─────────────────────────────────
try:
    _redis = redis_client.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    _redis.ping()
    log.info("Redis blacklist conectado en %s", REDIS_URL)
    BLACKLIST_AVAILABLE = True
except Exception as e:
    log.warning("Redis blacklist no disponible (%s). Tokens no se pueden revocar.", e)
    _redis = None
    BLACKLIST_AVAILABLE = False


def _token_key(token: str) -> str:
    """Hash del token para guardarlo en Redis (no guardar token raw)."""
    return "auth:blacklist:" + hashlib.sha256(token.encode()).hexdigest()


def is_blacklisted(token: str) -> bool:
    if not BLACKLIST_AVAILABLE or _redis is None:
        return False
    try:
        return bool(_redis.exists(_token_key(token)))
    except Exception:
        return False  # Fail open: if Redis is down, don't block valid tokens


def blacklist_token(token: str, ttl_seconds: int = 86400) -> bool:
    """Agrega token a la blacklist con TTL igual al tiempo restante de expiración."""
    if not BLACKLIST_AVAILABLE or _redis is None:
        return False
    try:
        _redis.setex(_token_key(token), ttl_seconds, "1")
        return True
    except Exception as e:
        log.error("Error agregando token a blacklist: %s", e)
        return False

# ── Rate limiting ─────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── Security headers middleware ───────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Cache-Control"] = "no-store"
        return response

# ── FastAPI app ───────────────────────────────────────────
app = FastAPI(
    title="Cumbre Auth Sidecar",
    version="0.2.0",
    docs_url=None,   # Never expose docs - this is an internal service
    redoc_url=None,
    openapi_url=None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/revoke")
@limiter.limit("10/minute")
async def revoke_token(request: Request, authorization: Optional[str] = Header(default=None)):
    """Revoca el token del request actual. Solo para uso interno."""
    if authorization is None:
        raise HTTPException(status_code=400, detail="No hay token para revocar")
    token = authorization.removeprefix("Bearer ").removeprefix("bearer ").strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHMS)
        exp = payload.get("exp", 0)
        ttl = max(0, int(exp - time.time()))
    except Exception:
        ttl = 86400  # Default 24h if we can't decode

    ok = blacklist_token(token, ttl_seconds=ttl or 86400)
    return {"revoked": ok, "message": "Token revocado" if ok else "Blacklist no disponible"}


@app.api_route("/", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
@limiter.limit("300/minute")
async def authorize(request: Request, full_path: str = "", authorization: Optional[str] = Header(default=None)):
    """Envoy nos pega aquí con cada request. Validamos y devolvemos 200 o 401."""

    client_ip = request.client.host if request.client else "unknown"

    if authorization is None:
        log.info("DENY no_auth ip=%s path=%s", client_ip, full_path)
        raise HTTPException(status_code=401, detail="missing Authorization header")

    if not authorization.lower().startswith("bearer "):
        log.info("DENY bad_format ip=%s", client_ip)
        raise HTTPException(status_code=401, detail="malformed Authorization header")

    token = authorization.split(" ", 1)[1].strip()

    # Sanity check: JWT tokens have exactly 3 dot-separated parts
    if token.count(".") != 2:
        log.warning("DENY malformed_token ip=%s", client_ip)
        raise HTTPException(status_code=401, detail="malformed token")

    # Check blacklist BEFORE decoding (fast rejection)
    if is_blacklisted(token):
        log.warning("DENY blacklisted ip=%s", client_ip)
        raise HTTPException(status_code=403, detail="token revocado")

    # Decode and validate
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=JWT_ALGORITHMS,
            options={
                "require": ["exp", "iat", "sub"],  # Require essential claims
                "verify_exp": True,
                "verify_iat": True,
            }
        )
    except jwt.ExpiredSignatureError:
        log.info("DENY expired ip=%s", client_ip)
        raise HTTPException(status_code=401, detail="token expired")
    except jwt.MissingRequiredClaimError as e:
        log.warning("DENY missing_claim ip=%s claim=%s", client_ip, e)
        raise HTTPException(status_code=401, detail="token incompleto")
    except jwt.InvalidTokenError as e:
        log.warning("DENY invalid_token ip=%s err=%s", client_ip, type(e).__name__)
        raise HTTPException(status_code=401, detail="invalid token")

    sub = payload.get("sub", "")
    if not sub or len(sub) > 256:
        raise HTTPException(status_code=401, detail="token subject inválido")

    log.info("ALLOW sub=%s ip=%s path=%s", sub, client_ip, full_path)
    # Return minimal info — do NOT leak JWT payload details
    return {"authorized": True}
