"""Servicio echo — devuelve un JSON con info del request. Sirve para demos."""
import os
import socket
from datetime import datetime

from fastapi import FastAPI, Request

SERVICE_NAME = os.getenv("SERVICE_NAME", "echo-service")

app = FastAPI(title=SERVICE_NAME)


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def echo(full_path: str, request: Request):
    body_bytes = await request.body()
    return {
        "service": SERVICE_NAME,
        "hostname": socket.gethostname(),
        "method": request.method,
        "path": "/" + full_path,
        "query": dict(request.query_params),
        "headers": {k: v for k, v in request.headers.items() if k.lower() not in ("authorization", "cookie")},
        "body_size": len(body_bytes),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
