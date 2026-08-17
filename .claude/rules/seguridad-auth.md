---
paths:
  - "osb/app/routers/auth.py"
  - "osb/app/security.py"
  - "auth-sidecar/**"
---

# Reglas para el código de autenticación

Este código decide quién entra a la plataforma de un cliente FinTech. Un error
acá no es un bug, es una brecha.

- **Nunca** un secreto con valor por defecto que funcione en producción. Si falta
  la variable de entorno y el entorno no es `dev`, el servicio tiene que **negarse
  a arrancar** (`raise RuntimeError`), no seguir con un default. Ver
  `require_jwt_secret()` en `osb/app/security.py`.
- El OSB firma los tokens y el sidecar los valida: **ambos tienen que usar
  exactamente el mismo secreto y el mismo algoritmo**. Si tocás uno, revisá el otro.
- El algoritmo se fija explícitamente en el código (`HS256`). Nunca dejes que el
  token elija su propio algoritmo, y nunca aceptes `none`.
- Al decodificar, verificá siempre expiración. No desactives `verify_exp` ni
  ninguna verificación para "que ande".
- Los mensajes de error no filtran nada del payload ni del token. "token inválido"
  y listo: no le digas al atacante qué parte falló.
- Todo endpoint nuevo arranca **cerrado**. Si tiene que ser público, que sea una
  decisión explícita y comentada, no un olvido.
- Cambios acá necesitan test. Si agregás una validación, agregá el test que prueba
  que rechaza el caso malo, no sólo que acepta el bueno.
