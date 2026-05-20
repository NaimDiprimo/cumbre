# Arquitectura de Cumbre

## Visión

Cumbre es una **Internal Developer Platform (IDP)**. Su objetivo es que cualquier developer en la empresa pueda exponer un servicio detrás de un proxy edge — con autenticación, rate limiting, observabilidad y rutas — sin abrir un ticket.

El sistema sigue tres principios:

1. **Plano de control / plano de datos separados.** El OSB y Sovereign son el plano de control; Envoy es el plano de datos. Si el control plane cae, el tráfico sigue fluyendo con la última configuración conocida.
2. **Asincronía con polling.** Las operaciones que tardan (aprovisionar un servicio) se encolan y el cliente consulta el estado.
3. **Configuración generada dinámicamente.** Envoy no tiene archivos de config estáticos. Sovereign los genera al vuelo a partir del estado de la BD.

## Diagrama de componentes

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        CUMBRE — Internal Dev Platform                    │
└──────────────────────────────────────────────────────────────────────────┘

                      [Developer / equipo interno]
                                  │
                                  │ usa Web UI o API
                                  ▼
            ┌───────────────────────────────────────────┐
            │                  OSB                      │
            │   FastAPI + Jinja2 templates + Pydantic   │
            │  - Crea/actualiza/elimina services        │
            │  - Encola jobs en Redis                   │
            └────┬───────────────────────────────────┬──┘
                 │                                   │
                 │ escribe estado                    │ encola job
                 ▼                                   ▼
       ┌──────────────────┐                  ┌─────────────────┐
       │    Postgres      │                  │     Redis       │
       │  services table  │                  │ provision-queue │
       └────────▲─────────┘                  └────────┬────────┘
                │                                     │
                │ lee context             consume     │
                │                                     ▼
                │                            ┌─────────────────┐
                │                            │  OSB Worker     │
                │                            │ (provisioner)   │
                │   actualiza status         └────────┬────────┘
                ├────────────────────────────────────┘
                │
       ┌────────┴──────────┐
       │     Sovereign     │           ────► sirve XDS
       │  control plane    │
       │ (templates + plug)│
       └────────▲──────────┘
                │
                │ XDS sobre HTTP/gRPC
                │
       ┌────────┴──────────┐         ┌────────────────────────┐
       │      Envoy        │ ext_au  │   Auth Sidecar         │
       │   data plane      ├────────►│   (JWT validator)      │
       │   :10000 público  │         └────────────────────────┘
       └────────┬──────────┘
                │
                │ proxy
                ▼
       ┌───────────────────┐
       │     Backends      │   echo-service / orders-service / ...
       │   (microservicios)│
       └───────────────────┘
```

## Decisiones técnicas clave

### Por qué FastAPI para el OSB

- Tipado fuerte (Pydantic v2) → menos bugs.
- OpenAPI auto-generado → docs y SDKs sin esfuerzo extra.
- Performance comparable a Node.js / Go en cargas I/O-bound.
- Ecosistema Python: SQLAlchemy, Alembic, Celery/arq están maduros.

### Por qué Sovereign

Es el código que el propio Vasilios open-sourceó. Está en producción en Atlassian. Tiene los pliegues correctos: plugins para contexto, templates Jinja2, modelo de "polling" en vez de "push" (más simple operacionalmente). No reinventamos la rueda.

### Por qué Envoy

- Estándar de facto en cloud-native (Istio, App Mesh, Consul Connect, etc.).
- API XDS bien definida → cualquier control plane que la implemente sirve.
- Filtros `ext_authz` permiten desacoplar auth en sidecar.
- Métricas Prometheus nativas en `:9901/stats/prometheus`.

### Por qué Redis y no SQS

Para correr en una laptop. En producción se puede cambiar a SQS (AWS), Cloud Tasks (GCP), Service Bus (Azure) o RabbitMQ — el módulo `app/queue.py` es la única abstracción que hay que ajustar.

### Por qué Python para el auth sidecar (no Rust como Vasilios)

- Velocidad de desarrollo: iteramos rápido.
- El sidecar no es el cuello de botella en la mayoría de casos.
- Rust queda en el roadmap; el cambio es transparente para Envoy (mismo contrato `ext_authz`).

## Flujo end-to-end

Ver [COMO_FUNCIONA.md](COMO_FUNCIONA.md).

## Trade-offs explícitos

| Decisión | Pro | Contra | Mitigación |
|---|---|---|---|
| Postgres como source of truth | Transacciones, JOIN, mantenible | Single point of failure | RDS Multi-AZ en prod |
| Sovereign por polling | Simple, debuggeable | Latencia ~10s entre cambio y aplicación | Reducir `refresh_context_seconds` |
| Auth en Python | Iteración rápida | Más latencia que Rust | Reescribir a Rust si p99 > 5ms |
| Un solo listener Envoy | Simple | No SNI multi-dominio | Templates parametrizables por host |
| Redis local (no SQS) | Funciona en laptop | No persiste fuera del volume | Cambiar adapter en prod |

## Escalamiento

| Componente | Escalamiento |
|---|---|
| OSB API | Horizontal (stateless) detrás de un LB |
| OSB Worker | Horizontal (cada uno toma un job de la cola) |
| Sovereign | Horizontal (stateless, cada Envoy se conecta a uno) |
| Envoy | Horizontal con ASG o HPA en K8s |
| Postgres | Vertical primero, replica de lectura después |
| Redis | Cluster Redis para HA |
