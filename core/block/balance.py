from eth_typing import BlockNumber, ChecksumAddress
from web3 import AsyncWeb3
from web3.types import Wei


async def get_balance_by_block(
    web3: AsyncWeb3, address: ChecksumAddress, block_number: BlockNumber
) -> Wei:
    return await web3.eth.get_balance(account=address, block_identifier=block_number)
