"""Test cases for ping and ready."""

from typing import Any

from aiohttp import ClientSession
import pytest


@pytest.mark.contract
@pytest.mark.asyncio
async def test_ping(http_service: Any) -> None:
    """Should return status code 200."""
    url = f"{http_service}/ping"
    async with ClientSession() as session:
        async with session.get(url) as resp:
            assert 200 == resp.status


@pytest.mark.contract
@pytest.mark.asyncio
async def test_ready(http_service: Any) -> None:
    """Should return status code 200."""
    url = f"{http_service}/ready"

    async with ClientSession() as session:
        async with session.get(url) as resp:
            assert 200 == resp.status
