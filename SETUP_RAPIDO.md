# Setup Rápido — Correr Cumbre en tu Mac

> Guía paso a paso para alguien que nunca corrió Docker. Si te trabas en algún paso, pausá y avisame.

## Antes de empezar

Asegurate de tener:

- **Docker Desktop** abierto (el icono de la ballenita arriba en la barra del Mac).
- **5 GB libres** en el disco.
- **15 minutos** la primera vez (después arranca en 60 segundos).

---

## Paso 1 — Verificar que Docker está vivo

1. Mirá arriba a la derecha de tu Mac, en la barra de menú. ¿Ves un icono que parece una ballenita (🐳)?
2. Si **sí** y dice "Docker Desktop is running" cuando le hacés clic, todo bien.
3. Si **no**, abrí Spotlight (⌘ Espacio), tipeá "Docker" y abrilo. Esperá 30-60 segundos hasta que la ballenita aparezca.

**Avisame antes de seguir si Docker está corriendo.**

---

## Paso 2 — Abrir la Terminal

1. Apretá **⌘ Espacio**, escribí **Terminal** y apretá Enter.
2. Se abre una ventana negra (o blanca) con texto. Esa es la terminal.

---

## Paso 3 — Ir a la carpeta del proyecto

Copiá y pegá este comando exacto en la terminal, después apretá Enter:

```bash
cd "/Users/naimvalencia/Documents/Claude/Projects/mina de oro/cumbre"
```

Para verificar que estás en el lugar correcto, pegá:

```bash
ls
```

Deberías ver: `README.md`, `docker-compose.yml`, `osb`, `sovereign`, `envoy`, etc.

Si ves eso, vas bien. Si no, avisame.

---

## Paso 4 — Levantar la plataforma

Este es el paso largo (la primera vez tarda 5-10 minutos porque Docker descarga las imágenes base y construye todo).

Pegá:

```bash
docker-compose up -d --build
```

Vas a ver mucho texto pasando. Es normal. Espera hasta que veas algo así al final:

```
[+] Running 11/11
 ✔ Network cumbre_cumbre_net  Created
 ✔ Container cumbre-postgres-1     Healthy
 ✔ Container cumbre-redis-1        Healthy
 ✔ Container cumbre-osb-1          Started
 ✔ Container cumbre-osb-worker-1   Started
 ✔ Container cumbre-sovereign-1    Started
 ✔ Container cumbre-envoy-1        Started
 ✔ Container cumbre-auth-sidecar-1 Started
 ✔ Container cumbre-echo-service-1 Started
 ✔ Container cumbre-orders-service-1 Started
 ✔ Container cumbre-prometheus-1   Started
 ✔ Container cumbre-grafana-1      Started
```

Si llegaste hasta ahí: **¡felicitaciones, tenés tu propia plataforma corriendo!**

---

## Paso 5 — Verificar que todo está vivo

Pegá:

```bash
docker-compose ps
```

Deberías ver todos los servicios con `State: running` o `Up`. Si alguno dice `restarting` o `exited`, avisame y miramos los logs.

---

## Paso 6 — Abrir el dashboard

Abrí tu navegador (Chrome, Safari, lo que uses) y andá a:

**http://localhost:8000**

Deberías ver el dashboard de Cumbre con fondo oscuro, el logo ▲, y un mensaje "Todavía no hay servicios". ¡Eso está bien — todavía no creamos nada!

---

## Paso 7 — Cargar datos de demo

Volvé a la terminal y pegá:

```bash
curl -X POST http://localhost:8000/v1/services \
  -H 'Content-Type: application/json' \
  -d '{"name":"echo-demo","team":"platform","upstream_host":"echo-service","upstream_port":8080,"public_path":"/echo","requires_auth":false,"rate_limit_rpm":1000}'
```

Y después:

```bash
curl -X POST http://localhost:8000/v1/services \
  -H 'Content-Type: application/json' \
  -d '{"name":"orders-api","team":"payments","upstream_host":"orders-service","upstream_port":8080,"public_path":"/orders","requires_auth":true,"rate_limit_rpm":300}'
```

**Esperá 5 segundos.**

Refrescá http://localhost:8000 en el navegador. Deberías ver los dos servicios con estado **`ready`** en verde.

---

## Paso 8 — Probar que el tráfico fluye

Pegá en la terminal:

```bash
curl -s http://localhost:10000/echo/hola-mundo
```

Si ves un JSON con `"service": "echo-service"` y la ruta `/hola-mundo` adentro: **EL TRÁFICO ESTÁ FLUYENDO REAL POR TU PLATAFORMA.** Lo que acabás de probar es exactamente lo que un cliente de Cumbre tendría en su producción.

Ahora probá esto:

```bash
curl -s http://localhost:10000/orders
```

Debería devolverte una respuesta de **401** o **403** (no autorizado). Eso es porque `orders-api` requiere auth y no le mandaste token. **Es el comportamiento correcto.**

Para probar con auth:

```bash
docker-compose exec auth-sidecar python -c "import jwt, time; print(jwt.encode({'sub':'naim','iat':int(time.time()),'exp':int(time.time())+3600}, 'dev-only-secret-change-me', algorithm='HS256'))"
```

Te da un token. Copialo y usá:

```bash
TOKEN="pega-aca-el-token"
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:10000/orders
```

Ahora sí te devuelve datos. **El sidecar de auth funcionó.**

---

## Paso 9 — Mirar las métricas

Abrí en el navegador:

- **Grafana:** http://localhost:3000 — vas a ver dashboards con métricas en vivo. Usuario `admin`, contraseña `cumbre`. Anonymous viewer activado, vas a poder mirar sin loguearte.
- **Prometheus:** http://localhost:9090
- **Envoy admin:** http://localhost:9901

Para generar tráfico y ver métricas moviéndose:

```bash
while true; do curl -s http://localhost:10000/echo/test > /dev/null; sleep 0.1; done
```

Dejá eso corriendo en una ventana de terminal y mirá Grafana — los gráficos se mueven.

Para parar: **Ctrl+C** en la terminal donde está el loop.

---

## Paso 10 — Apagar todo

Cuando termines:

```bash
docker-compose down
```

Eso baja todo. Los datos se guardan en volumes Docker, así que la próxima vez que hagas `docker-compose up -d` arranca con todo lo que ya creaste.

Si querés borrar **todo** (incluyendo los datos):

```bash
docker-compose down -v
```

---

## Atajos rápidos para después

Una vez que sepás que funciona, hay atajos en el `Makefile`:

```bash
make up         # levantar todo
make down       # apagar todo
make demo       # cargar datos de demo automáticamente
make logs       # ver logs en vivo
make dashboard  # ver todas las URLs
make ps         # ver estado
```

---

## Problemas comunes

**"command not found: docker-compose"**
Tu Docker Desktop puede usar el comando `docker compose` (con espacio) en vez de `docker-compose` (con guión). Probá ambos.

**"Cannot connect to the Docker daemon"**
Docker Desktop no está corriendo. Abrilo y esperá la ballenita.

**Algún servicio se reinicia en loop**
Pegame esto en la terminal para que veamos qué pasa:
```bash
docker-compose logs <nombre-del-servicio> --tail=50
```

**El localhost:8000 no carga**
Esperá 30 segundos más. Postgres a veces tarda en estar listo y el OSB necesita Postgres.

---

## Cuando todo funcione

Mandame este mensaje: **"funcionó"**. A partir de ahí avanzamos al siguiente paso: subir a GitHub y grabar el video de demo.
