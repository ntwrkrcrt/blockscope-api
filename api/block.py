from typing import Any, Optional

import orjson
from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from redis.asyncio import Redis
from web3 import AsyncWeb3
from web3.exceptions import Web3RPCError

from config import settings
from core.block.balance import get_balance_by_block
from core.block.web3 import get_web3_client
from core.cache.redis import get_redis_client
from core.cache.utils import build_get_query_cache_key, get_cache, set_cache
from schemas.balance import BalanceRequest, BalanceResponse

router = APIRouter(
    prefix="/block",
    tags=["block"],
)


@router.get("/{block_number}/balance/{address}/", response_model=BalanceResponse)
async def balance_by_block(
    request: Request,
    params: BalanceRequest = Depends(),
    cache: Redis = Depends(get_redis_client),
):
    """
    Get native balance in WEI in specified block
    """
    cache_key: str = build_get_query_cache_key(
        prefix="balance_by_block", url=request.url
    )

    try:
        cached: Optional[str] = await get_cache(client=cache, key=cache_key)
        if cached:
            logger.info(
                f"Cache HIT for {params.address} at block {params.block_number}"
            )
            return orjson.loads(cached)
    except Exception as e:
        logger.warning(f"Cache get failed for {cache_key}: {e}")

    try:
        web3: AsyncWeb3 = get_web3_client(chain_id=params.chain_id)
    except ValueError as e:
        msg = str(e)
        logger.error(f"Failed to get web3 client: {msg}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

    try:
        result = await get_balance_by_block(
            web3=web3, address=params.address, block_number=params.block_number
        )
    except Web3RPCError as e:
        msg = e.message
        logger.error(f"Rpc error occured: {msg}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=msg)

    logger.info(f"Block: {params.block_number} | address: {params.address}: {result}")

    response: dict[str, Any] = BalanceResponse(
        address=params.address, balance=result
    ).model_dump()

    try:
        await set_cache(
            client=cache,
            key=cache_key,
            value=orjson.dumps(response),
            ttl=settings.cache_ttl,
        )
        logger.debug(
            f"Cached balance for {params.address} at block {params.block_number}"
        )
    except Exception as e:
        logger.warning(f"Cache set failed for {cache_key}: {e}")

    return response
