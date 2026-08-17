---
paths:
  - "sovereign/**"
  - "envoy/**"
  - "docker-compose.yml"
---

# Reglas para el ruteo y la exposición de servicios

Lo que se genera acá termina siendo la configuración con la que Envoy atiende
tráfico real de internet.

- La config dinámica de Envoy **no se edita a mano**. Sale de las plantillas
  `sovereign/templates/*.j2` alimentadas por `sovereign/plugins/osb_context.py`,
  que lee la base del OSB. Si el ruteo está mal, el problema está ahí.
- **Todo lo que venga de la base es entrada de usuario.** Un developer que crea un
  servicio en el OSB controla el nombre, el host y la ruta pública. Ese texto entra
  a una plantilla Jinja y sale como YAML de configuración: si no se valida, un
  nombre malicioso puede romper el YAML o inyectar rutas. Validá y escapá antes de
  interpolar.
- Puertos que **nunca** van expuestos a internet en un despliegue real:
  - `9901` — admin de Envoy (permite reconfigurar el proxy)
  - `8081` — Sovereign (el control plane entero)
  - `9090` — Prometheus (métricas internas)
  - `5432` / `6379` — Postgres y Redis
  Sólo `10000` (Envoy) es público. Si un cambio en `docker-compose.yml` abre otro
  puerto al host, decilo explícitamente en el resumen.
- Un servicio nuevo con `requires_auth: false` es una decisión de seguridad, no un
  detalle de configuración. Que quede escrito por qué.
- Sovereign está pineado en `0.23.0` y sus dependencias vienen fijadas por el
  paquete upstream, así que no se pueden actualizar sin romper la resolución. Ver
  `docs/SEGURIDAD.md`. No intentes subirle las versiones a mano.
