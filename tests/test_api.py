from os import environ as env
import requests
from dotenv import load_dotenv
load_dotenv()

HOST_URL = env.get("HOST_URL")


def test_ping():
    "Get request to /ping returns a 200"
    resp = requests.get(HOST_URL + "/ping")
    assert 200 == resp.status_code


def test_ready():
    "Get request to /ready returns a 200"
    resp = requests.get(HOST_URL + "/ready")
    assert 200 == resp.status_code
