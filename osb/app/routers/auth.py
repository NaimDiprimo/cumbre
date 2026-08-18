"""Google OAuth2 para autenticación en el dashboard del OSB."""
import os
import secrets
import time
import urllib.parse

import httpx
import jwt
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..security import es_entorno_productivo, require_jwt_secret

router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"  # noqa: S105 — es una URL, no una credencial
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

JWT_SECRET = require_jwt_secret()
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = 28800  # 8 horas


def _google_client_id() -> str:
    return os.getenv("GOOGLE_CLIENT_ID", "")


def _google_client_secret() -> str:
    return os.getenv("GOOGLE_CLIENT_SECRET", "")


def _redirect_uri() -> str:
    return os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")


def get_current_user(request: Request) -> dict | None:
    token = request.cookies.get("cumbre_token")
    if not token:
        return None
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        return None


@router.get("/auth/google/login", include_in_schema=False)
async def google_login():
    client_id = _google_client_id()
    if not client_id:
        return HTMLResponse(
            "<h1>Google OAuth no configurado</h1>"
            "<p>Seteá <code>GOOGLE_CLIENT_ID</code> y <code>GOOGLE_CLIENT_SECRET</code>.</p>",
            status_code=503,
        )
    state = secrets.token_urlsafe(16)
    params = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": _redirect_uri(),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
    })
    response = RedirectResponse(f"{GOOGLE_AUTH_URL}?{params}")
    response.set_cookie("oauth_state", state, httponly=True, max_age=300, samesite="lax")
    return response


@router.get("/auth/google/callback", include_in_schema=False)
async def google_callback(request: Request, code: str = "", state: str = "", error: str = ""):
    if error:
        raise HTTPException(400, f"Google OAuth error: {error}")

    stored_state = request.cookies.get("oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(400, "OAuth state inválido — posible CSRF")

    client_id = _google_client_id()
    client_secret = _google_client_secret()

    async with httpx.AsyncClient() as http:
        token_resp = await http.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": _redirect_uri(),
            "grant_type": "authorization_code",
        })
        if token_resp.status_code != 200:
            raise HTTPException(502, "Error al obtener token de Google")

        access_token = token_resp.json().get("access_token", "")
        userinfo_resp = await http.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if userinfo_resp.status_code != 200:
            raise HTTPException(502, "Error al obtener datos del usuario de Google")
        user = userinfo_resp.json()

    email = user.get("email", "")
    if not email:
        raise HTTPException(400, "No se pudo obtener el email de Google")

    now = int(time.time())
    payload = {
        "sub": email,
        "name": user.get("name", email),
        "picture": user.get("picture", ""),
        "iat": now,
        "exp": now + JWT_EXPIRE_SECONDS,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("oauth_state")
    response.set_cookie(
        "cumbre_token", token,
        httponly=True, max_age=JWT_EXPIRE_SECONDS, samesite="lax",
    )
    return response


@router.get("/auth/dev/login", include_in_schema=False)
async def dev_login():
    """Entrada de demo, sin Google.

    Existe para poder mostrar el dashboard con sesión iniciada sin tener que
    dar de alta una aplicación en Google Cloud. **Sólo funciona en desarrollo**:
    si `OSB_ENVIRONMENT` no es `dev` ni `test`, este endpoint no existe.
    """
    if es_entorno_productivo():
        raise HTTPException(404, "Not Found")

    now = int(time.time())
    token = jwt.encode(
        {
            "sub": "demo@cumbre.local",
            "name": "Usuario de demo",
            "picture": "",
            "iat": now,
            "exp": now + JWT_EXPIRE_SECONDS,
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        "cumbre_token", token,
        httponly=True, max_age=JWT_EXPIRE_SECONDS, samesite="lax",
    )
    return response


@router.get("/auth/logout", include_in_schema=False)
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("cumbre_token")
    return response
