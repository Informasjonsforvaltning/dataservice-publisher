"""Unit test cases for the login route."""
import json
from os import environ as env

from dotenv import load_dotenv
from flask import Flask
import pytest

# Get environment
load_dotenv()
ADMIN_USERNAME = env.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = env.get("ADMIN_PASSWORD")


@pytest.mark.unit
def test_login_succeds(client: Flask) -> None:
    """Should return 200 and an access_token."""
    headers = {"Content-Type": "application/json"}
    data = dict(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)

    response = client.post("/login", headers=headers, data=json.dumps(data))

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["access_token"]


@pytest.mark.unit
def test_login_without_username_password_fails(client: Flask) -> None:
    """Should return 401 an WWW-Authenticate header."""
    response = client.post("/login")

    assert response.status_code == 401


@pytest.mark.unit
def test_login_wrong_username_password_fails(client: Flask) -> None:
    """Should return 401 an WWW-Authenticate header."""
    headers = {"Content-Type": "application/json"}
    data = dict(username="WRONGUSERNAME", password="WRONGPASSWORD")  # noqa: S106

    response = client.post("/login", headers=headers, data=json.dumps(data))

    assert response.status_code == 401
