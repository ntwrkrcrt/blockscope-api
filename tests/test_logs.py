from typing import Any

import pytest

from core.exceptions.logs import MaxBlockRangeLimit


@pytest.mark.asyncio
async def test_logs_by_block_period_returns_data(
    async_client, monkeypatch, fake_web3_clients
):
    sample_logs: list[dict[str, Any]] = [
        {
            "address": "0x66357dCaCe80431aee0A7507e2E361B7e2402370",
            "blockHash": "0x1",
            "blockNumber": 10,
            "data": "0x0",
            "logIndex": 0,
            "removed": False,
            "topics": ["0xabc"],
            "transactionHash": "0x2",
            "transactionIndex": 0,
        }
    ]

    async def mock_get_logs(web3, address, from_block, to_block):
        assert web3 is fake_web3_clients[43114]
        assert from_block == 5
        assert to_block == 15
        return sample_logs

    monkeypatch.setattr(
        "api.logs.get_logs_by_block_period",
        mock_get_logs,
    )

    response = await async_client.get("/logs/?from_block=5&to_block=15")

    assert response.status_code == 200
    assert response.json()["logs"] == sample_logs


@pytest.mark.asyncio
async def test_logs_by_block_period_single_block(
    async_client, monkeypatch, fake_web3_clients
):
    sample_logs: list[dict[str, Any]] = [
        {
            "address": "0x66357dCaCe80431aee0A7507e2E361B7e2402370",
            "blockHash": "0xabc",
            "blockNumber": 100,
            "data": "0x123",
            "logIndex": 0,
            "removed": False,
            "topics": ["0xdef"],
            "transactionHash": "0x456",
            "transactionIndex": 0,
        }
    ]

    async def mock_get_logs(web3, address, from_block, to_block):
        assert web3 is fake_web3_clients[43114]
        assert from_block == 100
        assert to_block == 100
        return sample_logs

    monkeypatch.setattr(
        "api.logs.get_logs_by_block_period",
        mock_get_logs,
    )

    response = await async_client.get("/logs/?from_block=100&to_block=100")

    assert response.status_code == 200
    assert len(response.json()["logs"]) == 1


@pytest.mark.asyncio
async def test_logs_by_block_period_without_to_block(
    async_client, monkeypatch, fake_web3_clients
):
    sample_logs: list[dict[str, Any]] = []

    async def mock_get_logs(web3, address, from_block, to_block):
        assert web3 is fake_web3_clients[43114]
        assert from_block == 100
        assert to_block is None
        return sample_logs

    monkeypatch.setattr(
        "api.logs.get_logs_by_block_period",
        mock_get_logs,
    )

    response = await async_client.get("/logs/?from_block=100")

    assert response.status_code == 200
    assert response.json()["logs"] == []


@pytest.mark.asyncio
async def test_logs_by_block_period_invalid_block_range(async_client):
    response = await async_client.get("/logs/?from_block=15&to_block=5")

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_logs_by_block_period_negative_block(async_client):
    response = await async_client.get("/logs/?from_block=-1")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_logs_by_block_period_missing_from_block(async_client):
    response = await async_client.get("/logs/")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_logs_by_block_period_respects_block_limit(async_client, monkeypatch):
    async def mock_get_logs(*_, **__):
        raise MaxBlockRangeLimit("Max block range limit is 3000")

    monkeypatch.setattr(
        "api.logs.get_logs_by_block_period",
        mock_get_logs,
    )

    response = await async_client.get("/logs/?from_block=0&to_block=4000")

    assert response.status_code == 400
    assert "limit" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logs_by_block_period_empty_response(
    async_client, monkeypatch, fake_web3_clients
):
    async def mock_get_logs(web3, address, from_block, to_block):
        assert web3 is fake_web3_clients[43114]
        return []

    monkeypatch.setattr(
        "api.logs.get_logs_by_block_period",
        mock_get_logs,
    )

    response = await async_client.get("/logs/?from_block=1000&to_block=1010")

    assert response.status_code == 200
    assert response.json() == {"logs": []}


@pytest.mark.asyncio
async def test_logs_by_block_period_multiple_logs(
    async_client, monkeypatch, fake_web3_clients
):
    sample_logs: list[dict[str, Any]] = [
        {
            "address": "0x66357dCaCe80431aee0A7507e2E361B7e2402370",
            "blockHash": f"0x{i}",
            "blockNumber": 100 + i,
            "data": f"0x{i}00",
            "logIndex": i,
            "removed": False,
            "topics": [f"0xabc{i}"],
            "transactionHash": f"0xtx{i}",
            "transactionIndex": i,
        }
        for i in range(5)
    ]

    async def mock_get_logs(web3, address, from_block, to_block):
        assert web3 is fake_web3_clients[43114]
        return sample_logs

    monkeypatch.setattr(
        "api.logs.get_logs_by_block_period",
        mock_get_logs,
    )

    response = await async_client.get("/logs/?from_block=100&to_block=105")

    assert response.status_code == 200
    assert len(response.json()["logs"]) == 5


@pytest.mark.asyncio
async def test_logs_by_block_period_caching(
    async_client, monkeypatch, fake_redis, fake_web3_clients
):
    sample_logs: list[dict[str, Any]] = [
        {
            "address": "0x66357dCaCe80431aee0A7507e2E361B7e2402370",
            "blockHash": "0xcached",
            "blockNumber": 50,
            "data": "0x0",
            "logIndex": 0,
            "removed": False,
            "topics": ["0xcache"],
            "transactionHash": "0x123",
            "transactionIndex": 0,
        }
    ]

    call_count = {"count": 0}

    async def mock_get_logs(web3, address, from_block, to_block):
        assert web3 is fake_web3_clients[43114]
        call_count["count"] += 1
        return sample_logs

    monkeypatch.setattr(
        "api.logs.get_logs_by_block_period",
        mock_get_logs,
    )

    response1 = await async_client.get("/logs/?from_block=50&to_block=60")
    assert response1.status_code == 200
    assert call_count["count"] == 1

    response2 = await async_client.get("/logs/?from_block=50&to_block=60")
    assert response2.status_code == 200
    assert call_count["count"] == 1
    assert response1.json() == response2.json()
