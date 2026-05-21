"""Broadcaster SSE para notificaciones en tiempo real al dashboard."""
import asyncio
import json
from typing import AsyncGenerator, Set

_subscribers: Set[asyncio.Queue] = set()


def broadcast(event_type: str, data: dict) -> None:
    payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    for q in list(_subscribers):
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            pass


async def subscribe() -> AsyncGenerator[str, None]:
    q: asyncio.Queue = asyncio.Queue(maxsize=50)
    _subscribers.add(q)
    try:
        yield ": keepalive\n\n"
        while True:
            try:
                msg = await asyncio.wait_for(q.get(), timeout=25.0)
                yield msg
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"
    finally:
        _subscribers.discard(q)
