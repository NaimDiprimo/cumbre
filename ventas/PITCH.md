# Pitch comercial — Cumbre

> **Para uso interno.** Esta es la columna vertebral de toda conversación con prospectos.

## El one-liner

> **"Cumbre es la plataforma que tus developers usan para aprovisionar su propia infraestructura — sin tickets, sin esperas, sin que tu equipo de DevOps se queme."**

## La frase que cierra reuniones

> **"En 30 minutos te mostramos un developer creando un endpoint productivo con auth y rate limiting. Y en 90 días lo tenemos corriendo en tu producción."**

---

## El problema (el dolor que vendés)

Tu prospecto tiene este día a día (cualquier empresa chilena/argentina con +30 ingenieros):

1. **Cuello de botella:** un equipo de 3 personas de "infra" o "DevOps" atendiendo tickets de 50+ developers.
2. **Tiempos absurdos:** "tengo un endpoint nuevo" → 3 a 7 días hábiles.
3. **Cada uno hace lo suyo:** autenticación implementada 8 veces en 8 servicios distintos.
4. **Nadie sabe qué hay:** ningún catálogo central de "qué servicios existen, quién los mantiene, dónde están las dependencias".
5. **El equipo de infra está quemado:** rotación alta, salarios al alza, no se contrata más rápido.
6. **El CTO está bajo presión:** "¿por qué no entregamos features más rápido?"

## La promesa (cómo Cumbre lo soluciona)

Cumbre es una plataforma interna donde:

- Cualquier developer entra y, en un formulario simple, define: "quiero exponer mi servicio en `/api/v1/orders`, con auth, rate limit X, observado".
- En **segundos** Envoy enruta tráfico real con todo aplicado.
- El equipo de infra deja de hacer ticket y empieza a hacer producto.
- Tenés un **catálogo único** de qué hay en tu sistema, quién lo dueño, cómo se conecta.

## Por qué creemos esto

- Gartner: el 80% de orgs de ingeniería tendrán equipo de plataforma en 2026.
- El video de Vasilios Syrakis (ex-Atlassian) — 1.1M de vistas en 8 días — confirmó que esta arquitectura es replicable y que **el mercado quiere entenderla**.
- En Chile específicamente: la demanda de Cloud/DevOps creció 250% en dos años; la oferta de seniors solo 40%. Las empresas no pueden contratar su salida del problema.

## Qué traemos nosotros que no tiene el cliente

- **Producto open-source listo** — no es una promesa, le mostramos el código corriendo en 10 minutos.
- **Conocimiento del patrón** — sabemos por qué Envoy y no NGINX, por qué Sovereign y no escribir tu propio control plane, por qué sidecar y no in-proc.
- **Foco LATAM** — documentación en español, soporte en husos horarios LATAM, conocimiento del mercado local (compliance financiera chilena, NeoBancos argentinos, etc.).
- **Implementación garantizada** — 90 días, contrato firmado, hitos claros, sin sorpresas.

---

## Casos de uso

### Caso 1: FinTech chilena de pagos con 40 ingenieros

**Pain:** equipo de SRE de 4 personas saturado. Tiempo medio de exposición de un nuevo endpoint: 6 días. CMO pide "lanzar feature en 2 semanas", ingeniería responde "imposible".

**Cumbre:** implementación en 75 días. A los 30 días post-launch, el tiempo de exposición de endpoint pasa de 6 días a 30 minutos. SRE se reasigna 60% a trabajo de producto.

**ROI:** ahorra ~3 contrataciones de SRE adicionales que ya tenían en pipeline (≈ US$180k/año). Acelera lanzamiento de features. Mejora moral del equipo.

### Caso 2: Banco tradicional chileno migrando a cloud

**Pain:** 200+ ingenieros distribuidos en 15 squads. Cada squad tiene su propio approach a auth, logging, rate limiting. Auditorías cuestan fortunas por la inconsistencia.

**Cumbre:** capa central que estandariza. Después de 6 meses, todos los servicios nuevos pasan por Cumbre. Auditorías unificadas.

