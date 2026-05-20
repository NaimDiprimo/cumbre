# Plantilla de Propuesta Comercial — Cumbre

> **Cómo usar:** copiá este documento, reemplazá los `[VARIABLES]`, ajustá precios según el tier y el discovery. La propuesta debería caber en 3-4 páginas A4. **Nunca** mandes un PDF de 20 páginas.

---

# Propuesta de Implementación
## Cumbre Internal Developer Platform

**Para:** [NOMBRE EMPRESA]
**A la atención de:** [NOMBRE DECISOR] — [CARGO]
**Preparada por:** Naim Di Primo — Cumbre Platform
**Fecha:** [FECHA]
**Validez de la oferta:** 30 días corridos

---

## 1. Contexto

\[Acá resumís en 1-2 párrafos lo que te contaron en discovery. Mostrás que escuchaste. Ejemplos:\]

> "\[EMPRESA\] está en un momento de crecimiento acelerado. El equipo de ingeniería pasó de 30 a 80 personas en los últimos 18 meses, y se proyecta llegar a 120 hacia fin de año. La velocidad para entregar features es una prioridad estratégica; sin embargo, el equipo de plataforma actual está saturado atendiendo solicitudes de los squads de producto, lo que se traduce en demoras de 4-7 días para exponer un nuevo endpoint y en cada equipo implementando autenticación y rate limiting de manera independiente."

## 2. Diagnóstico

Identificamos los siguientes puntos de dolor en su situación actual:

- **\[Dolor 1\]:** [Ej: "tiempo de aprovisionamiento de endpoint: 4-7 días"]
- **\[Dolor 2\]:** [Ej: "auth implementado de 6 maneras distintas en los servicios"]
- **\[Dolor 3\]:** [Ej: "falta visibilidad centralizada de qué servicios existen y quién los mantiene"]
- **\[Dolor 4\]:** [Ej: "compliance team revisa cada servicio por separado, alto costo de auditoría"]

## 3. Propuesta

Implementaremos **Cumbre Internal Developer Platform** en su infraestructura, configurando:

- **Open Service Broker (OSB)** — portal interno donde sus developers aprovisionan servicios.
- **Control Plane (Sovereign)** — generación dinámica de configuración Envoy.
- **Edge Proxy (Envoy)** — un único punto de entrada para todo el tráfico interno.
- **Auth Sidecar** — autenticación y autorización centralizadas.
- **Observabilidad** — Prometheus + Grafana con dashboards listos.

### 3.1 Alcance

**Incluido en esta propuesta:**

- Setup en \[CLOUD/ON-PREM ELEGIDO\] con \[AMBIENTES\] (típicamente: dev + staging + prod).
- Configuración de \[X\] servicios productivos pilotos (definidos junto a su equipo).
- Integración con su SSO actual (\[OKTA / AZURE AD / OTRO\]).
- Documentación interna específica de la implementación.
- \[N\] horas de entrenamiento al equipo de plataforma.
- 30 días de soporte post-go-live.

**No incluido (cotizable aparte):**

- Migración de la totalidad de servicios existentes (estimamos \[X\] servicios — la migración guiada cotiza aparte).
- Customizaciones al producto Cumbre core.
- Hosting / costos de infraestructura cloud.

### 3.2 Cronograma

| Fase | Duración | Hitos |
|---|---|---|
| **Kickoff y descubrimiento técnico** | Semana 1 | Acceso a sandbox, sesiones con squads piloto, diseño detallado |
| **Setup de infraestructura base** | Semanas 2-3 | OSB + Sovereign + Envoy en ambiente dev |
| **Integración SSO y políticas** | Semanas 4-5 | Auth conectada, primeras políticas de rate limiting |
| **Migración pilotos** | Semanas 6-8 | 3 servicios productivos en Cumbre |
| **Hardening y observabilidad** | Semanas 9-10 | Dashboards custom, runbooks, alerting |
| **Entrenamiento + go-live producción** | Semanas 11-12 | Equipo capacitado, sistema en prod |
| **Soporte post-launch** | Semanas 13-16 | Acompañamiento operacional incluido |

**Tiempo total: \[X semanas / Y meses\].**

### 3.3 Equipo asignado

- **Líder técnico:** Naim Di Primo
- **Ingeniero(s) de implementación:** \[1-2 según tier\]
- **Punto de contacto comercial:** Naim Di Primo

## 4. Inversión

| Concepto | Monto USD |
|---|---|
| Implementación completa (Tier \[X\]) | **US$\[XX,XXX\]** |
| Retainer mensual de soporte (opcional, plan \[X\]) | US$\[X,XXX\] / mes |
| Total año 1 (implementación + 12 meses de retainer plan \[X\]) | US$\[XX,XXX\] |

### Forma de pago

- **40%** al firmar este acuerdo (kickoff).
- **30%** al cumplir hito de Semana 8 (servicios piloto en staging).
- **30%** al go-live de producción.

Retainer: mensual o anual con 15% de descuento.

## 5. ROI esperado

Sobre la base de su equipo actual de \[N\] ingenieros y suponiendo:

- Tiempo evitado en gestión de tickets de infraestructura: \~\[X\] horas/mes a US$\[Y\]/hora.
- Capacidad recuperada del equipo de plataforma: equivalente a \[Z\] contrataciones evitadas (≈ US$\[A\]/año).
- Time-to-market reducido en \[B\]%, lo que se traduce en ingresos adicionales estimados en US$\[C\]/año.

**Recupero estimado de la inversión: \[N\] meses.**

\[Acá ajustá los números a lo que te dijo el cliente. Sé conservador. Mejor entregar más de lo que prometés.\]

## 6. Por qué Cumbre

- **Producto funcionando.** No es una promesa. Le mostramos demo en vivo.
- **Open-source Apache 2.0.** El código es suyo. No hay lock-in.
- **Foco LATAM.** Documentación en español, soporte en su huso horario.
- **Inspirado en arquitectura validada.** Atlassian operó este patrón por 8 años en producción a escala global.
- **Sin sorpresas.** Precio cerrado, hitos claros, entregables auditables.

## 7. Próximos pasos

1. Confirmación de su parte para avanzar (responder este email o coordinar llamada).
2. Firma de acuerdo en \[X\] días.
3. Pago inicial.
4. Kickoff el \[FECHA TENTATIVA\].

---

**Naim Di Primo**
Fundador — Cumbre Platform
diprimodp@gmail.com
\[teléfono\]
\[LinkedIn\]
