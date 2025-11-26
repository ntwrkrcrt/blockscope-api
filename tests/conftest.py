import os
import sys
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("AVAX_RPC", "https://api.avax-test.network/ext/bc/C/rpc")
os.environ.setdefault("ETH_RPC", "https://eth-mainnet.g.alchemy.com/v2/demo")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("CONTRACT_ADDRESS", "0x66357dCaCe80431aee0A7507e2E361B7e2402370")

sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.cache.redis import get_redis_client
from main import app as fastapi_app


class FakeRedis:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def get(self, name: str) -> str | None:
        return self._store.get(name)

    async def setex(self, name: str, time: int, value: str) -> bool:
        self._store[name] = value
        return True

    async def delete(self, name: str) -> None:
        self._store.pop(name, None)


@pytest.fixture(name="app")
def app_fixture() -> FastAPI:
    return fastapi_app


@pytest.fixture
def fake_redis() -> FakeRedis:
    return FakeRedis()


@pytest.fixture(autouse=True)
def override_redis_dependency(
    app: FastAPI, fake_redis: FakeRedis
) -> AsyncIterator[None]:
    async def _get_client_override() -> FakeRedis:
        return fake_redis

    app.dependency_overrides[get_redis_client] = _get_client_override

    yield

    app.dependency_overrides.pop(get_redis_client, None)


@pytest.fixture(autouse=True)
def fake_web3_clients(monkeypatch: pytest.MonkeyPatch) -> dict[int, object]:
    class _DummyEth:
        async def get_balance(self, *_, **__):
            return 0

        async def get_logs(self, *_, **__):
            return []

        async def get_block_number(self) -> int:
            return 0

    class _DummyWeb3:
        def __init__(self, name: str) -> None:
            self.name = name
            self.eth = _DummyEth()

    clients = {
        43114: _DummyWeb3(name="avalanche"),
        1: _DummyWeb3(name="ethereum"),
    }

    monkeypatch.setattr("core.block.web3._web3_clients", clients)

    yield clients

    monkeypatch.setattr("core.block.web3._web3_clients", {})


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
