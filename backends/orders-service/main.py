"""Servicio de órdenes — backend de demo con datos sintéticos.

Útil para demos a clientes FinTech: simula una API de órdenes/pagos.
"""
import random
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException

app = FastAPI(title="orders-service", version="0.1.0")

# Datos sintéticos en memoria
_ORDERS = {}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
@app.get("/orders")
def list_orders(limit: int = 20):
    return {"items": list(_ORDERS.values())[-limit:], "total": len(_ORDERS)}


@app.post("/orders")
def create_order():
    oid = str(uuid.uuid4())
    order = {
        "id": oid,
        # noqa justificado: es un backend de demo que inventa pedidos falsos
        # para las pruebas de ruteo. No hay nada criptográfico acá.
        "amount_clp": random.randint(5000, 250000),  # noqa: S311
        "status": random.choice(["created", "paid", "shipped"]),  # noqa: S311
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    _ORDERS[oid] = order
    return order


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    if order_id not in _ORDERS:
        raise HTTPException(status_code=404, detail="order not found")
    return _ORDERS[order_id]
