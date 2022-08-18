"""Unit test cases for the ready route."""
from flask.testing import FlaskClient
import pytest
import requests
import requests_mock


@pytest.mark.integration
def test_ready(client: FlaskClient) -> None:
    """Should return OK."""
    # Configure the mock to return a response with an OK status code.
    with requests_mock.Mocker() as m:
        m.get("/fuseki/$/ping", status_code=200)

        response = client.get("/ready")

        assert response.status_code == 200
        assert response.data.decode() == "OK"


@pytest.mark.integration
def test_ready_not_ok_status(client: FlaskClient) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    with requests_mock.Mocker() as m:
        m.get("/fuseki/$/ping", status_code=400)

        response = client.get("/ready")

        assert response.status_code == 500


@pytest.mark.integration
def test_ready_fails(client: FlaskClient) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    with requests_mock.Mocker() as m:
        m.get("/fuseki/$/ping", exc=requests.exceptions.ConnectionError)

        response = client.get("/ready")

        assert response.status_code == 500
