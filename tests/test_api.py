"""Test cases for ping and ready."""
from typing import Any

import pytest
import requests


@pytest.mark.contract
def test_ping(http_service: Any) -> None:
    """Should return status code 200."""
    url = f"{http_service}/ping"
    resp = requests.get(url)
    assert 200 == resp.status_code


@pytest.mark.contract
def test_ready(http_service: Any) -> None:
    """Should return status code 200."""
    url = f"{http_service}/ready"
    resp = requests.get(url)
    assert 200 == resp.status_code
