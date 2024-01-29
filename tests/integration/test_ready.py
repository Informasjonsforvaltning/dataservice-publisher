"""Integration test cases for the ready route."""

from typing import Any

from aiohttp import ClientConnectionError
from aiohttp.test_utils import TestClient as _TestClient
from aioresponses import aioresponses
import pytest


@pytest.fixture
def mock_aioresponse() -> Any:
    """Set up aioresponses as fixture."""
    with aioresponses(passthrough=["http://127.0.0.1"]) as m:
        yield m


@pytest.mark.integration
async def test_ready(client: _TestClient, mock_aioresponse: Any) -> None:
    """Should return OK."""
    # Configure the mock to return a response with an OK status code.
    mock_aioresponse.get("http://fuseki:8080/fuseki/$/ping", status=200)

    response = await client.get("/ready")

    assert response.status == 200
    data = await response.text()
    assert data == "OK"


@pytest.mark.integration
async def test_ready_not_ok_status(client: _TestClient, mock_aioresponse: Any) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mock_aioresponse.get("http://localhost:8080/fuseki/$/ping", status=400)

    response = await client.get("/ready")

    assert response.status == 500


@pytest.mark.integration
async def test_ready_raises_client_connection_error(
    client: _TestClient, mock_aioresponse: Any
) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mock_aioresponse.get(
        "http://localhost:8080/fuseki/$/ping",
        exception=ClientConnectionError(),
    )

    response = await client.get("/ready")

    assert response.status == 500
