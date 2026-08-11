---
name: verificar
description: Verificar que Cumbre sigue funcionando después de un cambio — corre los tests del OSB y, si la plataforma está levantada, chequea que los servicios responden y que el tráfico llega a Envoy. Usalo antes de commitear o cuando haya que confirmar que algo no se rompió.
argument-hint: "[qué cambió, opcional]"
---

# Verificar Cumbre

Comprobá que el proyecto sigue sano. Mostrá siempre la **salida real** de cada
comando, no un resumen tuyo.

## 1. Tests (siempre)

```bash
make test
```

No necesita docker. Deberían pasar los 64 tests. Si alguno falla:

- Leé el traceback completo antes de tocar nada.
- Arreglá la **causa raíz**. Nunca marques un test como skip ni suprimas el error
  para que pase.
- Volvé a correr `make test` hasta que pase, y mostrá la salida final.

## 2. Servicios (sólo si la plataforma está levantada)

```bash
make ps
make health
```

Si `make ps` muestra que no hay contenedores corriendo, decilo y saltate este paso
— no levantes la plataforma por tu cuenta salvo que te lo pidan.

Si hay servicios caídos o reiniciándose, traé sus logs:

```bash
docker-compose logs --tail=50 <servicio>
```

## 3. Tráfico real (sólo si la plataforma está levantada)

```bash
make test-edge
```

Esto prueba el camino completo: Envoy recibe el request, consulta la config que le
dio Sovereign y lo rutea al backend. Si falla acá pero los tests pasan, el problema
casi siempre está en `sovereign/plugins/osb_context.py` o en las plantillas
`sovereign/templates/*.j2`, no en Envoy.

## 4. Informe final

Cerrá con un resumen en castellano simple:

- Qué corriste y qué devolvió cada cosa.
- Verde o rojo, sin ambigüedad.
- Si algo quedó roto y no lo arreglaste, decí exactamente qué y por qué.
