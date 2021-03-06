"""Conftest module."""
import os
from os import environ as env
import time
from typing import Any, Generator

from dotenv import load_dotenv
from flask import Flask
from flask.testing import FlaskClient
import pytest
import requests
from requests.exceptions import ConnectionError

from dataservice_publisher import create_app

load_dotenv()
HOST_PORT = int(env.get("HOST_PORT", "8080"))
FUSEKI_HOST_URL = env.get("FUSEKI_HOST_URL", "http://fuseki:3030")


def is_responsive(url: Any) -> Any:
    """Return true if respons from service is 200."""
    url = f"{url}/ready"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            time.sleep(2)  # sleep extra 2 sec
            return True
    except ConnectionError:
        return False


@pytest.mark.contract
@pytest.fixture(scope="session")
def http_service(docker_ip: Any, docker_services: Any) -> Any:
    """Ensure that HTTP service is up and responsive."""
    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("dataservice-publisher", HOST_PORT)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url


@pytest.mark.contract
@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig: Any) -> Any:
    """Override default location of docker-compose.yml file."""
    return os.path.join(str(pytestconfig.rootdir), "./", "docker-compose.yml")


@pytest.mark.unit
@pytest.fixture
def app() -> Generator:
    """Returns a Flask app for unit testing."""
    app = create_app({"TESTING": True})

    yield app


@pytest.mark.unit
@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Returns a client for unit testing."""
    return app.test_client()