**ROI:** ahorro de costo de auditoría + tiempo de equipos. Compliance simplificado para SBIF / CMF.

### Caso 3: Marketplace argentino con escala alta

**Pain:** ya tienen Envoy en producción pero todo lo configuran a mano. Cada cambio requiere PR + merge + deploy + reload. Tiempo: ~40 min.

**Cumbre:** integramos su Envoy con nuestro control plane. Configuraciones declarativas en API. Cambio en producción: <30 segundos.

**ROI:** velocidad de iteración 80x. Permite arquitectura más experimental (A/B routing, canary releases).

---

## Quién es el cliente ideal

**Stages que sí:**
- Series A-C en FinTech, e-commerce, logística, salud digital.
- Empresas tradicionales en migración cloud (banca, retail, telco).
- 30-300 ingenieros (sweet spot: 50-150).

**Stages que no (al menos por ahora):**
- Startup pre-Seed sin equipo de ingeniería formado.
- Empresas con menos de 20 ingenieros (no necesitan IDP todavía).
- Hyperscale (Mercado Libre, Globant) — tienen sus propios equipos.

## Decisores con quien conversar

| Rol | Cómo te recibe |
|---|---|
| **CTO / VP Engineering** | Decisor final. Habla con él/ella primero. Argumento principal: velocidad y costo de oportunidad. |
| **VP Platform / VP Infra** | Aliado natural. Está sufriendo el dolor. Le encanta poder decir "yo lideré esta migración". |
| **Head of SRE** | Cuidado: puede sentir amenaza ("vienes a quitarme trabajo"). Reposicionar: "te liberamos para hacer trabajo más interesante". |
| **CISO / Compliance** | Vendele auditoría centralizada y trazabilidad. |
| **CEO/COO** | Solo en casos donde el área tech reporta directo. Vende ROI puro: ahorro de contrataciones, time-to-market. |

---

## Las objeciones más comunes y cómo responder

### "Eso ya lo podemos hacer con Istio / Kubernetes nativo"

> *"Podés. Vamos a ver cuántos meses y cuánta gente te toma. Cumbre te da el 80% del valor en 3 meses; vos podés invertir 18 meses en hacer el 100% por tu cuenta. La pregunta es cuál es tu costo de oportunidad."*

### "Es muy caro"

> *"Comparálo con el costo de contratar 2 senior DevOps en Chile durante un año (≈ US$150k cada uno) y dejarlos construir esto desde cero. Y eso si los encontrás, porque la demanda creció 250% y la oferta no."*

### "Y si te vas, ¿quién mantiene esto?"

> *"Open-source Apache 2.0. El código es tuyo. Te entrenamos a tu equipo en el proceso. Y si querés, contratás un retainer de soporte. Pero el lock-in técnico no existe."*

### "No tenemos cultura de plataforma todavía"

> *"Justamente por eso. Empezar a construir esa cultura con un producto funcionando es más barato y rápido que empezar de cero. Cumbre te da el framework para enseñar a la organización qué es una plataforma."*

### "Nuestros equipos no van a querer usarlo"

> *"En la implementación incluimos onboarding y change management. La adopción se mide y se reporta. Y lo más importante: si el producto es bueno (lo es, te lo mostramos), los equipos lo van a pedir."*

---

## La conversación ideal (script)

**Tú:** Hola \[nombre\]. Te contacto porque vi que tu equipo de ingeniería viene creciendo rápido. Sé que en empresas en tu etapa el cuello de botella suele estar en infraestructura — ¿cuánto tarda un equipo en exponer un nuevo endpoint hoy?

**Prospect:** \[Cualquier número >24h\]

**Tú:** Eso era lo que esperaba. Ese es exactamente el problema que resolvemos. Yo tengo una plataforma open-source que reduce ese tiempo a minutos, y la implementamos completa en 90 días. ¿Tenés 25 minutos en los próximos días para que te haga una demo en vivo? No es slides, es código corriendo.

**Prospect:** OK, sí.

**Tú:** Genial. \[Agenda meet\]. Antes te mando un link al README y un pequeño video grabado para que sepas qué vas a ver.
