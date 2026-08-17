"""Hook Stop: no deja cerrar el turno si se tocó código Python y los tests fallan.

Una instrucción como "corré los tests antes de terminar" es un pedido. Esto es
un portón: si los tests están en rojo, el turno no termina y Claude tiene que
seguir trabajando.

Sólo se activa si hay archivos .py modificados en osb/ o sovereign/. Editar
documentación no dispara nada.
"""
import json
import os
import subprocess
import sys

VENV = ".venv-test/bin/python"


def hay_python_modificado(cwd: str) -> bool:
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=30, cwd=cwd,
        )
    except (subprocess.SubprocessError, OSError):
        return False

    for linea in r.stdout.splitlines():
        ruta = linea[3:].strip()
        # Los renombres vienen como "viejo -> nuevo"
        if " -> " in ruta:
            ruta = ruta.split(" -> ", 1)[1]
        if ruta.endswith(".py") and (
            ruta.startswith("osb/") or ruta.startswith("sovereign/")
        ):
            return True
    return False


def main() -> int:
    try:
        datos = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    # Si ya bloqueamos una vez y Claude sigue trabajando por eso, no volvemos
    # a bloquear en cadena.
    if datos.get("stop_hook_active"):
        return 0

    cwd = datos.get("cwd") or "."

    if not os.path.exists(os.path.join(cwd, VENV)):
        return 0  # sin entorno de test armado; `make test` lo crea

    if not hay_python_modificado(cwd):
        return 0

    python = os.path.abspath(os.path.join(cwd, VENV))
    try:
        r = subprocess.run(
            [python, "-m", "pytest", "tests/", "-q", "--no-header"],
            capture_output=True, text=True, timeout=300,
            cwd=os.path.join(cwd, "osb"),
        )
    except subprocess.TimeoutExpired:
        print(
            "Los tests tardaron más de 5 minutos y se cortaron. Revisá si algo "
            "quedó colgado antes de dar el trabajo por terminado.",
            file=sys.stderr,
        )
        return 2
    except (subprocess.SubprocessError, OSError):
        return 0

    if r.returncode == 0:
        return 0

    salida = (r.stdout or "") + (r.stderr or "")
    print(
        "No podés terminar el turno: tocaste código Python y los tests fallan.\n\n"
        f"{salida[-3000:]}\n"
        "Arreglá la causa raíz y volvé a correr `make test`. No marques tests "
        "como skip ni suprimas el error para que pase.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
