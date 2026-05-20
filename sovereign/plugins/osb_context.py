"""Context plugin de Sovereign: expone los servicios READY desde Postgres a los templates Jinja2."""
from __future__ import annotations

import logging
import os
from typing import Iterator

from sqlalchemy import create_engine, text

log = logging.getLogger("sovereign.plugin.osb")

_DB_URL = os.getenv(
    "SOVEREIGN_DB_URL",
    "postgresql+psycopg2://cumbre:cumbre@postgres:5432/cumbre",
)
_engine = create_engine(_DB_URL, pool_pre_ping=True)


def _slug(name: str) -> str:
    return name.replace("-", "_").replace(".", "_")


class ServicesList:
    """Iterable que consulta Postgres en cada iteración.

    Sovereign hace deepcopy de los context vars antes de cada render,
    así que cada request XDS ve datos frescos sin re-importar el módulo.
    """

    def __iter__(self) -> Iterator[dict]:
        try:
            with _engine.connect() as conn:
                rows = (
                    conn.execute(
                        text(
                            """
                            SELECT id, name, team, upstream_host, upstream_port,
                                   public_path, requires_auth, rate_limit_rpm
                            FROM services
                            WHERE status = 'READY'
                            ORDER BY name
                            """
                        )
                    )
                    .mappings()
                    .all()
                )
                for r in rows:
                    yield {
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
        except Exception as e:
            log.error("ServicesList query failed: %s", e)
            return


# Sovereign carga este atributo vía: module://plugins.osb_context:services
services = ServicesList()
