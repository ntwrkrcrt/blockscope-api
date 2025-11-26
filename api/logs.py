from typing import Any, Optional

import orjson
from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from redis.asyncio import Redis
from web3 import AsyncWeb3
from web3.types import LogReceipt

from config import settings
from core.block.logs import get_logs_by_block_period
from core.block.web3 import get_web3_client
from core.cache.redis import get_redis_client
from core.cache.utils import build_get_query_cache_key, get_cache, set_cache
from core.exceptions.logs import MaxBlockRangeLimit
from schemas.logs import LogRequest, LogResponse

router = APIRouter(
    prefix="/logs",
    tags=["logs"],
)


@router.get("/", response_model=LogResponse)
async def logs_by_block_period(
    request: Request,
    cache: Redis = Depends(get_redis_client),
    params: LogRequest = Depends(),
):
    """
    Get 0x66357dCaCe80431aee0A7507e2E361B7e2402370 logs from X to Y blocks range on Avalanche
    """
    cache_key: str = build_get_query_cache_key(
        prefix="logs_by_block_period", url=request.url
    )
    try:
        cached: Optional[str] = await get_cache(client=cache, key=cache_key)
        if cached:
            logger.info(f"Cache HIT for blocks {params.from_block} - {params.to_block}")
            return orjson.loads(cached)
    except Exception as e:
        logger.warning(f"Cache get failed for {cache_key}: {e}")

    try:
        web3: AsyncWeb3 = get_web3_client()  # Default Avalanche
    except ValueError as e:
        msg = str(e)
        logger.error(f"Failed to get web3 client: {msg}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    try:
        result: list[LogReceipt] = await get_logs_by_block_period(
            web3=web3,
            address=settings.CONTRACT_ADDRESS,
            from_block=params.from_block,
            to_block=params.to_block,
        )
    except MaxBlockRangeLimit as e:
        msg = e.message
        logger.error(f"MaxBlockRangeLimit error occured: {msg}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    logger.info(
        f"Contract logs from {params.from_block} to {params.to_block} returned: {len(result)} log receipt"
    )

    response: dict[str, Any] = LogResponse(logs=result).model_dump()

    try:
        await set_cache(
            client=cache,
            key=cache_key,
            value=orjson.dumps(response),
            ttl=settings.cache_ttl,
        )
        logger.debug(
            f"Cached result for blocks {params.from_block} - {params.to_block}"
        )
    except Exception as e:
        logger.warning(f"Cache set failed for {cache_key}: {e}")

    return response
