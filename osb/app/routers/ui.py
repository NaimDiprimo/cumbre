"""Web UI sencilla (la mejora sobre lo que mostró Vasilios)."""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Service, ServiceStatus
from ..queue import enqueue, queue_depth
from .auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard principal del OSB."""
    services = db.execute(select(Service).order_by(Service.created_at.desc())).scalars().all()
    by_status = {}
    for s in services:
        by_status[s.status.value] = by_status.get(s.status.value, 0) + 1
    # Starlette 1.x exige el request como primer argumento. La forma vieja
    # (nombre de plantilla primero) se interpreta como request y revienta con
    # "unhashable type: 'dict'".
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "services": services,
            "by_status": by_status,
            "queue_depth": queue_depth(),
            "env": settings.environment,
            "version": settings.api_version,
            "current_user": get_current_user(request),
        },
    )


@router.get("/ui/new", response_class=HTMLResponse, include_in_schema=False)
def new_service_form(request: Request):
    return templates.TemplateResponse(request, "new_service.html", {})


@router.post("/ui/new", include_in_schema=False)
def create_service_form(
    name: str = Form(...),
    team: str = Form(...),
    upstream_host: str = Form(...),
    upstream_port: int = Form(8080),
    public_path: str = Form("/"),
    requires_auth: bool = Form(False),
    rate_limit_rpm: int = Form(600),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    s = Service(
        name=name,
        team=team,
        description=description or None,
        upstream_host=upstream_host,
        upstream_port=upstream_port,
        public_path=public_path,
        requires_auth=requires_auth,
        rate_limit_rpm=rate_limit_rpm,
        status=ServiceStatus.PENDING,
        labels={},
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    enqueue("provision", s.id)
    return RedirectResponse(url="/", status_code=303)
