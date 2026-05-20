"""Cola de tareas en Redis. Equivalente a SQS en la arquitectura de Vasilios."""
import json

import redis

from .config import settings

QUEUE_KEY = "cumbre:osb:provision-queue"
DLQ_KEY = "cumbre:osb:dead-letter"


def get_redis() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)


def enqueue(action: str, service_id: str, payload: dict | None = None) -> None:
    """Encola un trabajo para que el worker lo procese.

    action: 'provision' | 'update' | 'delete'
    """
    r = get_redis()
    msg = {"action": action, "service_id": service_id, "payload": payload or {}}
    r.lpush(QUEUE_KEY, json.dumps(msg))


def dequeue(timeout: int = 5) -> dict | None:
    """Bloquea hasta que llegue un mensaje o expire el timeout."""
    r = get_redis()
    item = r.brpop(QUEUE_KEY, timeout=timeout)
    if not item:
        return None
    _, raw = item
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        r.lpush(DLQ_KEY, raw)
        return None


def queue_depth() -> int:
    return get_redis().llen(QUEUE_KEY)
