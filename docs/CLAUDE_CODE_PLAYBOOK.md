# Playbook de Claude Code para Cumbre

> Cómo usan Claude Code el ingeniero que lo creó y los equipos internos de Anthropic,
> y cómo aplicamos eso concretamente en este repo.

Investigación hecha en agosto de 2026 a partir de la documentación oficial de
Anthropic, de los tips públicos de Boris Cherny (creador de Claude Code) y del caso
de estudio sobre cómo lo usan los equipos internos de Anthropic. Las fuentes están
al final.

---

## 1. La idea que explica todo lo demás

Casi todas las buenas prácticas salen de una sola restricción:

> **La ventana de contexto se llena rápido, y el rendimiento del modelo se degrada a
> medida que se llena.**

El contexto es todo lo que Claude "tiene en la cabeza" en una sesión: cada mensaje,
cada archivo que leyó, cada salida de comando. Una sola sesión de debugging puede
consumir decenas de miles de tokens. Cuando se llena, Claude empieza a "olvidar"
instrucciones de más arriba y a cometer más errores.

Todo lo que sigue —skills que cargan bajo demanda, subagentes que trabajan en su
propia ventana, `/clear` entre tareas, CLAUDE.md corto— existe para administrar ese
recurso. Si entendés esto, el resto se deduce solo.

**La segunda idea, en importancia:**

> **Dale a Claude una forma de verificar su propio trabajo.**

Claude se detiene cuando el trabajo *parece* terminado. Sin un chequeo que pueda
correr, "parece terminado" es la única señal disponible y vos sos el bucle de
verificación: cada error espera a que vos lo notes. Con un chequeo que devuelve
pasa/falla, el bucle se cierra solo: Claude trabaja, corre el chequeo, lee el
resultado e itera hasta que pase.

Boris Cherny dice que esto solo puede **duplicar o triplicar la calidad del
resultado final**. Es la razón por la que en este repo agregamos `make test` y
`make health` (ver sección 7).

---

## 2. Cómo usa Claude Code el que lo creó

Boris Cherny publicó su setup en enero de 2026 y lo fue actualizando. Su primera
aclaración es importante:

> "Mi setup puede resultar sorprendentemente vainilla. Claude Code funciona muy bien
> out of the box, así que personalmente no lo customizo mucho. No hay una única forma
> correcta de usarlo."

Sus prácticas, en orden:

**1. Auto mode es su tip número uno (mayo 2026).** Auto mode elimina los prompts de
permiso: un modelo clasificador aparte revisa cada comando antes de ejecutarlo y
bloquea sólo lo riesgoso (escalamiento de alcance, infraestructura desconocida,
acciones disparadas por contenido hostil). Es la pieza que habilita todo lo demás:
arrancás una sesión y, mientras corre sola, trabajás en otra en paralelo.

**2. Corre 5 instancias de Claude en paralelo.** Cinco pestañas de terminal
numeradas 1 a 5, cada una en un checkout de git distinto del mismo repo, para que
no se pisen los archivos. Usa las notificaciones del sistema para saber cuál
necesita atención.

**3. Suma claude.ai/code para más paralelismo todavía.** 5 a 10 sesiones en la nube
además de las locales, pasándose trabajo entre ambos entornos.

**4. Opus con thinking para todo.** Aunque sea más lento por token, necesita menos
correcciones y usa mejor las herramientas, así que **termina antes** que un modelo
más chico al que hay que estar dirigiendo.

**5. Un solo CLAUDE.md compartido con el equipo.** Todo el equipo le agrega cosas
cada semana. La regla: *"cada vez que Claude hace algo mal, agregalo al CLAUDE.md
para que la próxima vez sepa que no lo tiene que hacer"*. El archivo se vuelve una
base de conocimiento que compone valor con el tiempo.

**6. Etiqueta a @claude en los PRs para que actualice el CLAUDE.md.** Durante el
code review, menciona a Claude en el PR y la GitHub Action mejora la documentación
compartida de forma incremental. Lo llama **"Compounding Engineering"**: ingeniería
que capitaliza.

**7. Arranca casi toda sesión en plan mode** (Shift+Tab dos veces). Itera el plan
hasta que él y Claude coinciden en el alcance. Recién ahí pasa a ejecución.

**8. Slash commands para el loop diario** — `/commit-push-pr` y similares, guardados
en el repo para que Claude también los use por su cuenta.

**9. Subagentes para lo repetitivo** — `code-simplifier`, `verify-app`, guardados en
`.claude/agents/`.

**10. Un hook PostToolUse que formatea el código automáticamente** después de cada
edición.

