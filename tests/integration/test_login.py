"""Unit test cases for the login route."""
import json
from os import environ as env

from aiohttp.test_utils import TestClient as _TestClient
from dotenv import load_dotenv
import pytest
from pytest_mock import MockFixture

# Get environment
load_dotenv()
ADMIN_USERNAME = env.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = env.get("ADMIN_PASSWORD")


@pytest.mark.integration
async def test_login_succeeds(client: _TestClient) -> None:
    """Should return 200 and an access_token."""
    headers = {"Content-Type": "application/json"}
    data = dict(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)

    response = await client.post("/login", headers=headers, data=json.dumps(data))

    assert response.status == 200
    assert response.headers["Content-Type"] == "application/json"
    data = await response.json()
    assert data["access_token"]


@pytest.mark.integration
async def test_login_no_username(client: _TestClient) -> None:
    """Should return 401 an WWW-Authenticate header."""
    headers = {"Content-Type": "application/json"}
    data = dict(password=ADMIN_PASSWORD)

    response = await client.post("/login", headers=headers, data=json.dumps(data))

    assert response.status == 401


@pytest.mark.integration
async def test_login_no_password(client: _TestClient) -> None:
    """Should return 401 an WWW-Authenticate header."""
    headers = {"Content-Type": "application/json"}
    data = dict(username=ADMIN_USERNAME)

    response = await client.post("/login", headers=headers, data=json.dumps(data))

    assert response.status == 401


@pytest.mark.integration
async def test_login_without_username_password(client: _TestClient) -> None:
    """Should return 401 an WWW-Authenticate header."""
    headers = {"Content-Type": "application/json"}
    response = await client.post("/login", headers=headers)

    assert response.status == 401


@pytest.mark.integration
async def test_login_without_content_type_header(client: _TestClient) -> None:
    """Should return 415."""
    data = dict(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
    response = await client.post("/login", data=json.dumps(data))

    assert response.status == 415


@pytest.mark.integration
async def test_login_unsupported_media_type(client: _TestClient) -> None:
    """Should return 415."""
    headers = {"Content-Type": "unsupported/media-type"}
    data = dict(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)

    response = await client.post("/login", headers=headers, data=json.dumps(data))

    assert response.status == 415


@pytest.mark.integration
async def test_login_wrong_username_password_fails(client: _TestClient) -> None:
    """Should return 401 an WWW-Authenticate header."""
    headers = {"Content-Type": "application/json"}
    data = dict(username="WRONGUSERNAME", password="WRONGPASSWORD")  # noqa: S106

    response = await client.post("/login", headers=headers, data=json.dumps(data))

    assert response.status == 401


@pytest.mark.integration
async def test_login_no_shared_secret(client: _TestClient, mocker: MockFixture) -> None:
    """Should return 500 Internal server error."""
    mocker.patch("dataservice_publisher.resources.login.SHARED_SECRET", new=None)

    headers = {"Content-Type": "application/json"}
    data = dict(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)

    response = await client.post("/login", headers=headers, data=json.dumps(data))

    assert response.status == 500
