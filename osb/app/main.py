"""Punto de entrada de la API HTTP del OSB."""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response, Response as StarletteResponse

from .config import settings
from .database import init_db
from .routers import health, services, ui

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("cumbre.osb")

# ---------------------------------------------------------------------------
# Rate limiter — 200 requests per minute per IP by default
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


# ---------------------------------------------------------------------------
# Security middleware
# ---------------------------------------------------------------------------

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds defensive HTTP headers to every response."""

    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Cache-Control"] = "no-store"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Rejects bodies larger than 64 KB to prevent resource exhaustion."""

    MAX_BODY_SIZE = 64 * 1024  # 64 KB

    async def dispatch(self, request: StarletteRequest, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_BODY_SIZE:
            return StarletteResponse("Request too large", status_code=413)
        return await call_next(request)


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Structured audit log for every mutating request."""

    AUDIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(self, request: StarletteRequest, call_next):
        start = time.time()
        response = await call_next(request)
        if request.method in self.AUDIT_METHODS:
            duration_ms = int((time.time() - start) * 1000)
            client_ip = request.client.host if request.client else "unknown"
            logger.info(
                "AUDIT method=%s path=%s status=%d ip=%s duration_ms=%d",
                request.method,
                request.url.path,
                response.status_code,
                client_ip,
                duration_ms,
            )
        return response


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando Cumbre OSB v%s (%s)", settings.api_version, settings.environment)
    init_db()
    yield
    logger.info("Cerrando Cumbre OSB")


is_dev = settings.environment == "dev"

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
    docs_url="/docs" if is_dev else None,       # Hidden in production
    redoc_url="/redoc" if is_dev else None,
    openapi_url="/openapi.json" if is_dev else None,
)

# Rate limiter state + exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware stack (innermost registered last)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(AuditLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3010", "http://localhost:8000"],  # explicit allowlist
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(health.router, tags=["health"])
app.include_router(services.router, prefix="/v1", tags=["services"])
app.include_router(ui.router, tags=["ui"])


# ---------------------------------------------------------------------------
# Internal-only endpoints
# ---------------------------------------------------------------------------

@app.get("/metrics", include_in_schema=False)
async def metrics(request: Request):
    """Prometheus scrape endpoint — restricted to localhost and Docker subnets."""
    client_ip = request.client.host if request.client else ""
    allowed = client_ip in ("127.0.0.1", "::1") or client_ip.startswith(("172.", "10."))
    if not allowed:
        raise HTTPException(status_code=403, detail="Forbidden")
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# ---------------------------------------------------------------------------
# Static files (CSS del dashboard)
# ---------------------------------------------------------------------------
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except Exception:
    pass
