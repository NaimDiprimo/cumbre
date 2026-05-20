"""Endpoints CRUD para servicios provisionados por la plataforma."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Service, ServiceStatus
from ..queue import enqueue, queue_depth
from ..schemas import ServiceCreate, ServiceOut, ServiceUpdate

router = APIRouter()


@router.post(
    "/services",
    response_model=ServiceOut,
    status_code=202,
    summary="Aprovisionar un nuevo servicio",
    description="Crea el registro del servicio y encola el aprovisionamiento. "
                "Responde 202 porque el trabajo es asíncrono.",
)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)) -> ServiceOut:
    existing = db.execute(select(Service).where(Service.name == payload.name)).scalar_one_or_none()
    if existing:
        raise HTTPException(409, f"Ya existe un servicio con nombre '{payload.name}'")

    service = Service(
        name=payload.name,
        team=payload.team,
        description=payload.description,
        upstream_host=payload.upstream_host,
        upstream_port=payload.upstream_port,
        public_path=payload.public_path,
        requires_auth=payload.requires_auth,
        rate_limit_rpm=payload.rate_limit_rpm,
        labels=payload.labels,
        status=ServiceStatus.PENDING,
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    enqueue("provision", service.id)
    return ServiceOut.model_validate(service)


@router.get("/services", response_model=list[ServiceOut])
def list_services(
    team: str | None = Query(None, description="Filtrar por equipo"),
    status: ServiceStatus | None = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db),
):
    q = select(Service).order_by(Service.created_at.desc())
    if team:
        q = q.where(Service.team == team)
    if status:
        q = q.where(Service.status == status)
    return [ServiceOut.model_validate(s) for s in db.execute(q).scalars().all()]


@router.get("/services/{service_id}", response_model=ServiceOut)
def get_service(service_id: str, db: Session = Depends(get_db)):
    s = db.get(Service, service_id)
    if not s:
        raise HTTPException(404, "Servicio no encontrado")
    return ServiceOut.model_validate(s)


@router.patch("/services/{service_id}", response_model=ServiceOut)
def update_service(service_id: str, payload: ServiceUpdate, db: Session = Depends(get_db)):
    s = db.get(Service, service_id)
    if not s:
        raise HTTPException(404, "Servicio no encontrado")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(s, k, v)
    s.status = ServiceStatus.PROVISIONING
    db.commit()
    db.refresh(s)
    enqueue("update", s.id)
    return ServiceOut.model_validate(s)


@router.delete("/services/{service_id}", status_code=202)
def delete_service(service_id: str, db: Session = Depends(get_db)):
    s = db.get(Service, service_id)
    if not s:
        raise HTTPException(404, "Servicio no encontrado")
    s.status = ServiceStatus.DELETING
    db.commit()
    enqueue("delete", s.id)
    return {"detail": "Borrado en curso", "id": service_id}


@router.get("/queue", summary="Profundidad de la cola interna")
def queue_status():
    return {"depth": queue_depth()}
