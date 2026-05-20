# Decisiones de diseño (ADRs)

Cada decisión arquitectónica importante se registra acá. Formato corto a propósito: "decidimos X porque Y, con consecuencia Z".

## ADR-001 — Usar Sovereign en vez de escribir nuestro propio control plane

**Contexto:** Necesitamos un control plane XDS. Las opciones eran: escribirlo desde cero, usar go-control-plane, usar Sovereign, usar Istio Pilot.

**Decisión:** Usar [Sovereign](https://github.com/cetanu/sovereign) (Apache 2.0).

**Por qué:**
- Es el código real que Atlassian usó por 8 años.
- Python (mismo stack que el OSB) → menos contexto para el equipo.
- Modelo de templates Jinja2 es lo bastante flexible para 90% de casos.
- Está open-source y mantenido.

**Consecuencias:**
- Dependencia de un proyecto externo. Mitigado: licencia Apache 2.0, código auditable, podemos forkear.
- No tiene gRPC (solo HTTP-REST). Para nuestros volúmenes no es problema.

## ADR-002 — Auth sidecar en Python, no Rust (todavía)

**Contexto:** Vasilios escribió el suyo en Rust. ¿Replicamos?

**Decisión:** Empezar en Python, dejar Rust en roadmap.

**Por qué:**
- Velocidad de iteración inicial.
- p99 esperado para validación de JWT HS256: < 5ms incluso en Python.
- El equipo (1-2 personas) maneja Python mejor que Rust.

**Consecuencias:**
- Si crecemos en tráfico, hay que reescribir. El contrato `ext_authz` se mantiene → cambio transparente para Envoy.
- Mientras tanto, hot reload en desarrollo es trivial.

## ADR-003 — Redis como cola, no SQS

**Contexto:** El sistema original de Atlassian usa SQS. Nosotros queremos poder correr en laptop.

**Decisión:** Redis con `LPUSH/BRPOP`.

**Por qué:**
- Funciona offline.
- Misma semántica básica (FIFO, una sola consumición por mensaje con BRPOP).
- Una sola dependencia que ya usamos para otras cosas en el futuro.

**Consecuencias:**
- En producción AWS conviene cambiar a SQS para durabilidad. El módulo `app/queue.py` aísla esta decisión — un solo archivo a cambiar.

## ADR-004 — Postgres como source of truth, no DynamoDB

**Contexto:** Atlassian usa DynamoDB. ¿Por qué nosotros no?

**Decisión:** Postgres.

**Por qué:**
- LATAM: los equipos conocen mejor SQL que NoSQL.
- Joins y consistencia ACID gratis.
- Funciona en laptop con `docker-compose`.
- Cloud-providers en LATAM (incluida AWS Santiago) ofrecen RDS managed.

**Consecuencias:**
- Para escala >10M servicios habría que repensar. Para los rangos típicos en LATAM (100-10000) Postgres alcanza con sobra.

## ADR-005 — Web UI propia, no Backstage

**Contexto:** Backstage es el estándar de IDP "portal". ¿Lo integramos?

**Decisión:** UI nativa simple ahora, integración con Backstage como plugin en roadmap.

**Por qué:**
- Backstage requiere Node.js, una infra propia, plugins de configuración → suma overhead.
- Para empezar a vender, una UI simple muestra mejor el producto que un Backstage genérico.
- Los clientes que ya tienen Backstage pueden integrar vía nuestra API.

**Consecuencias:**
- Limitamos la primera versión a casos de uso "expone un servicio". Catálogo de software, plantillas (scaffolder), TechDocs vienen después.

## ADR-006 — Documentación en español

**Contexto:** La mayoría de proyectos open-source serios están en inglés.

**Decisión:** Documentar todo en español. Comentarios de código mixto (variables y funciones en inglés por convención técnica, comentarios en español).

**Por qué:**
- Target: empresas chilenas y argentinas.
- Diferenciador: ninguna competencia local documenta así.
- El target de venta no son senior engineers sino arquitectos / CTOs / VPs que se sienten más cómodos en español.

**Consecuencias:**
- Limita adopción global. Aceptable para esta etapa.

## ADR-007 — Apache 2.0, no propietario

**Contexto:** ¿Cobramos por el código o vendemos servicio?

**Decisión:** Open-source (Apache 2.0). Cobramos por implementación, soporte y customizaciones.

**Por qué:**
- Modelo HashiCorp / MongoDB / Sentry — funciona.
- Open-source genera trust y leads inbound.
- En LATAM, "open-source" es un argumento de venta hacia compliance, auditoría y soberanía técnica.

**Consecuencias:**
- Competidores pueden tomar el código. Aceptable: la ventaja competitiva es la implementación y conocimiento, no el código.
