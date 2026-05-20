# Script de demo en vivo — Cumbre

> **Duración objetivo: 25 minutos.** Si te pasas de 30 perdés a la audiencia.

## Antes de la demo

**Lista de verificación 24 hs antes:**

- [ ] `docker-compose up -d` funciona limpio
- [ ] `make demo` carga datos sin error
- [ ] `make test-edge` devuelve JSON
- [ ] Grafana muestra al menos una métrica
- [ ] Tu cámara y micrófono funcionan
- [ ] Tenés Zoom/Meet abierto en pantalla secundaria
- [ ] Pestañas listas en orden: README → UI OSB → Envoy admin → Grafana → API docs → diagrama de arquitectura

**Tu setup en pantalla:**
- Lado izquierdo: la terminal con docker-compose corriendo (logs visibles).
- Lado derecho: el navegador con las pestañas.
- Pantalla compartida: ventana del navegador a pantalla completa.

---

## Minuto 0-3 — Apertura y dolor

> "Hola \[nombre\]. Antes de mostrarte código, te recuerdo el problema que vinimos a resolver: tu equipo de \[X\] ingenieros está perdiendo tiempo en infraestructura repetitiva. Hoy un endpoint nuevo tarda \[días\]. Auth, rate limiting, observabilidad — cada equipo lo reinventa. ¿Te suena familiar?"

(Pausa. Esperá respuesta.)

> "OK. Lo que te voy a mostrar son tres cosas: primero, qué experiencia tendría un developer tuyo usando Cumbre. Segundo, qué pasa atrás. Tercero, cómo se opera. ¿Vamos?"

## Minuto 3-8 — La experiencia del developer

**Compartí pantalla. Abrí http://localhost:8000**

> "Esto es lo que ve cualquier developer en su empresa. Un dashboard simple. Acá veo todos los servicios que la plataforma está sirviendo, su estado, quién es dueño."

(Pausa para que mire.)

> "Voy a aprovisionar uno nuevo. Imaginá que sos del equipo de Payments y necesitás exponer una API de órdenes."

**Click en "Nuevo servicio". Llenar:**

```
name: demo-orders
team: payments
upstream_host: orders-service
upstream_port: 8080
public_path: /orders-demo
requires_auth: ✓
rate_limit_rpm: 300
```

**Click "Aprovisionar".**

> "Lo que acabás de ver: 30 segundos. En tu empresa hoy, esto es un ticket de 3-7 días."

(Volver al dashboard. El servicio aparece en "pending", después "ready" en pocos segundos.)

> "Ya está. Cumbre configuró Envoy, registró la ruta, aplicó auth, aplicó rate limit. Lo voy a probar."

**Abrir terminal y mostrar:**

```bash
curl -sS http://localhost:10000/orders-demo
# 401 — sin auth

TOKEN=$(make token | tail -1)
curl -sS -H "Authorization: Bearer $TOKEN" http://localhost:10000/orders-demo | jq .
# 200 + JSON con la lista de órdenes
```

> "Sin auth → 401. Con token → pasa. Y no toqué un archivo de configuración de Envoy. Todo declarativo desde la API."

## Minuto 8-15 — Cómo funciona por dentro (técnico)

> "Si tu equipo técnico se está preguntando 'sí, ¿pero cómo?'. Te lo muestro."

**Abrir el diagrama de arquitectura (de docs/ARQUITECTURA.md).**

> "Tres planos: el plano de datos, que es Envoy. El plano de control, que es Sovereign — código que mira los datos y genera config para Envoy. Y el OSB, que es donde los developers interactúan."

**Mostrar la API docs (http://localhost:8000/docs).**

> "Todo está expuesto como API REST con OpenAPI. Tu equipo puede automatizar lo que quiera: integrarlo a CI/CD, a un GitOps, a un bot de Slack. No estás obligado a usar la UI."

**Mostrar Envoy admin (http://localhost:9901/clusters).**

> "Acá está Envoy admitiendo que ahora tiene un cluster nuevo, `demo_orders_cluster`. Esto se cargó dinámicamente, sin reiniciar nada."

**Mostrar Sovereign (http://localhost:8081).**

> "Acá Sovereign me muestra qué configuración generó. Esto es 100% trazable — auditable. Tu compliance team va a estar contento."

## Minuto 15-22 — Observabilidad

**Abrir Grafana (http://localhost:3000).**

> "Y todo esto viene observado. Acá tengo: cuántos requests por segundo, cuántos 5xx, latencia p99 por cluster. Sin que tu equipo configure nada."

**Lanzar tráfico en otra pestaña:**

```bash
while true; do curl -sS -H "Authorization: Bearer $TOKEN" http://localhost:10000/orders-demo > /dev/null; sleep 0.1; done
```

> "Mirá cómo suben las métricas en tiempo real."

(Esperar 30s a que se vea el gráfico.)

**Bonus si el cliente parece interesado en seguridad:**

> "Y mirá esto: el auth sidecar es un servicio separado. Si mañana querés tu auth corporativa con Okta o Azure AD, cambiás un solo componente. Si querés que esté en Rust para más performance, lo cambiás sin tocar nada más. Modular en serio."

## Minuto 22-25 — Cierre

> "Resumen de lo que viste:
> - Developer pide → 30 segundos → tráfico fluyendo con auth, rate limit y métricas.
> - Cero configuración manual de Envoy.
> - Todo open-source. El código es tuyo.
> - Documentación en español. Soporte LATAM."

> "Lo que te ofrezco: en 90 días lo tenemos en tu producción. Casos de éxito documentados, equipo entrenado, retainer si querés que sigamos cerca."

> "Mi propuesta: te mando hoy mismo una propuesta personalizada para tu caso. Discutimos números y plan. ¿Te parece?"

(Esperá respuesta. Cerrá con próximo paso concreto.)

---

## Si algo falla durante la demo

**Plan A: seguís como si nada y volvés al punto en 30s.**

```bash
# Restart rápido del componente
docker-compose restart osb
```

**Plan B: lo usás a tu favor.**

> "Mirá, justo se cayó el OSB y notá que el tráfico que ya estaba fluyendo SIGUIÓ funcionando. Eso es porque el plano de datos (Envoy) es independiente del plano de control. Es exactamente el diseño que hace que Cumbre sea production-grade."

**Plan C: pestaña de respaldo.**

Tené un video grabado de la demo en una pestaña aparte. Si todo se rompe, lo mostrás y seguís.

---

## Después de la demo

- Mandá un email en las próximas 2 horas con: link al README, link a un video grabado, y una propuesta inicial estimada.
- Anotá objeciones que aparecieron y respondelas en el email.
- Agendá un follow-up para 3-5 días después.

---

## Variantes de demo

- **Demo corta (10 min):** salteás minuto 8-15 (interno). Vas directo: dashboard → crear → probar → grafana → cierre.
- **Demo técnica profunda (60 min):** sumás minuto a minuto cómo trabaja Sovereign, mostrás el código del context plugin, mostrás Jinja templates.
- **Demo para C-level (15 min):** menos pantalla negra, más métricas de negocio (tiempo a producción, costo evitado, ROI estimado).
