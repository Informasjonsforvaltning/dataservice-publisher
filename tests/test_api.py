import requests
import rdflib
import json

def test_ping():
    "Get request to /ping returns a 200"
    url = 'http://localhost:8080/ping'
    resp = requests.get(url)
    assert 200 == resp.status_code

def test_ready():
    "Get request to /ready returns a 200"
    url = 'http://localhost:8080/ready'
    resp = requests.get(url)
    assert 200 == resp.status_code
