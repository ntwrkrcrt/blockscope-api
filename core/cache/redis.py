from typing import Optional

from redis import asyncio as redis_async

from config import settings

_redis_client: Optional[redis_async.Redis] = None


async def init_redis() -> None:
    global _redis_client
    _redis_client = redis_async.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )


async def get_redis_client() -> redis_async.Redis:
    if _redis_client is None:
        raise RuntimeError("Redis not initialized")
    return _redis_client


async def shutdown_redis() -> None:
    if _redis_client:
        await _redis_client.close()
