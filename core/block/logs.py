from eth_typing import BlockIdentifier, BlockNumber, ChecksumAddress
from web3 import AsyncWeb3
from web3.types import FilterParams, LogReceipt

from config import settings
from core.exceptions.logs import MaxBlockRangeLimit


async def get_logs_by_block_period(
    web3: AsyncWeb3,
    address: ChecksumAddress,
    from_block: BlockIdentifier,
    to_block: BlockIdentifier | None = None,
) -> list[LogReceipt]:
    if to_block is None:
        to_block: BlockNumber = await web3.eth.get_block_number()

    if to_block - from_block > settings.max_block_range:
        raise MaxBlockRangeLimit(f"Max block range limit is {settings.max_block_range}")

    filter_params: FilterParams = {
        "address": address,
        "fromBlock": from_block,
        "toBlock": to_block,
    }

    return await web3.eth.get_logs(filter_params=filter_params)
