from typing import Optional

from web3 import AsyncHTTPProvider, AsyncWeb3

from config import settings
from core.exceptions.client import EmptyClientsException

AVAILABLE_CHAINS = {
    1: settings.ETH_RPC,
    43114: settings.AVAX_RPC,
}


_web3_clients: dict[int, AsyncWeb3] = {}


async def init_web3_pool() -> None:
    global _web3_clients
    for chain_id, rpc_url in AVAILABLE_CHAINS.items():
        if rpc_url:
            _web3_clients[chain_id] = AsyncWeb3(AsyncHTTPProvider(endpoint_uri=rpc_url))

    if not _web3_clients:
        raise EmptyClientsException("No clients to initialize")


async def shutdown_web3_pool() -> None:
    global _web3_clients
    for client in _web3_clients.values():
        await client.provider.disconnect()
    _web3_clients.clear()


def get_web3_client(chain_id: Optional[int] = None) -> AsyncWeb3:
    if chain_id is None:
        chain_id = 43114  # Default Avalanche

    if not _web3_clients:
        raise RuntimeError("Web3 clients not initialized")

    if chain_id not in _web3_clients:
        raise ValueError(f"Chain ID {chain_id} is not supported")

    return _web3_clients[chain_id]
