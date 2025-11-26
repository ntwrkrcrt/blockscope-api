import hashlib
from typing import Optional

from redis.asyncio import Redis


async def get_cache(client: Redis, key: str) -> Optional[str]:
    return await client.get(name=key)


async def set_cache(client: Redis, key: str, value: bytes, ttl: int) -> bool:
    return await client.setex(name=key, time=ttl, value=value)


async def delete_cache(client: Redis, key: str) -> None:
    await client.delete(key)


def build_get_query_cache_key(prefix: str, url: str) -> str:
    return f"{prefix}:{hashlib.sha256(str(url).encode()).hexdigest()}"
