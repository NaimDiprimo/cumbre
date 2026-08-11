---
name: entregar
description: Cerrar un cambio en Cumbre — verificar, commitear en castellano con formato conventional y pushear a la rama actual. Usalo cuando digan "entregá esto", "commiteá y subí" o "cerrá el cambio".
argument-hint: "[descripción del cambio, opcional]"
disable-model-invocation: true
---

# Entregar el cambio

## 1. Verificar antes de commitear

Corré `make test`. Si falla algo, **parás acá**: arreglalo o avisá, pero no
commitees rojo.

## 2. Revisar qué se va a commitear

```bash
git status
git diff
```

Revisá la lista archivo por archivo:

- ¿Se está por commitear `.env`, una clave, un token o una contraseña real?
  **Frená y avisá.** No lo commitees.
- ¿Hay archivos temporales, logs o `.venv-test/` colándose? Sacalos del commit.
- ¿Hay cambios que no tienen nada que ver con lo pedido? Preguntá antes de incluirlos.

## 3. Commitear

Mensaje en castellano, formato conventional, igual que el historial del repo:

```
feat(osb): agregar filtro por equipo en el catálogo de servicios
fix(sovereign): corregir el cluster name cuando el upstream tiene guiones
docs: actualizar CONTEXT.md con el estado del rate limiting
```

El cuerpo del commit, si hace falta, explica **por qué** se hizo el cambio, no qué
líneas se tocaron — eso ya está en el diff.

## 4. Pushear

```bash
git push -u origin $(git branch --show-current)
```

Nunca pushees a `main` sin que te lo pidan explícitamente. Si estás parado en
`main`, creá una rama primero.

## 5. Informe

Decí en castellano simple: qué cambió, en qué rama quedó, y qué tendría que mirar
Naim para confirmar que está bien.
