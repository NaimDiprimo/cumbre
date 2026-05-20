# Modelo de precios — Cumbre

> **Para uso interno.** Nunca mostrar esta tabla cruda al cliente sin contexto.

## Filosofía de precios

Cumbre es **open-source gratis**. Cobramos por:

1. **Implementación** (servicio one-shot)
2. **Soporte continuo** (retainer mensual)
3. **Customizaciones / módulos adicionales** (ad-hoc)
4. **Entrenamiento** (workshops)

Nunca cobramos por "licencia". Esto desbloquea conversaciones con compliance, CFO y compras.

---

## Tier 1 — Implementación

| Tier | Tamaño cliente | Alcance | Tiempo | Precio (USD) |
|---|---|---|---|---|
| **Starter** | 20-50 ingenieros | OSB + Sovereign + Envoy en 1 ambiente | 45 días | **US$15,000 – US$25,000** |
| **Growth** | 50-150 ingenieros | + multi-ambiente (dev/stg/prod), SSO, monitoring custom | 75 días | **US$28,000 – US$45,000** |
| **Enterprise** | 150-500 ingenieros | + HA, multi-región, compliance, training extendido | 120 días | **US$55,000 – US$95,000** |

**Qué incluye cada implementación (sin importar tier):**

- Kickoff técnico con equipo del cliente (5 días).
- Setup en la infra del cliente (AWS, GCP o on-prem).
- Migración de 1 a 3 servicios productivos de muestra.
- Documentación interna específica del cliente.
- Capacitación del equipo (4 a 16 horas según tier).
- 30 días de soporte post-go-live incluidos.

**Qué NO incluye:**

- Costos de infraestructura cloud (los paga el cliente).
- Migración de TODOS los servicios (eso es ad-hoc).
- Cambios al producto Cumbre core (eso es customización).

---

## Tier 2 — Retainer mensual de soporte

Después del go-live, el cliente puede contratar soporte continuo:

| Plan | Horas/mes | SLA respuesta | Precio (USD/mes) |
|---|---|---|---|
| **Bronze** | hasta 10 hs | 24 hs hábiles | **US$1,200** |
| **Silver** | hasta 25 hs | 8 hs hábiles | **US$2,800** |
| **Gold** | hasta 50 hs | 2 hs hábiles | **US$5,500** |
| **Platinum** | sin tope razonable | < 30 min en SEV1 | **US$10,000** |

**Qué incluye el retainer:**

- Atención a incidentes operacionales.
- Sesiones de revisión arquitectónica trimestrales.
- Pre-acceso a nuevas features.
- Actualizaciones de seguridad gestionadas.

---

## Tier 3 — Módulos / customizaciones

Precios estimados. Cotización fija contra alcance acordado.

| Módulo | Precio (USD) | Tiempo |
|---|---|---|
| Integración con SSO existente (Okta, Auth0, Azure AD) | US$3,500 – US$7,000 | 1-2 semanas |
| Auth sidecar reescrito en Rust con SLA estricto | US$12,000 – US$18,000 | 4 semanas |
| Backstage plugin (catálogo + Cumbre integrado) | US$8,000 – US$15,000 | 3 semanas |
| Multi-tenant con namespaces aislados | US$10,000 – US$20,000 | 4-6 semanas |
| Helm chart + operator para Kubernetes | US$8,000 – US$14,000 | 3 semanas |
| Edge caching nativo | US$15,000 – US$25,000 | 6-8 semanas |
| Compliance reporting (SOC2, PCI-DSS) | US$6,000 – US$12,000 | 4 semanas |

---

## Tier 4 — Entrenamiento

| Formato | Audiencia | Precio (USD) |
|---|---|---|
| Workshop privado 1 día (8 hs) | hasta 15 personas | US$3,500 |
| Workshop privado 2 días (16 hs) | hasta 15 personas | US$6,000 |
| Bootcamp 5 días (full stack platform engineering) | hasta 10 personas | US$15,000 |
| Office hours semanales (4 sesiones/mes) | sin tope | US$2,500/mes |

---

## Cómo presentarlo

**No** mostrás la tabla. Hacés discovery primero:

1. ¿Cuántos ingenieros tiene la empresa?
2. ¿Cuál es la urgencia? (CTO presionado, auditoría próxima, lanzamiento de feature)
3. ¿En qué cloud están? ¿Tienen Kubernetes?
4. ¿Tienen capacidad técnica para mantener Cumbre después? (Si no → vendé Gold/Platinum)

**Después** armás propuesta a medida con la plantilla en [PROPUESTA_PLANTILLA.md](PROPUESTA_PLANTILLA.md).

---

## Descuentos y políticas

- **Pago anual de retainer:** 15% off.
- **Compromiso de caso de éxito público:** 10% off implementación.
- **Primer cliente en cada vertical:** hasta 25% off (compensás con visibilidad + caso).
- **Pago 100% por adelantado:** 5% off.
- **Sin descuento por "amigo de un amigo".** El descuento es por valor, no por relación.

## Forma de cobro

- Implementación: 40% al firmar + 30% al medio + 30% al go-live.
- Retainer: mensual o anual por adelantado.
- Customizaciones: 50% al kickoff + 50% a la entrega.

Moneda: USD preferido, CLP/ARS aceptado al tipo de cambio del día con reajuste UF anual para contratos largos en Chile.

## Margen real estimado

- Costo directo de 1 implementación Growth (75 días, 1.5 personas) ≈ US$18,000.
- Precio cobrado: US$35,000.
- **Margen bruto ≈ 49%.**

A escala (3+ proyectos en paralelo con un equipo de 4 personas), el margen sube a ~60%.

---

## Referencias de mercado (validación)

- Una implementación de **Backstage** por consultora externa en LATAM: US$40k - US$120k.
- Una implementación de **Istio** managed por consultora: US$50k - US$150k.
- Un mes de **AWS Premium Support** para una empresa mediana: US$15k+.
- Un senior platform engineer en Chile cuesta US$70k-US$120k/año.

Cumbre está **por debajo** del precio de la competencia directa y **muy por debajo** del costo de contratar talento interno. Ese es el pitch.