**11. Pre-aprobar permisos en vez de `--dangerously-skip-permissions`.** Usa
`/permissions` para poner en lista blanca los comandos que sabe que son seguros, y
lo guarda en `.claude/settings.json` para compartirlo con el equipo.

**12. Claude usa todas sus herramientas vía MCP** — busca y publica en Slack, corre
queries de BigQuery para responder preguntas de analytics, trae logs de errores de
Sentry. La config de Slack está commiteada en `.mcp.json` y compartida con el equipo.

**13. Verifica las tareas largas con agentes de verificación** en segundo plano, vía
prompting, hooks de Stop, o plugins.

---

## 3. Cómo lo usan los equipos internos de Anthropic

Del caso de estudio oficial:

- **Security Engineering** pasó de "design doc → código berreta → refactor → abandonar
  los tests" a: pedirle pseudocódigo a Claude, guiarlo con desarrollo dirigido por
  tests, y chequear cada tanto.
- **Data Infrastructure** debuggeó una caída de Kubernetes **pegando capturas de
  pantalla** del dashboard y dejando que Claude los guiara por la consola hasta
  encontrar el problema: agotamiento de IPs de pods.
- Los ingenieros más avanzados corren **5 a 10 instancias simultáneas**, usan
  archivos de memoria compartidos que hacen al sistema más inteligente con cada
  commit, y automatizan el 80% del trabajo de PRs.
- Los equipos **no técnicos** también lo usan: los abogados armaron un sistema de
  árbol telefónico, marketing genera cientos de variantes de avisos procesando CSVs,
  y el equipo de finanzas escribe sus flujos de trabajo en texto plano y los carga
  en Claude Code para que se ejecuten solos.

Este último punto importa para Cumbre: **el patrón "escribí en texto plano lo que
querés que pase, y dejá que Claude lo ejecute" es exactamente el modo de trabajo de
alguien que no programa.** Es la base de las skills que dejamos configuradas.

---

## 4. Las piezas de configuración, y cuándo usar cada una

Este es el mapa completo. La columna que importa es la última.

| Pieza | Qué es | Cuándo usarla | Costo de contexto |
| --- | --- | --- | --- |
| **CLAUDE.md** | Contexto persistente que se carga en cada sesión | Convenciones del proyecto, reglas "siempre hacé X" | Alto: en cada request |
| **`.claude/rules/`** | Como CLAUDE.md pero se puede limitar por rutas | Reglas específicas de un lenguaje o carpeta | Sólo cuando aplica |
| **Skills** | Instrucciones y flujos reutilizables, en `.claude/skills/<nombre>/SKILL.md` | Material de referencia, procedimientos repetibles, comandos `/nombre` | Bajo: sólo la descripción, el cuerpo carga al usarse |
| **Subagentes** | Trabajador aislado con su propia ventana de contexto | Tareas que leen muchos archivos, verificación, trabajo en paralelo | Aislado del contexto principal |
| **Agent teams** | Varias sesiones independientes que se hablan entre sí | Investigación con hipótesis en competencia, review en paralelo | Alto: cada compañero es una instancia entera |
| **Hooks** | Un script que se dispara en un evento del ciclo de vida | Algo que tiene que pasar **siempre**, sin excepción | Cero, salvo que devuelva output |
| **MCP** | Conexión a servicios externos | Datos o acciones fuera del repo (Slack, base de datos, Sentry) | Bajo hasta que se usa una herramienta |
| **Plugins** | Empaquetado de todo lo anterior | Reusar el mismo setup en varios repos | Depende de lo que traiga |

### Las distinciones que más confunden

**CLAUDE.md vs Skill.** CLAUDE.md se carga **siempre**; una skill se carga **cuando
hace falta**. Regla práctica: si Claude tiene que saberlo siempre (convenciones,
comandos de build, "nunca hagas X"), va en CLAUDE.md. Si es material de referencia
que necesita a veces, o un flujo que disparás con `/nombre`, va en una skill.
**Mantené CLAUDE.md por debajo de 200 líneas.**

**Hook vs instrucción.** Una instrucción en CLAUDE.md tipo "nunca edites `.env`" es
**un pedido, no una garantía**. Un hook `PreToolUse` que bloquea la edición es
**cumplimiento**. Si una regla tiene que valer siempre, hacela un hook o una regla
`deny` de permisos, no una frase en un prompt.

