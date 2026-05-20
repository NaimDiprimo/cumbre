# Cómo funciona Cumbre — flujo end-to-end

Este documento te lleva de la mano por lo que pasa cuando un developer aprovisiona un servicio en Cumbre. Usalo cuando le hagas una demo a un cliente.

## El escenario

El equipo de Payments necesita exponer una API nueva (`orders-api`) que corre internamente en `orders-service:8080`. Quiere:

- Que sea pública en `/orders`
- Que requiera autenticación
- Rate limit de 300 req/min

Antes de Cumbre: ticket → 3 días → "tenés el LB listo".
Con Cumbre: 30 segundos.

## Paso 1: el developer abre la UI

Va a `http://localhost:8000` y hace clic en "Nuevo servicio". Llena el formulario:

```
name: orders-api
team: payments
upstream_host: orders-service
upstream_port: 8080
public_path: /orders
requires_auth: ✓
rate_limit_rpm: 300
```

Hace clic en "Aprovisionar".

## Paso 2: el OSB recibe el request

`POST /v1/services` con el JSON:

```json
{
  "name": "orders-api",
  "team": "payments",
  "upstream_host": "orders-service",
  "upstream_port": 8080,
  "public_path": "/orders",
  "requires_auth": true,
  "rate_limit_rpm": 300
}
```

El OSB:

1. Valida con Pydantic (nombre kebab-case, puerto válido, etc.).
2. Inserta una fila en Postgres con `status='pending'`.
3. Encola un mensaje en Redis: `{"action":"provision","service_id":"<uuid>"}`.
4. Devuelve `202 Accepted` con el servicio creado y su id.

## Paso 3: el worker procesa el job

El proceso `osb-worker` está en un loop `BRPOP` sobre la cola. Al llegar el mensaje:

1. Carga el servicio de Postgres.
2. Cambia el `status` a `provisioning`.
3. Hace el "trabajo" (en producción: crear LB en AWS, registrar DNS, etc. Acá: simula con un `sleep`).
4. Marca `status='ready'`.
5. Commit.

En Postgres ahora hay una fila con `status='ready'`.

## Paso 4: Sovereign refresca el contexto

Cada `refresh_context_seconds` (10s por default) Sovereign:

1. Llama al plugin `osb_context.OsbContext.load()`.
2. El plugin hace `SELECT * FROM services WHERE status='ready'`.
3. Devuelve un dict `{"services": [...]}`.

## Paso 5: Sovereign rinde los templates

Envoy llama a Sovereign cada `refresh_delay` (5s) pidiendo:

- `/v3/discovery:listeners`
- `/v3/discovery:clusters`

Sovereign:

1. Toma el contexto (con `orders-api` adentro).
2. Renderiza `templates/listeners.yaml.j2` y `clusters.yaml.j2` con Jinja2.
3. Devuelve YAML/JSON XDS válido.

El cluster `orders_api_cluster` ahora existe, y el listener tiene la ruta `/orders` apuntando a él.

## Paso 6: Envoy aplica la nueva config

Envoy compara la respuesta con su estado actual. Detecta:

- Nuevo cluster `orders_api_cluster` → lo crea.
- Nueva ruta `/orders` → la agrega al listener `cumbre_ingress_http`.

Sin reiniciar. Sin downtime.

## Paso 7: el tráfico real

Alguien hace:

```bash
curl http://localhost:10000/orders
```

Lo que pasa internamente:

1. Envoy recibe el request en `:10000`.
2. Match de la ruta `/orders` → cluster `orders_api_cluster`.
3. Filtro `ext_authz` → llama a `http://auth-sidecar:9000/orders`.
4. El sidecar no encuentra `Authorization` header → devuelve 401.
5. Envoy responde 401 al cliente. **El request nunca llegó al backend.**

Ahora con token válido:

```bash
TOKEN=$(make token)
curl -H "Authorization: Bearer $TOKEN" http://localhost:10000/orders
```

1. Envoy recibe.
2. ext_authz → sidecar valida JWT → 200 OK + `{"sub":"naim"}`.
3. Envoy reenvía al cluster.
4. `orders-service` responde con el listado de órdenes.
5. Envoy logea y devuelve al cliente.

## Paso 8: la observabilidad

Mientras esto pasa, Envoy va emitiendo métricas en `:9901/stats/prometheus`:

- `envoy_cluster_upstream_rq_total{envoy_cluster_name="orders_api_cluster"}`
- `envoy_cluster_upstream_rq_time_bucket` (histograma de latencia)

Prometheus las raspa cada 15s. Grafana las grafica. El equipo de Payments puede mirar su tablero en `http://localhost:3000` y ver tráfico en tiempo real.

## Mapa mental para la demo

> "Un developer pide algo en la UI. El OSB lo guarda y encola. Un worker lo ejecuta y marca como listo. Sovereign lee la BD, genera config para Envoy. Envoy aplica la config en caliente. El tráfico real fluye y se observa. Todo el ciclo: 5 segundos."
