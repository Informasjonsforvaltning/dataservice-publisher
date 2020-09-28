"""Unit test cases for the ready route."""
from flask import Flask
import pytest
import requests
import requests_mock


@pytest.mark.unit
def test_ready(client: Flask) -> None:
    """Should return OK."""
    # Configure the mock to return a response with an OK status code.
    with requests_mock.Mocker() as m:
        m.get("/$/ping", status_code=200)

        response = client.get("/ready")

        assert response.status_code == 200
        assert response.data.decode() == "OK"


@pytest.mark.unit
def test_ready_fails(client: Flask) -> None:
    """Should return 400."""
    # Configure the mock to return a response with an OK status code.
    with requests_mock.Mocker() as m:
        m.get("/$/ping", exc=requests.exceptions.ConnectionError)

        response = client.get("/ready")

        assert response.status_code == 500
