# Cumbre

**Internal Developer Platform open-source para empresas LATAM.**

> Una plataforma que tus developers usan para aprovisionar su propia infraestructura, sin tickets, sin esperas, sin un equipo de DevOps de 15 personas en el medio.

Inspirado en la arquitectura que [Vasilios Syrakis](https://www.youtube.com/watch?v=55pTFVoclvE) explicó después de 8 años en Atlassian. Reimplementado desde cero, en español, listo para correr en empresas de 50 a 500 ingenieros.

[![Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-beta-yellow.svg)](#)
[![LATAM](https://img.shields.io/badge/built%20for-LATAM-orange.svg)](#)

---

## ¿Qué problema resuelve?

En la mayoría de empresas chilenas y argentinas con más de 30 ingenieros, el día a día se ve así:

- Un equipo necesita exponer un nuevo microservicio → abre un ticket → espera 2 a 5 días.
- Quieren cambiar un rate limit → otro ticket → otra espera.
- Necesitan agregar autenticación → "lo hago yo en mi servicio" → cada equipo reinventa la rueda.
- El equipo de infraestructura termina siendo cuello de botella y se quema.

**Cumbre cambia eso.** Un developer entra a la plataforma, define lo que necesita, le da a "aprovisionar", y en segundos Envoy enruta tráfico real con auth, rate limiting y observabilidad aplicados.

---

## Arquitectura

```
       Internet
          │
          ▼
   ┌─────────────┐         ┌──────────────┐
   │    Envoy    │◄────────│  Sovereign   │  (XDS)
   │  data plane │  config │ control plane│
   └──────┬──────┘         └──────▲───────┘
          │                       │ lee
          │ ext_authz             │
          ▼                       │
   ┌─────────────┐         ┌──────┴───────┐
   │ Auth sidecar│         │   Postgres   │
   └─────────────┘         └──────▲───────┘
                                  │ escribe
          ┌───────────────────────┘
          │
   ┌──────┴──────┐         ┌──────────────┐
   │     OSB     │ encola  │    Redis     │
   │  FastAPI    │────────►│   (cola)     │
   │  + Web UI   │         └──────┬───────┘
   └──────▲──────┘                │
          │                       │ procesa
          │ HTTP / UI      ┌──────┴───────┐
       Developer           │ OSB worker   │
                           └──────────────┘
```

**Componentes:**

- **OSB (Open Service Broker)** — FastAPI + Web UI. Donde los developers piden lo que necesitan.
- **OSB worker** — proceso async que ejecuta los aprovisionamientos.
- **Sovereign** — el control plane XDS que [Vasilios open-sourceó](https://github.com/cetanu/sovereign), usado aquí con templates propios.
- **Envoy** — el proxy moderno (data plane) que enruta tráfico real.
- **Auth sidecar** — valida JWTs vía `ext_authz` antes de que el request llegue al backend.
- **Backends de demo** — `echo-service` y `orders-service` para mostrar el sistema funcionando.
- **Postgres + Redis** — estado y cola de tareas.
- **Prometheus + Grafana** — métricas y dashboards incluidos.

---

## Cómo correrlo (5 minutos)

Necesitas Docker y Docker Compose instalados.

```bash
git clone <repo>
cd cumbre
cp .env.example .env
make up
```

Esperá ~60 segundos a que todo arranque. Después:

```bash
make dashboard   # te muestra las URLs
make demo        # carga 2 servicios de ejemplo
sleep 5
make test-edge   # prueba el endpoint público que no requiere auth
```

**URLs principales:**

| Servicio | URL | Notas |
|---|---|---|
| OSB UI | http://localhost:8000 | Dashboard principal |
| API docs | http://localhost:8000/docs | OpenAPI / Swagger |
| Envoy (tráfico) | http://localhost:10000 | Endpoint público |
| Envoy admin | http://localhost:9901 | Stats, config, clusters |
| Sovereign | http://localhost:8081 | Control plane |
| Prometheus | http://localhost:9090 | Métricas |
| Grafana | http://localhost:3000 | Dashboards (anon viewer activo) |

---

## Mejoras respecto al sistema original

Cumbre toma los patrones del video y agrega cosas que Vasilios mencionó como pendientes o que el ecosistema de hoy hace más simples:

1. **Web UI propia** — el OSB de Atlassian no tenía UI (los devs subían YAMLs). Cumbre incluye dashboard listo.
2. **Self-contained con docker-compose** — corre en una laptop. La de Atlassian requería 13 regiones AWS.
3. **Observabilidad built-in** — Prometheus + Grafana con dashboard inicial cargado.
4. **Auth sidecar en Python primero** — más rápido de iterar; reescritura a Rust en roadmap.
5. **Documentación en español** — pensada para equipos LATAM.
6. **API OpenAPI auto-generada** — Swagger UI listo sin trabajo extra.

---

## Documentación

- [Arquitectura detallada](docs/ARQUITECTURA.md)
- [Cómo funciona el flujo end-to-end](docs/COMO_FUNCIONA.md)
- [Runbook para operación](docs/RUNBOOK.md)
- [Decisiones de diseño](docs/DECISIONES.md)

## Para empresas

Si estás evaluando Cumbre para tu equipo, mirá:

- [Pitch comercial](ventas/PITCH.md)
- [Modelo de precios](ventas/PRECIOS.md)
- [Casos de uso](ventas/PITCH.md#casos-de-uso)

Para una demo en vivo, contactá a **diprimodp@gmail.com**.

---

## Roadmap

- [x] OSB con Web UI
- [x] Sovereign con templates propios
- [x] Envoy + ext_authz
- [x] Sidecar de auth en Python
- [x] docker-compose end-to-end
- [x] Dashboards Grafana
- [ ] Sidecar de auth reescrito en Rust
- [ ] Helm chart para Kubernetes
- [ ] Multi-tenant con namespaces
- [ ] Integración SSO (Okta, Auth0)
- [ ] Edge cache nativo
- [ ] Plugin para Backstage

---

## Licencia

Apache 2.0. Usá esto libremente. Si te sirve, [contactanos](mailto:diprimodp@gmail.com) — ofrecemos implementación, soporte y customización.

## Créditos

Cumbre se basa en los patrones y herramientas que Vasilios Syrakis hizo públicos. Sovereign sigue siendo de Atlassian; lo usamos respetando su licencia Apache 2.0.
