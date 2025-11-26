import pytest
from web3.exceptions import Web3RPCError


VALID_ADDRESS = "0x000000000000000000000000000000000000dEaD"
CHECKSUM_ADDRESS = "0x000000000000000000000000000000000000dEaD"


@pytest.mark.asyncio
async def test_balance_by_block_returns_value(
    async_client, monkeypatch, fake_web3_clients
):
    async def mock_get_balance(web3, address, block_number):
        assert web3 is fake_web3_clients[43114]
        assert address == CHECKSUM_ADDRESS
        assert block_number == 100
        return 42

    monkeypatch.setattr(
        "api.block.get_balance_by_block",
        mock_get_balance,
    )

    response = await async_client.get(f"/block/100/balance/{VALID_ADDRESS}/")

    assert response.status_code == 200
    assert response.json() == {"address": CHECKSUM_ADDRESS, "balance": 42}


@pytest.mark.asyncio
async def test_balance_by_block_zero_balance(async_client, monkeypatch):
    async def mock_get_balance(web3, address, block_number):
        return 0

    monkeypatch.setattr(
        "api.block.get_balance_by_block",
        mock_get_balance,
    )

    response = await async_client.get(f"/block/12345/balance/{VALID_ADDRESS}/")

    assert response.status_code == 200
    assert response.json()["balance"] == 0


@pytest.mark.asyncio
async def test_balance_by_block_large_balance(async_client, monkeypatch):
    large_balance = 10**18  # 1 ETH in WEI

    async def mock_get_balance(web3, address, block_number):
        return large_balance

    monkeypatch.setattr(
        "api.block.get_balance_by_block",
        mock_get_balance,
    )

    response = await async_client.get(f"/block/999/balance/{VALID_ADDRESS}/")

    assert response.status_code == 200
    assert response.json()["balance"] == large_balance


@pytest.mark.asyncio
async def test_balance_by_block_invalid_address(async_client):
    response = await async_client.get("/block/1/balance/not-an-address/")

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_balance_by_block_lowercase_address(
    async_client, monkeypatch, fake_web3_clients
):
    lowercase_address = "0x000000000000000000000000000000000000dead"

    async def mock_get_balance(web3, address, block_number):
        assert web3 is fake_web3_clients[43114]
        assert address == CHECKSUM_ADDRESS
        return 123

    monkeypatch.setattr(
        "api.block.get_balance_by_block",
        mock_get_balance,
    )

    response = await async_client.get(f"/block/100/balance/{lowercase_address}/")

    assert response.status_code == 200
    assert response.json()["address"] == CHECKSUM_ADDRESS


@pytest.mark.asyncio
async def test_balance_by_block_with_chain_id_avalanche(
    async_client, monkeypatch, fake_web3_clients
):
    async def mock_get_balance(web3, address, block_number):
        assert web3 is fake_web3_clients[43114]
        return 999

    monkeypatch.setattr(
        "api.block.get_balance_by_block",
        mock_get_balance,
    )

    response = await async_client.get(
        f"/block/100/balance/{VALID_ADDRESS}/?chain_id=43114"
    )

    assert response.status_code == 200
    assert response.json()["balance"] == 999


@pytest.mark.asyncio
async def test_balance_by_block_with_chain_id_ethereum(
    async_client, monkeypatch, fake_web3_clients
):
    async def mock_get_balance(web3, address, block_number):
        assert web3 is fake_web3_clients[1]
        return 777

    monkeypatch.setattr(
        "api.block.get_balance_by_block",
        mock_get_balance,
    )

    response = await async_client.get(f"/block/200/balance/{VALID_ADDRESS}/?chain_id=1")

    assert response.status_code == 200
    assert response.json()["balance"] == 777


@pytest.mark.asyncio
async def test_balance_by_block_unsupported_chain_id(async_client):
    response = await async_client.get(
        f"/block/100/balance/{VALID_ADDRESS}/?chain_id=99999"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_balance_by_block_rpc_error(async_client, monkeypatch):
    async def mock_get_balance(web3, address, block_number):
        raise Web3RPCError("RPC connection failed")

    monkeypatch.setattr(
        "api.block.get_balance_by_block",
        mock_get_balance,
    )

    response = await async_client.get(f"/block/100/balance/{VALID_ADDRESS}/")

    assert response.status_code == 502
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_balance_by_block_caching(async_client, monkeypatch, fake_redis):
    call_count = {"count": 0}

    async def mock_get_balance(web3, address, block_number):
        call_count["count"] += 1
        return 555

    monkeypatch.setattr(
        "api.block.get_balance_by_block",
        mock_get_balance,
    )

    # Первый запрос
    response1 = await async_client.get(f"/block/333/balance/{VALID_ADDRESS}/")
    assert response1.status_code == 200
    assert call_count["count"] == 1

    # Второй идентичный запрос - должен взять из кэша
    response2 = await async_client.get(f"/block/333/balance/{VALID_ADDRESS}/")
    assert response2.status_code == 200
    assert call_count["count"] == 1
    assert response1.json() == response2.json()


@pytest.mark.asyncio
async def test_balance_by_block_different_blocks_no_cache(
    async_client, monkeypatch, fake_redis
):
    call_count = {"count": 0}

    async def mock_get_balance(web3, address, block_number):
        call_count["count"] += 1
        return block_number * 100

    monkeypatch.setattr(
        "api.block.get_balance_by_block",
        mock_get_balance,
    )

    response1 = await async_client.get(f"/block/100/balance/{VALID_ADDRESS}/")
    assert response1.status_code == 200
    assert call_count["count"] == 1

    response2 = await async_client.get(f"/block/200/balance/{VALID_ADDRESS}/")
    assert response2.status_code == 200
    assert call_count["count"] == 2
    assert response1.json()["balance"] != response2.json()["balance"]
