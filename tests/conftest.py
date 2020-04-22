"""Conftest module."""
from typing import Any

import pytest
import requests
from requests.exceptions import ConnectionError


def is_responsive(url: Any) -> Any:
    """Return true if respons from service is 200."""
    try:
        response = requests.get(url + "/ready")
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


@pytest.mark.contract
@pytest.fixture(scope="session")
def http_service(docker_ip: Any, docker_services: Any) -> Any:
    """Ensure that HTTP service is up and responsive."""
    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("dataservice-publisher", 8080)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url
