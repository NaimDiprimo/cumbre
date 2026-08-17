#!/usr/bin/env python3
"""Hook PostToolUse: pasa el linter de seguridad sobre el archivo Python que
Claude acaba de editar.

Corre las reglas de bandit (flake8-bandit, prefijo S) más los errores de
sintaxis y las variables sin usar. Si encuentra algo, se lo devuelve a Claude
en el mismo turno para que lo arregle antes de seguir.

No reformatea el archivo: un reformateo masivo ensucia el diff y hace
imposible revisar qué cambió de verdad.
"""
import json
import os
import subprocess
import sys

RUFF = ".venv-test/bin/ruff"
REGLAS = ["--select", "S,E9,F821,F401", "--ignore", "S101"]


def main() -> int:
    try:
        datos = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    archivo = datos.get("tool_input", {}).get("file_path", "")
    if not archivo.endswith(".py"):
        return 0

    cwd = datos.get("cwd") or "."
    ruff = os.path.join(cwd, RUFF)
    if not os.path.exists(ruff):
        return 0  # entorno de test sin armar; `make test` lo crea

    if not os.path.exists(archivo):
        return 0  # el archivo pudo haberse borrado o movido

    try:
        r = subprocess.run(
            [ruff, "check", "--no-cache", *REGLAS, archivo],
            capture_output=True, text=True, timeout=60, cwd=cwd,
        )
    except (subprocess.SubprocessError, OSError):
        return 0

    if r.returncode == 0:
        return 0

    print(
        f"El linter de seguridad encontró problemas en {archivo}:\n\n"
        f"{r.stdout}\n"
        "Arreglá la causa, no silencies la regla con un `# noqa` salvo que sea "
        "un falso positivo y lo justifiques en un comentario.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
