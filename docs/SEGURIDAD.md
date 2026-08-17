# Seguridad de Cumbre

Cumbre se le vende a FinTechs reguladas. Un cliente así va a auditar esto antes de
firmar. Este documento es el estado real, sin maquillaje.

Para correr la auditoría vos mismo:

```bash
make security
```

---

## 1. Qué protege la plataforma automáticamente

### El servicio no arranca mal configurado

El error más común y más caro en una plataforma de auth es desplegarla sin definir
el secreto de firma, y que arranque igual con un valor por defecto que está
publicado en el repositorio. Cualquiera que lea el código puede entonces firmar
tokens válidos y entrar como quien quiera.

Cumbre ahora **se niega a arrancar** en ese caso. Tanto el OSB como el auth-sidecar
verifican al inicio que `CUMBRE_JWT_SECRET`:

- esté definida,
- no sea uno de los valores de ejemplo que están publicados en este repo,
- tenga al menos 32 caracteres.

Si algo de eso falla y `OSB_ENVIRONMENT` no es `dev` ni `test`, el proceso muere con
un mensaje explícito. En desarrollo avisa por log y sigue, para no romper el trabajo
local.

La lógica está en `osb/app/security.py` y sus tests en `osb/tests/test_jwt_secret.py`.

Generá un secreto propio así:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Barreras automáticas en el desarrollo

Configuradas en `.claude/settings.json`, se aplican a cualquier sesión de Claude Code
sobre este repo:

| Barrera | Qué hace |
| --- | --- |
| Reglas `deny` | Claude no puede leer ni escribir `.env`, `*.pem`, `*.key`, `~/.ssh`, `~/.aws` |
| Hook `scan_secrets.py` | Bloquea el `git commit` si en el diff hay algo que parece una credencial real |
| Hook `lint_python.py` | Pasa el linter de seguridad sobre cada archivo Python editado |
| Hook `test_gate.py` | No deja cerrar el turno si se tocó Python y los tests están en rojo |

Las reglas `deny` y los hooks son **cumplimiento**, no sugerencias: una instrucción
en un archivo de texto es un pedido que se puede ignorar, un hook no.

### Linter de seguridad

`ruff` con las reglas de bandit (`S`), configurado en `ruff.toml`. Detecta secretos
hardcodeados, `subprocess` con `shell=True`, SQL por concatenación, verificación de
certificados desactivada y similares. Hoy el repo pasa limpio.

---

## 2. Dependencias

Estado al 11 de agosto de 2026, medido con `pip-audit`.

### OSB y auth-sidecar: sin vulnerabilidades conocidas

Se actualizaron desde versiones que acumulaban 31 y 28 vulnerabilidades conocidas
respectivamente:

| Paquete | Antes | Ahora | Por qué importa |
| --- | --- | --- | --- |
| `pyjwt` | 2.9.0 | 2.13.0 | Valida **todos** los tokens de la plataforma |
| `cryptography` | 43.0.1 | 50.0.0 | Primitivas criptográficas del sidecar |
| `jinja2` | 3.1.4 | 3.1.6 | Renderiza las plantillas del dashboard |
| `python-multipart` | 0.0.12 | 0.0.32 | Parsea los formularios |
| `fastapi` | 0.115.0 | 0.141.1 | Trae `starlette` parcheado |

Los 76 tests pasan con las versiones nuevas, y el sidecar firma y valida tokens
correctamente.

### Sovereign: riesgo aceptado, con mitigación

`sovereign==0.23.0` fija sus propias dependencias y **no acepta** versiones
parcheadas: intentar subir `cryptography` o `gunicorn` da `ResolutionImpossible`.
Quedan 23 vulnerabilidades conocidas en `cryptography 41.0.7`, `fastapi 0.95.2`,
`gunicorn 20.1.0` y `starlette 0.27.0`.

**Mitigación:** Sovereign es el control plane y **no debe estar expuesto a
internet** en ningún despliegue. Escucha en el `8081` y sólo Envoy le habla, dentro
de la red de docker. Un atacante externo no tiene ruta hacia él.

**Qué hacer:** revisar si hay una versión más nueva de Sovereign antes del primer
despliegue en un cliente. Si un cliente FinTech audita esto, la respuesta honesta es
la de arriba: dependencia upstream pineada, no expuesta, con plan de actualización.

---

## 3. Superficie expuesta

En un despliegue real, **sólo el puerto 10000 (Envoy) mira a internet.**

| Puerto | Servicio | Exposición |
| --- | --- | --- |
| 10000 | Envoy | Público |
| 8000 | OSB (UI + API) | Interno / VPN |
| 9901 | Admin de Envoy | Interno. Permite reconfigurar el proxy |
| 8081 | Sovereign | Interno. Es el control plane entero |
| 9090 | Prometheus | Interno |
| 3002 | Grafana | Interno |
| 5432 / 6379 | Postgres / Redis | Interno |

El `docker-compose.yml` de desarrollo publica todos estos puertos en localhost, que
está bien para trabajar en tu máquina y **no** está bien en un servidor.

---

## 4. Lo que todavía falta

Ordenado por prioridad para una venta a FinTech:

1. **Un `docker-compose.prod.yml`** que sólo publique el 10000 y deje el resto en la
   red interna. Hoy la separación entre "desarrollo" y "producción" existe en la
   documentación, no en la configuración.
2. **Rotación de secretos documentada**: qué hacer si un secreto se filtra, en qué
   orden reiniciar los servicios, cómo invalidar los tokens ya emitidos.
3. **Revisar Sovereign** por una versión más nueva, o evaluar aislarlo todavía más.
4. **TLS**: hoy todo el tráfico interno va en claro. Para un banco eso es un
   hallazgo de auditoría.
5. **`make security` en CI**, para que la revisión no dependa de que alguien se
   acuerde de correrla.

---

## 5. Si encontrás una vulnerabilidad

Escribí a diprimodp@gmail.com. No abras un issue público hasta que esté arreglada.
