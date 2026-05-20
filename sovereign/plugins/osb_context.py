"""Context plugin de Sovereign: trae datos desde el OSB (Postgres) y los expone a los templates.

Cómo funciona Sovereign con plugins:
  1. Al arrancar y cada `refresh_context_seconds` segundos, Sovereign instancia este plugin.
  2. Llama al método `load()` que debe devolver un dict.
  3. Esas claves quedan disponibles dentro de los templates Jinja2.

Documentación: https://developer.atlassian.com/platform/sovereign/advanced/context/
"""
from __future__ import annotations

import logging
import os
from typing import Any

from sqlalchemy import create_engine, text

log = logging.getLogger("sovereign.plugin.osb")

DEFAULT_DB_URL = os.getenv(
    "SOVEREIGN_DB_URL",
    "postgresql+psycopg2://cumbre:cumbre@postgres:5432/cumbre",
)


class OsbContext:
    """Lee los servicios listos desde la BD y los pone al alcance de los templates."""

    def __init__(self, *args, **kwargs):
        self.engine = create_engine(DEFAULT_DB_URL, pool_pre_ping=True)

    def load(self) -> dict[str, Any]:
        services: list[dict] = []
        try:
            with self.engine.connect() as conn:
                rows = conn.execute(
                    text(
                        """
                        SELECT id, name, team, upstream_host, upstream_port,
                               public_path, requires_auth, rate_limit_rpm, status
                        FROM services
                        WHERE status = 'ready'
                        ORDER BY name
                        """
                    )
                ).mappings().all()
                for r in rows:
                    services.append(
                        {
                            "id": r["id"],
                            "name": r["name"],
                            "team": r["team"],
                            "upstream_host": r["upstream_host"],
                            "upstream_port": int(r["upstream_port"]),
                            "public_path": r["public_path"],
                            "requires_auth": bool(r["requires_auth"]),
                            "rate_limit_rpm": int(r["rate_limit_rpm"]),
                            "cluster_name": _slug(r["name"]) + "_cluster",
                            "route_name": _slug(r["name"]) + "_route",
                        }
                    )
        except Exception as e:
            log.error("OsbContext.load() falló: %s", e)
        log.info("OsbContext: %d servicios en estado READY", len(services))
        return {"services": services}


def _slug(name: str) -> str:
    return name.replace("-", "_").replace(".", "_")
