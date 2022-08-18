"""Unit test cases for the ping route."""
from flask.testing import FlaskClient
import pytest


@pytest.mark.integration
def test_ping(client: FlaskClient) -> None:
    """Should return OK."""
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.data.decode() == "OK"
