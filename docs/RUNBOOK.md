# Runbook de Cumbre

Guía operacional para mantener Cumbre en producción. Pensada para guardia (on-call).

## Síntomas comunes y diagnóstico

### 1. La UI del OSB no carga

```bash
docker-compose logs osb --tail=200
```

Comprobar:
- ¿`postgres` está `healthy`? `docker-compose ps`
- ¿Puede el OSB conectarse? `curl http://localhost:8000/ready`

**Fix típico:** reiniciar Postgres o validar credenciales en `.env`.

### 2. Los servicios quedan en `pending` para siempre

El worker no está consumiendo la cola.

```bash
docker-compose logs osb-worker --tail=200
docker-compose exec redis redis-cli LLEN cumbre:osb:provision-queue
```

**Fix:** `docker-compose restart osb-worker`. Si la cola crece sin parar, escalar workers (cambiar `docker-compose.yml` para tener `osb-worker-2`, etc.).

### 3. Envoy devuelve 503 en una ruta nueva

Probablemente Sovereign no actualizó la config aún.

```bash
# Ver qué clusters tiene Envoy
curl -s http://localhost:9901/clusters | head -50

# Forzar reload del context en Sovereign
curl http://localhost:8081/admin/clean

# Ver el último config que Sovereign le sirvió
curl http://localhost:8081/admin/source_versions
```

**Esperar:** ~15s (ciclo de refresh). Si pasa más, revisar logs de `sovereign`.

### 4. Auth devuelve 401 con un token que parece válido

```bash
# Probar el sidecar directamente
docker-compose exec auth-sidecar curl -i http://localhost:9000/ -H "Authorization: Bearer $TOKEN"

# Verificar que el secret coincida
docker-compose exec auth-sidecar env | grep JWT
```

**Fixes:**
- Secret distinto al que se usó para firmar → ajustar `CUMBRE_JWT_SECRET`.
- Token expirado → generar uno nuevo con `make token`.

### 5. Latencia alta en `p99`

Mirar Grafana → "Latencia upstream p99".

Si el problema es:
- Solo en un cluster → el backend está lento. Llamar al equipo dueño.
- En todos los clusters → posible problema en Envoy o auth sidecar.

```bash
# Stats de Envoy
curl -s http://localhost:9901/stats | grep upstream_rq_time
```

## Tareas comunes

### Agregar un servicio nuevo (vía API)

```bash
curl -X POST http://localhost:8000/v1/services \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "billing-api",
    "team": "finance",
    "upstream_host": "billing-service",
    "upstream_port": 8080,
    "public_path": "/billing",
    "requires_auth": true,
    "rate_limit_rpm": 600
  }'
```

### Cambiar rate limit de un servicio

```bash
curl -X PATCH http://localhost:8000/v1/services/<id> \
  -H 'Content-Type: application/json' \
  -d '{"rate_limit_rpm": 1200}'
```

### Eliminar un servicio

```bash
curl -X DELETE http://localhost:8000/v1/services/<id>
```

### Backup de la BD

```bash
docker-compose exec postgres pg_dump -U cumbre cumbre > backup_$(date +%Y%m%d).sql
```

### Restore

```bash
docker-compose exec -T postgres psql -U cumbre cumbre < backup_20260520.sql
```

## SLOs sugeridos (para conversar con clientes)

| SLI | Objetivo |
|---|---|
| Disponibilidad del OSB | 99.9% (mensual) |
| Disponibilidad de tráfico (Envoy) | 99.95% |
| Latencia p99 ext_authz | < 50ms |
| Tiempo entre "crear servicio" y "tráfico fluyendo" | < 30s (p95) |

## Escalada

| Severidad | Definición | Acción |
|---|---|---|
| SEV1 | Tráfico de producción caído | Página al on-call inmediatamente |
| SEV2 | Aprovisionamientos parados | Página en horario laboral |
| SEV3 | Métricas o UI con problemas | Ticket regular |
