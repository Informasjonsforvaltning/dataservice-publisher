import requests
import rdflib
import json


from dotenv import load_dotenv
load_dotenv()

from os import environ as env
HOST_URL = env.get("HOST_URL") + ":" + env.get("HOST_PORT")

def test_ping():
    "Get request to /ping returns a 200"
    resp = requests.get(HOST_URL + "/ping")
    assert 200 == resp.status_code

def test_ready():
    "Get request to /ready returns a 200"
    resp = requests.get(HOST_URL + "/ready")
    assert 200 == resp.status_code
