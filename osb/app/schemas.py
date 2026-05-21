"""Esquemas Pydantic para validación de entrada/salida en la API."""
import ipaddress
import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import ServiceStatus

NameStr = Annotated[str, Field(min_length=3, max_length=64, pattern=r"^[a-z][a-z0-9-]*$")]

# ---------------------------------------------------------------------------
# SSRF protection — hostnames and IP ranges that must never be accepted
# ---------------------------------------------------------------------------
BLOCKED_HOSTNAMES = {
    "localhost", "redis", "postgres", "sovereign", "envoy",
    "auth-sidecar", "prometheus", "grafana",
    "metadata.google.internal",
}
BLOCKED_IP_PREFIXES = ["10.", "172.", "192.168.", "127.", "169.254.", "::1", "0."]


def _validate_upstream_host(v: str) -> str:
    """Shared SSRF validator for upstream_host fields."""
    if v is None:
        return v
    host = v.lower().strip()
    # Block internal hostnames
    if host in BLOCKED_HOSTNAMES:
        raise ValueError(f"upstream_host '{v}' no está permitido (acceso interno bloqueado)")
    # Block internal IPs by prefix
    for prefix in BLOCKED_IP_PREFIXES:
        if host.startswith(prefix):
            raise ValueError(f"upstream_host '{v}' no está permitido (IP privada bloqueada)")
    # Try to parse as IP and block private/loopback/link-local/reserved ranges
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise ValueError(f"upstream_host '{v}' no está permitido (IP reservada)")
    except ValueError as e:
        if "no está permitido" in str(e):
            raise
        # Not an IP address — that is fine, continue with hostname checks
    # Basic hostname / FQDN format check
    if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]{0,253}[a-zA-Z0-9])?$', host):
        raise ValueError(f"upstream_host '{v}' tiene formato inválido")
    return v


class ServiceCreate(BaseModel):
    """Payload para crear un servicio nuevo en la plataforma."""
    name: NameStr
    team: str = Field(..., min_length=2, max_length=64)
    description: str | None = Field(None, max_length=500)
    upstream_host: str = Field(..., min_length=1, max_length=255)
    upstream_port: int = Field(8080, ge=1, le=65535)
    public_path: str = Field("/", min_length=1, max_length=255)
    requires_auth: bool = True
    rate_limit_rpm: int = Field(600, ge=1, le=1_000_000)
    labels: dict = Field(default_factory=dict)

    @field_validator("upstream_host")
    @classmethod
    def no_ssrf(cls, v: str) -> str:
        return _validate_upstream_host(v)

    @field_validator("public_path")
    @classmethod
    def no_path_traversal(cls, v: str) -> str:
        if ".." in v or "//" in v:
            raise ValueError("public_path inválido")
        if not v.startswith("/"):
            raise ValueError("public_path debe empezar con /")
        return v

    @field_validator("labels")
    @classmethod
    def validate_labels(cls, v: dict) -> dict:
        if len(v) > 10:
            raise ValueError("labels no puede tener más de 10 claves")
        for key, value in v.items():
            if len(str(key)) > 64:
                raise ValueError(f"La clave de labels '{key}' supera los 64 caracteres")
            if len(str(value)) > 64:
                raise ValueError(f"El valor de labels para '{key}' supera los 64 caracteres")
        return v


class ServiceUpdate(BaseModel):
    """Payload para actualizar parcialmente un servicio."""
    description: str | None = Field(None, max_length=500)
    upstream_host: str | None = None
    upstream_port: int | None = None
    public_path: str | None = None
    requires_auth: bool | None = None
    rate_limit_rpm: int | None = None
    labels: dict | None = None

    @field_validator("upstream_host")
    @classmethod
    def no_ssrf(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validate_upstream_host(v)


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
