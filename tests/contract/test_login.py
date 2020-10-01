"""Test cases for login."""
from os import environ as env
from typing import Any

from dotenv import load_dotenv
import pytest
import requests

# Get environment
load_dotenv()
ADMIN_USERNAME = env.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = env.get("ADMIN_PASSWORD")


@pytest.mark.contract
def test_login_with_valid_credentials(http_service: Any) -> None:
    """Should return status code 200 and an access_token."""
    headers = {"Content-Type": "application/json"}
    data = dict(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)

    url = f"{http_service}/login"
    response = requests.post(url, json=data, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]


@pytest.mark.contract
def test_login_with_faulty_credentials(http_service: Any) -> None:
    """Should return status code 401 and no access_token."""
    headers = {"Content-Type": "application/json"}
    data = dict(username="WRONGUSERNAME", password="WRONGPASSWORD")  # noqa: S106

    url = f"{http_service}/login"
    response = requests.post(url, json=data, headers=headers)

    assert response.status_code == 401
    data = response.json()
    assert "access_token" not in data
