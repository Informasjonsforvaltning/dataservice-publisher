"""Unit test cases for the ping route."""
from aiohttp.test_utils import TestClient as _TestClient
import pytest


@pytest.mark.integration
async def test_ping(client: _TestClient) -> None:
    """Should return OK."""
    response = await client.get("/ping")

    assert response.status == 200
    data = await response.text()
    assert data == "OK"
