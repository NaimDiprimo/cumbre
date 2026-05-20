# Contexto del proyecto Cumbre

> **Este archivo es el briefing que cualquier asistente (Claude Code, agentes, colaboradores futuros) debe leer al iniciar una sesión.** Te pone al tanto en 2 minutos del qué, por qué, dónde estamos y a dónde vamos.

---

## 1. Qué es Cumbre

Cumbre es una **Internal Developer Platform (IDP) open-source** para empresas de LATAM (foco inicial: FinTech chilena, después FinTech argentina, después banca y retail).

Replica y mejora el patrón arquitectónico que **Vasilios Syrakis** explicó después de 8 años en Atlassian (video viral con 1.1M vistas en mayo 2026, https://www.youtube.com/watch?v=55pTFVoclvE).

Permite a developers internos aprovisionar balanceadores de carga, rutas, auth y rate limiting en segundos, sin abrir tickets.

**Stack:**
- OSB (Open Service Broker): FastAPI + Postgres + Redis + Web UI propia
- Control plane: Sovereign (el código que Vasilios open-sourceó, lo usamos con templates propios)
- Data plane: Envoy Proxy
- Auth sidecar: Python (Rust en roadmap) vía ext_authz
- Observabilidad: Prometheus + Grafana
- Todo orquestado con docker-compose

---

## 2. Quién soy yo (el dueño del proyecto)

**Naim Di Primo** (diprimodp@gmail.com)
- Perfil: vendedor / business, **cero código**.
- Ubicación: LATAM (apuntando a Chile y Argentina).
- Objetivo: vender Cumbre a empresas LATAM en 90-180 días.
- Limitación: no puedo modificar código solo. Necesito que las herramientas (vos como asistente) hagan el trabajo técnico y me expliquen los resultados en lenguaje claro.
- Estoy solo por ahora (sin co-founder técnico todavía). Eventualmente tengo que conseguir uno antes de cerrar el primer cliente.

---

## 3. Modelo de negocio

**Híbrido open-source + servicios.** El código es Apache 2.0 (gratis). Cobramos por:

1. **Implementación** (one-shot): US$15k–US$95k según tamaño del cliente.
2. **Retainer mensual** (soporte continuo): US$1.2k–US$10k/mes.
3. **Módulos / customizaciones** ad-hoc: US$3.5k–US$25k.
4. **Workshops / entrenamiento**: US$3.5k–US$15k.

**Target inicial:** FinTech chilenas con 30-150 ingenieros. Lista priorizada en `ventas/EMAIL_OUTREACH.md`.

**Pricing detallado:** `ventas/PRECIOS.md`.

---

## 4. Estado actual del proyecto

### ✅ Hecho

- Código completo de la plataforma (61 archivos, 372 KB).
- docker-compose orquestando los 11 servicios.
- UI web propia en `/`, dashboard con stats + catálogo + form de creación.
- API REST con OpenAPI auto-generado en `/docs`.
- Sovereign control plane configurado con plugin propio que lee de la BD del OSB.
- Envoy configurado con bootstrap mínimo, recibe config dinámica de Sovereign.
- Auth sidecar con validación JWT vía ext_authz.
- 2 backends de demo (echo-service, orders-service).
- Prometheus + Grafana con dashboard inicial cargado.
- Documentación técnica completa en español (5 docs).
- Materiales de venta listos (pitch, precios, demo script, plantilla de propuesta, 6 plantillas de email).
- Análisis profundo del video de Vasilios + roadmap personal de 12 meses (en `/mina de oro/`, fuera de `cumbre/`).

### 🔴 Roto / pendiente urgente

- **BUG ACTUAL:** los servicios creados quedan atascados en estado `PENDING`. El worker (`osb-worker`) no está procesando jobs.
  - Diagnóstico requerido: `docker-compose ps` y `docker-compose logs osb-worker --tail=100`.
  - Posibles causas: contenedor no corriendo, conexión a Redis/Postgres fallida, o bug en el código del worker.
  - **Sin esto resuelto no se puede mostrar el producto a ningún cliente.**

### ⏳ Próximos pasos (en orden)

1. **AHORA:** arreglar el bug del worker → los servicios deben pasar a `READY` → `curl http://localhost:10000/echo/test` debe devolver JSON.
2. **Día 1-2:** subir el código a un repo público en GitHub (Naim ya tiene cuenta).
3. **Día 3-5:** grabar un video demo de 5 minutos siguiendo `ventas/DEMO_SCRIPT.md`. Subir a YouTube no listado.
4. **Día 6-10:** desplegar la demo en un VPS público (DigitalOcean / Hetzner / AWS Lightsail), con dominio. Idealmente `cumbre.cl` o similar.
5. **Día 7-14:** crear una landing page simple (HTML estático en GitHub Pages o similar).
6. **Semana 3:** primera tanda de cold outreach (10-20 emails a fintechs chilenas usando plantillas en `ventas/EMAIL_OUTREACH.md`).
7. **Semana 4-6:** primeras reuniones de discovery, primera propuesta enviada.
8. **Semana 6-12:** primer contrato firmado idealmente.
9. **En paralelo:** conseguir un co-founder técnico o freelance técnico de confianza (CRÍTICO antes de cerrar primer cliente).

---

## 5. Estructura de archivos

```
cumbre/
├── CONTEXT.md                ← este archivo
├── README.md                 ← presentación del proyecto
├── SETUP_RAPIDO.md           ← guía paso a paso para correr la demo en Mac
├── Makefile                  ← atajos: make up, make demo, make logs
├── docker-compose.yml        ← orquestación de los 11 servicios
├── .env.example              ← template de variables de entorno
├── osb/                      ← Open Service Broker (FastAPI + worker + UI)
├── sovereign/                ← control plane XDS con templates propios
├── envoy/                    ← bootstrap mínimo del proxy
├── auth-sidecar/             ← validación JWT vía ext_authz
├── backends/                 ← echo-service + orders-service
├── observability/            ← prometheus.yml + grafana dashboards
├── docs/                     ← ARQUITECTURA, COMO_FUNCIONA, RUNBOOK, DECISIONES
└── ventas/                   ← PITCH, PRECIOS, DEMO_SCRIPT, PROPUESTA_PLANTILLA, EMAIL_OUTREACH
```

---

## 6. Reglas de trabajo

### Tono y comunicación

- **En español, sin tecnicismos innecesarios.** Naim es zero-code; explicaciones claras.
- **Honestidad brutal.** Si algo no se puede, decirlo. Si una idea es mala, decirlo. Si hay un riesgo, mencionarlo.
- **Sin sycophancy.** No empieces con "great question!" ni "absolutely!". Al grano.

### Estilo de trabajo

- **Mostrar antes de explicar.** Primero correr el comando o crear el archivo, después explicar qué pasó.
- **Iteración corta.** Pasos chicos verificables, no megaplanes de 50 cosas.
- **Verificar después de cada cambio.** No asumir que algo funciona — comprobarlo con tests, curl, o logs.

### Reglas del producto

- **No inventar features que no están.** Si alguien (cliente, prospecto) pregunta si Cumbre tiene X, la respuesta tiene que ser verificable.
- **Open-source es no-negociable.** Apache 2.0. Nada de licencias raras.
- **Documentación en español.** Comentarios técnicos pueden ser mixtos (variables en inglés por convención, comentarios en español).
- **El código existente no se rehace desde cero.** Si hay que refactorizar, se justifica y se hace incremental.

### Seguridad y compromiso

- **Nunca commitear secrets.** `.env` está en `.gitignore`.
- **Antes de subir a GitHub público:** revisar que no haya credenciales, tokens, emails personales en el código.
- **El secret JWT default (`dev-only-secret-change-me`) es obviamente solo para dev.** En prod se regenera.

---

## 7. Inspiración y créditos

- **Vasilios Syrakis** (ex-Atlassian) — patrón arquitectónico y proyecto Sovereign open-source.
  - Video: https://www.youtube.com/watch?v=55pTFVoclvE
  - GitHub: https://github.com/cetanu/sovereign
  - Documentación: https://developer.atlassian.com/platform/sovereign/

- **Envoy Proxy** (Lyft + CNCF) — el data plane.
- **Atlassian** — dueños históricos de Sovereign (Apache 2.0).
- Resto del stack: FastAPI, PostgreSQL, Redis, Prometheus, Grafana.

---

## 8. Cómo arrancar una sesión con este proyecto

Si sos un asistente (Claude Code, agente, colaborador nuevo):

1. Leer este archivo entero (estás acá).
2. Leer el README.md para el panorama del producto.
3. Si vamos a tocar código: leer el archivo relevante (ej: `osb/app/main.py`) antes de editar.
4. Si vamos a vender o hacer propuestas: leer `ventas/PITCH.md` y `ventas/PRECIOS.md`.
5. Preguntar a Naim: "¿En qué quieres avanzar hoy?" — y proponer 2-3 opciones concretas si no lo tiene claro.

Última actualización: 20 de mayo de 2026
