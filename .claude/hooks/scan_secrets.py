#!/usr/bin/env python3
"""Hook PreToolUse: bloquea un `git commit` si en el diff staged hay algo que
parece un secreto real.

Es la última barrera antes de que una clave termine publicada en GitHub. A
diferencia de una instrucción en CLAUDE.md, que es un pedido, esto es un
bloqueo: el commit no ocurre.

Entrada: JSON de Claude Code por stdin.
Salida: exit 0 deja pasar; exit 2 bloquea y le muestra a Claude el motivo.
"""
import json
import re
import subprocess
import sys

# Patrones de credenciales con formato reconocible. Un match acá es casi
# siempre un secreto real, así que no se filtra por placeholder.
PATRONES_FUERTES = [
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "clave privada"),
    (r"sk-ant-[A-Za-z0-9_\-]{20,}", "API key de Anthropic"),
    (r"\bghp_[A-Za-z0-9]{30,}", "token de GitHub"),
    (r"\bgithub_pat_[A-Za-z0-9_]{30,}", "token de GitHub (fine-grained)"),
    (r"\bAKIA[0-9A-Z]{16}\b", "access key de AWS"),
    (r"\bxox[baprs]-[A-Za-z0-9\-]{10,}", "token de Slack"),
    (r"\bAIza[0-9A-Za-z_\-]{35}\b", "API key de Google"),
    (r"\bsk_live_[A-Za-z0-9]{20,}", "clave de producción de Stripe"),
]

# Asignaciones genéricas: password = "...". Acá sí hay falsos positivos, así
# que se descartan los valores que son claramente de ejemplo.
PATRON_ASIGNACION = re.compile(
    r"""(?ix)
    \b(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|
       private[_-]?key|client[_-]?secret)\b
    \s*[:=]\s*
    ["']([^"']{8,})["']
    """
)

# Si el valor contiene alguna de estas marcas, es un placeholder, no un secreto.
MARCAS_DE_EJEMPLO = (
    "change", "cambiar", "example", "ejemplo", "placeholder", "your-", "tu-",
    "dev-only", "test", "dummy", "fake", "xxx", "...", "<", "{{", "$", "TODO",
)


def es_placeholder(valor: str) -> bool:
    minus = valor.lower()
    return any(marca.lower() in minus for marca in MARCAS_DE_EJEMPLO)


def main() -> int:
    try:
        datos = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # sin entrada legible, no bloqueamos nada

    comando = datos.get("tool_input", {}).get("command", "")
    if not re.search(r"\bgit\s+commit\b", comando):
        return 0

    cwd = datos.get("cwd") or "."

    try:
        archivos = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=30, cwd=cwd,
        ).stdout.splitlines()
        diff = subprocess.run(
            ["git", "diff", "--cached", "--unified=0"],
            capture_output=True, text=True, timeout=30, cwd=cwd,
        ).stdout
    except (subprocess.SubprocessError, OSError):
        return 0  # si git no responde, no trabamos el flujo

    hallazgos = []

    # 1. Archivos que nunca se commitean, pase lo que pase.
    for archivo in archivos:
        nombre = archivo.rsplit("/", 1)[-1]
        if nombre == ".env" or (nombre.startswith(".env.") and nombre != ".env.example"):
            hallazgos.append(f"  · el archivo {archivo} está en el commit y nunca debe subirse")

    # 2. Contenido agregado que parece una credencial.
    for linea in diff.splitlines():
        if not linea.startswith("+") or linea.startswith("+++"):
            continue
        contenido = linea[1:]

        for patron, descripcion in PATRONES_FUERTES:
            if re.search(patron, contenido):
                hallazgos.append(f"  · {descripcion} en: {contenido.strip()[:80]}")

        m = PATRON_ASIGNACION.search(contenido)
        if m and not es_placeholder(m.group(2)):
            hallazgos.append(
                f"  · posible {m.group(1)} con valor real en: {contenido.strip()[:80]}"
            )

    if not hallazgos:
        return 0

    unicos = list(dict.fromkeys(hallazgos))
    print(
        "COMMIT BLOQUEADO — hay algo que parece un secreto real:\n"
        + "\n".join(unicos)
        + "\n\nQué hacer:\n"
        "  1. Sacá el secreto del código y leelo desde una variable de entorno.\n"
        "  2. Si el archivo no debe versionarse, agregalo a .gitignore y sacalo\n"
        "     del staging con: git restore --staged <archivo>\n"
        "  3. Si es un valor de ejemplo, que lo parezca (dev-only-, change-me, etc.).\n"
        "  4. Si el secreto ya se usó en algún lado, rotalo. Asumí que está quemado.\n"
        "\nNo desactives este hook para poder commitear.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
