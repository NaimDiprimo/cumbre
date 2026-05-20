"""Punto de entrada de la API HTTP del OSB."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from .config import settings
from .database import init_db
from .routers import health, services, ui

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("cumbre.osb")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando Cumbre OSB v%s (%s)", settings.api_version, settings.environment)
    init_db()
    yield
    logger.info("Cerrando Cumbre OSB")


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Routers
app.include_router(health.router, tags=["health"])
app.include_router(services.router, prefix="/v1", tags=["services"])
app.include_router(ui.router, tags=["ui"])


@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Endpoint Prometheus."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# Servir estáticos (CSS del dashboard)
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except Exception:
    pass