**Subagente vs agent team.** Un subagente reporta sólo al agente principal. Los
miembros de un agent team se hablan entre ellos y comparten una lista de tareas. Usá
subagentes para "andá, averiguá esto y contame"; usá teams cuando necesitás que
discutan y se contradigan entre sí. Los teams son experimentales y hay que
habilitarlos con `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.

**MCP vs Skill.** MCP da la **conexión** (acceso a la base de datos). Una skill da el
**conocimiento** de cómo usarla bien (nuestro modelo de datos, qué tablas mirar).
Se combinan.

### En qué orden agregar cosas

No hace falta configurar todo de entrada. Cada pieza tiene un disparador:

| Cuando pasa esto... | Agregá esto |
| --- | --- |
| Claude se equivoca dos veces en la misma convención | Una línea en CLAUDE.md |
| Escribís el mismo prompt para arrancar una tarea, otra vez | Una skill invocable con `/nombre` |
| Pegás el mismo procedimiento en el chat por tercera vez | Una skill |
| Copiás datos de una pestaña del navegador que Claude no ve | Un servidor MCP |
| Una tarea lateral te inunda la conversación de output | Un subagente |
| Querés que algo pase siempre, sin preguntar | Un hook |
| Un segundo repo necesita el mismo setup | Un plugin |

---

## 5. Modos de permiso

El modo define cuánto te interrumpe Claude. Se cicla con **Shift+Tab**.

| Modo | Qué corre sin preguntar | Para qué |
| --- | --- | --- |
| `default` (Manual) | Sólo lecturas | Empezar, trabajo sensible |
| `acceptEdits` | Lecturas, ediciones de archivos, comandos de filesystem | Iterar sobre código que estás revisando |
| `plan` | Lecturas, y exploración; **no edita nada** | Explorar antes de cambiar |
| `auto` | Todo, con chequeos de seguridad de fondo | Tareas largas, sesiones desatendidas |
| `bypassPermissions` | Todo, sin ningún chequeo | **Sólo** en contenedores aislados |

**Auto mode** es el que cambia el juego. Un clasificador revisa cada llamada a
herramienta y bloquea lo irreversible, lo destructivo y lo que apunta hacia afuera.
Si bloquea 3 veces seguidas o 20 en total, se desactiva solo y vuelve a preguntar.
El clasificador ve tus mensajes, las llamadas a herramientas y tu CLAUDE.md, pero
**no** ve los resultados de las herramientas, así que contenido hostil dentro de un
archivo o una página web no lo puede manipular directamente.

Anthropic anunció que auto mode pasa a ser **el default para los planes Pro, Max y
Team a partir del 14 de agosto de 2026**.

`bypassPermissions` (el viejo `--dangerously-skip-permissions`) **no** ofrece
protección contra inyección de prompts. La recomendación explícita de la doc y de
Boris es usar auto mode o listas blancas en vez de eso.

Para fijar un modo por defecto, va en `.claude/settings.json`:

```json
{ "permissions": { "defaultMode": "plan" } }
```

---

## 6. Paralelismo: las cuatro formas

1. **Worktrees de git** — varias sesiones de CLI, cada una en un checkout aislado.
   Es lo que hace Boris con sus 5 pestañas.
2. **Claude Code en la web** (claude.ai/code) — sesiones en la nube, sin setup local.
   Corren en un contenedor efímero de Anthropic, no en tu máquina.
3. **Remote Control** — una sesión que corre **en tu máquina** y que manejás desde el
   celular o el navegador. Ver la sección 8.
4. **Agent teams** — varias sesiones coordinadas automáticamente, con lista de tareas
   compartida y mensajería entre ellas. Experimental.

**El patrón Escritor/Revisor** merece mención aparte, porque no es sobre velocidad
sino sobre calidad: una sesión escribe el código, **otra sesión distinta** lo revisa.
La segunda tiene contexto fresco y no está sesgada a favor del código que acaba de
escribir. Lo mismo aplica con tests: una sesión escribe los tests, otra escribe el
código que los tiene que hacer pasar.

---

## 7. Qué quedó configurado en este repo

Todo esto ya está commiteado y funciona.

### `CLAUDE.md` (raíz)

El archivo que Claude lee al empezar cada sesión. Tiene los comandos, los puertos,
las convenciones (todo en castellano, commits conventional), y sobre todo la
instrucción de **explicar los resultados en lenguaje simple y mostrar evidencia**,
porque el dueño del proyecto no programa.

También tiene la sección "cosas que NO hay que hacer", con las dos trampas reales de
este repo: nunca commitear `.env`, y no editar a mano la config dinámica de Envoy
(la genera Sovereign a partir de las plantillas).

**Este archivo es el que más valor acumula con el tiempo.** Cada vez que Claude se
equivoque en algo del proyecto, agregale una línea. Es la práctica número uno de
Boris y de los equipos de Anthropic.

### `make test` y `make health` (nuevos)

Antes no había forma de que Claude verificara su propio trabajo: no existía un
comando de tests. Ahora sí:

- `make test` — arma un entorno virtual la primera vez y corre los 64 tests del OSB
  en menos de un segundo. **No necesita docker.**
- `make health` — chequea que los 5 servicios expuestos respondan.

Esto es lo más importante de todo lo que se agregó. Es el bucle de verificación que,
según Boris, duplica o triplica la calidad del resultado.

### `.claude/settings.json`

- `defaultMode: "plan"` — toda sesión arranca en modo plan. Claude explora y propone
  antes de tocar nada, y vos aprobás. Es la práctica de Boris ("arranco casi toda
  sesión en plan mode") y es especialmente útil cuando no leés código: ves el alcance
  antes de que pase.
  **Si te resulta molesto, cambiá esa línea a `"acceptEdits"`.**
- Lista blanca de comandos seguros (`make`, `git status`, `git diff`, `docker-compose
  ps`, `curl` a localhost, pytest). Menos interrupciones sin bajar la guardia.
- Reglas `deny` sobre `.env`: Claude **no puede leer ni escribir** ese archivo. Esto
  importa especialmente con Remote Control, porque mientras está conectado la
  transcripción de la sesión se guarda en servidores de Anthropic. Un secreto que
  Claude lee es un secreto que queda en la transcripción.

### Skills (`.claude/skills/`)

| Comando | Qué hace |
| --- | --- |
| `/verificar` | Corre los tests, chequea los servicios y prueba tráfico real contra Envoy. Muestra la salida real de cada comando, no un resumen. |
| `/explicame <cosa>` | Explica un archivo, un cambio o un concepto en castellano simple, sin jerga, con el comando exacto para verificarlo y una frase lista para usar con un cliente. |
| `/entregar` | Verifica, revisa el diff buscando secretos, commitea en castellano con formato conventional y pushea. Nunca a `main` sin permiso. |

`/explicame` y `/entregar` tienen `disable-model-invocation: true`: sólo se disparan
si los escribís vos. Eso las hace gratis en contexto y evita que Claude commitee por
su cuenta.

### Subagentes (`.claude/agents/`)

| Agente | Para qué |
| --- | --- |
| `revisor-seguridad` | Revisa cambios en auth, JWT, sidecar, rate limiting o config de Envoy. Busca bypass de auth, secretos hardcodeados, puertos de admin expuestos, inyección en las plantillas Jinja de Sovereign. |
| `revisor-adversario` | Revisa un cambio ya hecho con contexto fresco: ¿hace lo que se pidió? ¿está verificado de verdad? ¿se rompió algo más? Corre los tests él mismo en vez de confiar. |

Para usarlos: *"usá el subagente revisor-seguridad para revisar este cambio"*.

Corren en su propia ventana de contexto, así que pueden leer 40 archivos sin
ensuciarte la conversación principal.

---

## 8. Remote Control: manejar la sesión desde el celular

Remote Control conecta claude.ai/code o la app del celular a una sesión que corre
**en tu máquina**. El código y los archivos nunca salen de tu computadora; la web y
el celular son sólo una ventana.

Desde la carpeta del proyecto:

```bash
claude --remote-control "cumbre"
```

**Ojo con una trampa específica de este repo:** `.env.example` incluye
`ANTHROPIC_API_KEY`. Si copiás ese archivo a `.env` y lo cargás en tu terminal (con
`source .env`, `export $(cat .env)` o similar), esa variable queda definida en tu
shell y **Remote Control deja de funcionar**: sólo anda con login de claude.ai, no
con API key. Lo mismo pasa con `ANTHROPIC_BASE_URL`.

Si Remote Control no arranca, esa es la primera cosa a chequear.

---

## 9. Lo que todavía no está, y en qué orden conviene hacerlo

Ordenado por relación valor/esfuerzo:

1. **Un servidor MCP de GitHub o de la base de datos.** Es el paso que más
   capacidad agrega: Claude podría consultar directamente la base del OSB para
   debuggear, o manejar issues y PRs sin que le pases nada por copiar y pegar. Se
   configura con `claude mcp add` y se commitea en `.mcp.json` para compartirlo.
2. **Un hook PostToolUse que formatee el Python** después de cada edición. Requiere
   elegir un formateador primero (`ruff` es la opción obvia para este stack). Hoy el
   proyecto no tiene ninguno configurado, y por eso no lo agregamos.
3. **Un plugin de code intelligence para Python**, para que Claude navegue símbolos
   en vez de leer archivos enteros. Ahorra contexto en un repo que ya tiene 61
   archivos.
4. **La GitHub Action de Claude**, para poder etiquetar `@claude` en un PR y que
   revise o actualice el CLAUDE.md solo — el "compounding engineering" de Boris.
5. **Agent teams**, cuando haya varias features en paralelo. Hoy, con un solo
   desarrollador y un solo hilo de trabajo, agregaría más costo que beneficio.

---

## 10. Los errores que hay que evitar

De la documentación oficial, con el nombre que les pone:

- **La sesión bolsa de gatos.** Empezás con una tarea, preguntás algo sin relación,
  volvés a la primera. El contexto queda lleno de ruido. → `/clear` entre tareas
  distintas.
- **Corregir una y otra vez.** Claude hace algo mal, lo corregís, sigue mal, lo
  corregís de nuevo. El contexto se contamina de intentos fallidos. → Después de dos
  correcciones fallidas, `/clear` y volvé a escribir el pedido desde cero
  incorporando lo que aprendiste. Una sesión limpia con mejor prompt casi siempre
  gana.
- **El CLAUDE.md sobrecargado.** Si es muy largo, Claude ignora la mitad porque las
  reglas importantes se pierden en el ruido. → Podá sin piedad. Para cada línea
  preguntate: *"¿sacar esto haría que Claude se equivoque?"*. Si no, borrala.
- **Confiar sin verificar.** Una implementación que se ve bien pero no maneja los
  casos borde. → Siempre un chequeo: tests, script, captura de pantalla. Si no lo
  podés verificar, no lo mandes a producción.
- **La exploración infinita.** Le pedís "investigá esto" sin acotar y Claude lee
  cientos de archivos. → Acotá la investigación o mandala a un subagente, para que no
  se coma tu contexto.

---

## 11. Comandos de todos los días

| Comando | Para qué |
| --- | --- |
| `Shift+Tab` | Ciclar modo de permisos (manual → acceptEdits → plan) |
| `/clear` | Limpiar el contexto entre tareas sin relación |
| `/context` | Ver qué está cargado y cuánto contexto ocupa |
| `Esc` | Frenar a Claude en la mitad de una acción, sin perder el contexto |
| `Esc Esc` o `/rewind` | Volver atrás la conversación, el código, o ambos |
| `/compact <instrucción>` | Comprimir la conversación conservando lo que importa |
| `@archivo` | Referenciar un archivo en el prompt |
| `/btw` | Preguntar algo al margen, sin que la respuesta ensucie el contexto |
| `/code-review` | Review de correctitud del diff actual, en un subagente |
| `Ctrl+G` | Abrir el plan propuesto en tu editor para corregirlo a mano |

**Un truco que vale la pena para features grandes:** pedirle a Claude que te
entreviste antes de empezar.

> *Quiero construir [descripción breve]. Entrevistame en detalle usando la
> herramienta AskUserQuestion. Preguntame sobre implementación técnica, UI/UX, casos
> borde, riesgos y compromisos. No hagas preguntas obvias, metete en las partes
> difíciles que quizá no consideré. Seguí entrevistándome hasta cubrir todo, después
> escribí una especificación completa en SPEC.md.*

Después arrancás una sesión nueva y limpia para ejecutar el SPEC.md.

---

## Fuentes

- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) — documentación oficial
- [Extend Claude Code: cuándo usar cada pieza](https://code.claude.com/docs/en/features-overview)
- [Choose a permission mode](https://code.claude.com/docs/en/permission-modes)
- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams)
- [Continue local sessions with Remote Control](https://code.claude.com/docs/en/remote-control)
- [How Anthropic teams use Claude Code](https://claude.com/blog/how-anthropic-teams-use-claude-code) — caso de estudio interno
- [13 tips de Boris Cherny (enero 2026)](https://github.com/shanraisshan/claude-code-best-practice/blob/main/tips/claude-boris-13-tips-03-jan-26.md)
- [6 tips de Boris Cherny (abril 2026)](https://github.com/shanraisshan/claude-code-best-practice/blob/main/tips/claude-boris-6-tips-16-apr-26.md)
- [Boris Cherny sobre auto mode](https://x.com/bcherny/status/2058519809214607704)
- [Auto mode pasa a ser el default](https://techcrunch.com/2026/08/09/anthropic-is-turning-claude-codes-auto-mode-on-by-default/)
- [bcherny-claude: recopilación de su configuración](https://github.com/0xquinto/bcherny-claude)
