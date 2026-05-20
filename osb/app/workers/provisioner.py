"""Worker que consume la cola y \"aprovisiona\" los servicios.

En un sistema real esto:
  - llamaría a APIs de AWS/GCP para crear LBs, DNS, certs
  - empujaría el cambio al control plane (Sovereign) — en nuestro caso Sovereign
    LEE directamente la BD vía un context plugin, así que el worker solo
    actualiza el estado en Postgres y Sovereign lo recoge en su próximo poll.
"""
import logging
import signal
import time

from sqlalchemy import select

from ..config import settings
from ..database import SessionLocal, init_db
from ..models import Service, ServiceStatus
from ..queue import dequeue

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
log = logging.getLogger("cumbre.osb.worker")


class Worker:
    def __init__(self):
        self.running = True
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT, self._stop)

    def _stop(self, *_):
        log.info("Recibida señal de cierre. Terminando bucle…")
        self.running = False

    def handle(self, msg: dict) -> None:
        action = msg.get("action")
        service_id = msg.get("service_id")
        log.info("Procesando action=%s id=%s", action, service_id)
        with SessionLocal() as db:
            s: Service | None = db.get(Service, service_id)
            if not s:
                log.warning("Servicio %s no existe en BD. Descartando job.", service_id)
                return
            try:
                if action == "provision":
                    self._provision(s)
                elif action == "update":
                    self._update(s)
                elif action == "delete":
                    self._delete(s)
                else:
                    log.warning("Acción desconocida: %s", action)
                db.commit()
            except Exception as e:
                log.exception("Fallo procesando %s/%s", action, service_id)
                s.status = ServiceStatus.FAILED
                s.last_error = str(e)[:1000]
                db.commit()

    def _provision(self, s: Service) -> None:
        s.status = ServiceStatus.PROVISIONING
        # Simulamos trabajo (en real: crear LB, DNS, AMIs, etc.)
        time.sleep(1.5)
        # Validaciones mínimas
        if not s.upstream_host or s.upstream_port < 1:
            raise ValueError("upstream inválido")
        s.status = ServiceStatus.READY
        s.last_error = None
        log.info("Servicio %s LISTO (auth=%s, rpm=%s)", s.name, s.requires_auth, s.rate_limit_rpm)

    def _update(self, s: Service) -> None:
        time.sleep(0.5)
        s.status = ServiceStatus.READY
        log.info("Servicio %s actualizado", s.name)

    def _delete(self, s: Service) -> None:
        time.sleep(0.5)
        s.status = ServiceStatus.DELETED
        log.info("Servicio %s eliminado", s.name)

    def loop(self):
        log.info("Worker iniciado. Esperando jobs en la cola…")
        while self.running:
            msg = dequeue(timeout=2)
            if msg is None:
                continue
            self.handle(msg)
        log.info("Worker detenido.")


def main():
    init_db()
    Worker().loop()


if __name__ == "__main__":
    main()
