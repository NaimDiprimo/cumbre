---
name: seguridad
description: Auditoría de seguridad de Cumbre — corre el escaneo automático (linter bandit, secretos, dependencias vulnerables) y lanza el revisor de seguridad sobre los cambios. Usalo antes de una demo con un cliente, antes de un release, o cuando se tocó auth, ruteo o algo expuesto.
argument-hint: "[qué revisar, opcional]"
disable-model-invocation: true
---

# Auditoría de seguridad

## 1. Escaneo automático

```bash
make security
```

Chequea cuatro cosas: el linter de seguridad (reglas de bandit), credenciales con
formato reconocible en los archivos versionados, si `.env` se coló al repo, y
dependencias con vulnerabilidades conocidas.

Mostrá la salida completa. Si aparece algo, no lo minimices.

## 2. Revisión del cambio

Si hay cambios sin commitear o commiteados recientemente, lanzá el subagente:

> usá el subagente `revisor-seguridad` para revisar estos cambios

Corre en su propia ventana de contexto, así que puede leer todo el código de auth
sin ensuciar la conversación.

## 3. Chequeos que la máquina no puede hacer sola

Revisalos a mano y reportá el estado de cada uno:

- **Secretos**: ¿`CUMBRE_JWT_SECRET` está definida y es propia, no uno de los
  valores de ejemplo del repo? En producción el servicio se niega a arrancar si no,
  pero verificá que el `.env` real lo tenga.
- **Puertos**: en `docker-compose.yml`, ¿sigue siendo `10000` el único puerto que
  tendría que ver internet? Ver `.claude/rules/seguridad-ruteo.md`.
- **Endpoints abiertos**: listá los servicios con `requires_auth: false` y confirmá
  que cada uno esté abierto a propósito.
- **`/docs`**: sólo tiene que estar visible cuando `OSB_ENVIRONMENT` es `dev`.

## 4. Informe

En castellano simple, ordenado por gravedad:

- Qué está bien (decilo, sirve para la conversación con un cliente).
- Qué está mal, cómo se explota y qué hay que hacer.
- Qué es un riesgo aceptado y por qué (ej. las dependencias de Sovereign, ver
  `docs/SEGURIDAD.md`).

Nada de inventar hallazgos menores para llenar el informe. Si está limpio, decilo.
