"""Modelos de base de datos."""
import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class ServiceStatus(str, enum.Enum):
    """Estados del ciclo de vida de un servicio aprovisionado."""
    PENDING = "pending"          # Encolado, esperando worker
    PROVISIONING = "provisioning"  # Worker procesando
    READY = "ready"              # Listo para tráfico
    FAILED = "failed"            # Falló el aprovisionamiento
    DELETING = "deleting"        # Borrado en curso
    DELETED = "deleted"          # Borrado completo


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Service(Base):
    """Un \"servicio\" registrado en la plataforma.

    En la arquitectura de Vasilios esto representaría: un backend interno
    que necesita exposición vía Envoy con un set de rutas, autenticación,
    y rate limiting aplicados en el edge.
    """
    __tablename__ = "services"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    team: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Dónde vive el backend real (host:port en la red interna)
    upstream_host: Mapped[str] = mapped_column(String(255), nullable=False)
    upstream_port: Mapped[int] = mapped_column(nullable=False, default=8080)

    # Cómo se expone hacia fuera
    public_path: Mapped[str] = mapped_column(String(255), nullable=False, default="/")
    requires_auth: Mapped[bool] = mapped_column(default=True, nullable=False)
    rate_limit_rpm: Mapped[int] = mapped_column(default=600, nullable=False)

    # Estado del aprovisionamiento
    status: Mapped[ServiceStatus] = mapped_column(
        Enum(ServiceStatus), default=ServiceStatus.PENDING, nullable=False, index=True
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata libre
    labels: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_envoy_config(self) -> dict:
        """Datos que Sovereign usa para generar la config de Envoy."""
        return {
            "id": self.id,
            "name": self.name,
            "team": self.team,
            "upstream": {"host": self.upstream_host, "port": self.upstream_port},
            "route": {"prefix": self.public_path},
            "requires_auth": self.requires_auth,
            "rate_limit_rpm": self.rate_limit_rpm,
            "labels": self.labels or {},
        }
