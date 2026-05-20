"""Esquemas Pydantic para validación de entrada/salida en la API."""
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import ServiceStatus

NameStr = Annotated[str, Field(min_length=3, max_length=64, pattern=r"^[a-z][a-z0-9-]*$")]


class ServiceCreate(BaseModel):
    """Payload para crear un servicio nuevo en la plataforma."""
    name: NameStr
    team: str = Field(..., min_length=2, max_length=64)
    description: str | None = None
    upstream_host: str = Field(..., min_length=1, max_length=255)
    upstream_port: int = Field(8080, ge=1, le=65535)
    public_path: str = Field("/", min_length=1, max_length=255)
    requires_auth: bool = True
    rate_limit_rpm: int = Field(600, ge=1, le=1_000_000)
    labels: dict = Field(default_factory=dict)

    @field_validator("public_path")
    @classmethod
    def path_must_start_with_slash(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("public_path debe empezar con /")
        return v


class ServiceUpdate(BaseModel):
    """Payload para actualizar parcialmente un servicio."""
    description: str | None = None
    upstream_host: str | None = None
    upstream_port: int | None = None
    public_path: str | None = None
    requires_auth: bool | None = None
    rate_limit_rpm: int | None = None
    labels: dict | None = None


class ServiceOut(BaseModel):
    """Servicio expuesto en la API."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    team: str
    description: str | None
    upstream_host: str
    upstream_port: int
    public_path: str
    requires_auth: bool
    rate_limit_rpm: int
    status: ServiceStatus
    last_error: str | None
    labels: dict
    created_at: datetime
    updated_at: datetime


class HealthOut(BaseModel):
    status: str
    version: str
    environment: str


class ErrorOut(BaseModel):
    detail: str
