"""Test cases for login."""
from os import environ as env
from typing import Any

from aiohttp import ClientSession
from dotenv import load_dotenv
import pytest

# Get environment
load_dotenv()
ADMIN_USERNAME = env.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = env.get("ADMIN_PASSWORD")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_login_with_valid_credentials(http_service: Any) -> None:
    """Should return status code 200 and an access_token."""
    headers = {"Content-Type": "application/json"}
    data = dict(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)

    url = f"{http_service}/login"
    async with ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            assert 200 == resp.status
            data = await resp.json()

    assert data["access_token"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_login_with_faulty_credentials(http_service: Any) -> None:
    """Should return status code 401 and no access_token."""
    headers = {"Content-Type": "application/json"}
    data = dict(username="WRONGUSERNAME", password="WRONGPASSWORD")  # noqa: S106

    url = f"{http_service}/login"
    async with ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            assert 401 == resp.status
            data = await resp.json()

    assert "access_token" not in data
