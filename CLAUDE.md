# Cumbre — instrucciones para Claude Code

Internal Developer Platform open-source para LATAM. Ver `CONTEXT.md` para el briefing
completo de negocio y estado del proyecto.

## Cómo trabajar conmigo

- El dueño del proyecto (Naim) **no programa**. Al terminar una tarea, explicá en
  castellano simple qué cambiaste y cómo verificarlo. Nada de jerga sin traducir.
- Antes de dar algo por hecho, **mostrá la evidencia**: la salida de los tests, el
  comando que corriste y qué devolvió, o el curl con su respuesta. No alcanza con
  decir "listo".
- Si un cambio toca varios archivos o no tenés claro el enfoque, planificá primero.
  Si el diff se describe en una frase, hacelo directo.

## Comandos

```bash
make up          # levantar los 11 servicios (docker-compose)
make down        # apagar
make ps          # estado de los servicios
make logs        # logs en vivo
make test        # tests del OSB (pytest, NO necesita docker)
make security    # linter de seguridad + secretos + dependencias vulnerables
make health      # chequeo rápido de que todo responde
make demo        # cargar servicios de demo (echo-demo, orders-api)
make test-edge   # probar tráfico real contra Envoy
make dashboard   # imprimir todas las URLs
```

Los tests corren con SQLite en memoria y Redis mockeado (`osb/tests/conftest.py`),
así que **no hace falta docker para correrlos**. Corré `make test` antes de cada commit.

## Puertos

| Servicio | URL |
| --- | --- |
| OSB (UI + API) | http://localhost:8000 — docs en `/docs` |
| Envoy (tráfico) | http://localhost:10000 |
| Envoy admin | http://localhost:9901 |
| Sovereign (control plane) | http://localhost:8081 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3002 |

## Convenciones

- **Todo en castellano**: docs, comentarios, mensajes de commit, textos de la UI.
- Commits en formato conventional: `feat:`, `fix:`, `docs:`, `refactor:`, con
  descripción en castellano.
- Licencia Apache 2.0. No agregues dependencias con licencias incompatibles.
- Python: FastAPI + SQLAlchemy en `osb/app/`. Seguí los patrones de los routers
  existentes en `osb/app/routers/` antes de inventar uno nuevo.

## Cosas que NO hay que hacer

- **Nunca commitear `.env`** ni pegar secretos reales en el chat, en un archivo o en
  un commit. `.env.example` es la plantilla; `.env` está en `.gitignore`.
- **No editar a mano la config dinámica de Envoy.** Envoy sólo tiene el bootstrap
  mínimo (`envoy/bootstrap.yaml`); el resto se lo entrega Sovereign vía XDS a partir
  de las plantillas en `sovereign/templates/*.j2` y del plugin `sovereign/plugins/osb_context.py`,
  que lee la base del OSB. Si el ruteo está mal, el problema está ahí, no en Envoy.
- No suprimir un error para que el test pase. Buscá la causa raíz.
- **Nunca un secreto con default que funcione en producción.** Si falta la variable
  de entorno y el entorno no es `dev`, el servicio se tiene que negar a arrancar.
  Ver `osb/app/security.py` y `docs/SEGURIDAD.md`.

## Seguridad

Este producto se vende a FinTechs reguladas. Antes de dar un cambio por terminado,
si tocaste auth, ruteo o algo expuesto, corré `make security` y mostrá la salida.
El estado completo está en `docs/SEGURIDAD.md`.

Hay barreras automáticas configuradas en `.claude/settings.json` que bloquean
commits con secretos y no dejan cerrar el turno con los tests en rojo. No las
desactives para poder avanzar: si una te frena, el problema es el cambio.
