---
name: explicame
description: Explicar en castellano simple, para alguien que no programa, qué hace un cambio, un archivo o una parte de Cumbre. Usalo cuando pidan "explicame esto", "qué hace esto", "qué cambiaste" o cuando haya que traducir algo técnico a lenguaje de negocio.
argument-hint: "[archivo, cambio o concepto]"
disable-model-invocation: true
---

# Explicame: $ARGUMENTS

Explicá esto para **Naim, el dueño del proyecto, que no programa**. Es vendedor y
necesita entender lo suficiente para tomar decisiones y para explicárselo a un
cliente FinTech.

## Reglas

- Castellano simple. Cero jerga sin traducir. Si usás un término técnico
  (idempotente, XDS, sidecar), explicalo en la misma frase la primera vez.
- Analogías concretas antes que definiciones abstractas.
- Nada de código en la explicación principal. Si hace falta mostrar código, va al
  final, en una sección aparte marcada como opcional.
- Sé honesto sobre lo que no está terminado o no funciona. Un "esto todavía no
  anda" vale más que un optimismo que se cae en una demo.

## Estructura

1. **Qué es / qué hace** — dos o tres frases.
2. **Por qué importa para Cumbre** — qué problema del cliente resuelve, o qué
   pasaría si no existiera.
3. **Cómo lo verifico yo mismo** — el comando o la URL exacta que Naim puede
   correr o abrir para verlo con sus propios ojos.
4. **Qué le diría a un cliente** — una o dos frases listas para usar en una demo
   o en un mail, sin exagerar lo que la plataforma hace hoy.
