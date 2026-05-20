"""Endpoints de salud y readiness."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..queue import get_redis
from ..schemas import HealthOut

router = APIRouter()


@router.get("/health", response_model=HealthOut)
def health():
    return HealthOut(
        status="ok",
        version=settings.api_version,
        environment=settings.environment,
    )


@router.get("/ready")
def ready(db: Session = Depends(get_db)):
    """Verifica conectividad a Postgres y Redis."""
    deps = {}
    try:
        db.execute(text("SELECT 1"))
        deps["postgres"] = "ok"
    except Exception as e:
        deps["postgres"] = f"error: {e}"
    try:
        get_redis().ping()
        deps["redis"] = "ok"
    except Exception as e:
        deps["redis"] = f"error: {e}"
    ok = all(v == "ok" for v in deps.values())
    return {"ready": ok, "deps": deps}
