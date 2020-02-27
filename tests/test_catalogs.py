import requests
from rdflib import Graph
from rdflib.compare import isomorphic
import json

from os import environ as env
HOST_URL = env.get("HOST_URL")

def test_catalogs_with_json():
    "GET request to url returns a 200"
    url = HOST_URL + "/catalogs"
    headers = {'Accept': 'application/json'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'application/json' == resp.headers['Content-Type']
    j = json.loads(resp.text)
    assert 0 < len(j)

def test_catalogs_no_accept_returns_turtle():
    "GET request to url returns a 200"
    url = HOST_URL + "/catalogs"
    resp = requests.get(url)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'text/turtle; charset=utf-8' == resp.headers['Content-Type']
    g = Graph()
    g.parse(data=resp.text, format='turtle')
    assert 0 < len(g)

def test_catalogs_with_text_turtle():
    "GET request to url returns a 200"
    url = HOST_URL + "/catalogs"
    headers = {'Accept': 'text/turtle'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'text/turtle; charset=utf-8' == resp.headers['Content-Type']
    g = Graph()
    g.parse(data=resp.text, format='turtle')
    assert 0 < len(g)

def test_catalogs_with_application_rdf_xml():
    "GET request to url returns a 200"
    url = HOST_URL + "/catalogs"
    headers = {'Accept': 'application/rdf+xml'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'application/rdf+xml; charset=utf-8' == resp.headers['Content-Type']
    g = Graph()
    g.parse(data=resp.text, format='xml')
    assert 0 < len(g)

def test_catalogs_with_application_ld_json():
    "GET request to url returns a 200"
    url = HOST_URL + "/catalogs"
    headers = {'Accept': 'application/ld+json'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'application/ld+json' == resp.headers['Content-Type']
    g = Graph()
    g.parse(data=resp.text, format='json-ld')
    assert 0 < len(g)

def test_catalog_by_id_with_json():
    "GET request to url returns a 200"
    url = HOST_URL + "/catalogs/1"
    headers = {'Accept': 'application/json'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'application/json' == resp.headers['Content-Type']
    j = json.loads(resp.text)
    assert 0 < len(j)

def test_catalog_by_id_no_accept_returns_turtle():
    "GET request to url returns a 200"
    url = HOST_URL + "/catalogs/1"
    resp = requests.get(url)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'text/turtle; charset=utf-8' == resp.headers['Content-Type']
    g = Graph()
    g.parse(data=resp.text, format='turtle')
    assert 0 < len(g)

def test_catalog_by_id_with_text_turtle():
    "GET request to url returns a 200"
    url = HOST_URL + "/catalogs/1"
    headers = {'Accept': 'text/turtle'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'text/turtle; charset=utf-8' == resp.headers['Content-Type']
    g = Graph()
    g.parse(data=resp.text, format='turtle')
    assert 0 < len(g)

def test_catalog_by_id_with_application_rdf_xml():
    "GET request to url returns a 200"
    url = HOST_URL + "/catalogs/1"
    headers = {'Accept': 'application/rdf+xml'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'application/rdf+xml; charset=utf-8' == resp.headers['Content-Type']
    g = Graph()
    g.parse(data=resp.text, format='xml')
    assert 0 < len(g)

def test_catalog_by_id_with_application_ld_json():
    "GET request to url returns a 200"
    url = HOST_URL + "/catalogs/1"
    headers = {'Accept': 'application/ld+json'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'application/ld+json' == resp.headers['Content-Type']
    g = Graph()
    g.parse(data=resp.text, format='json-ld')
    assert 0 < len(g)

def test_isomorphic():
    "GET request to url returns a 200"
    url = HOST_URL + "/catalogs/1"
    headers = {'Accept': 'text/turtle'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'text/turtle; charset=utf-8' == resp.headers['Content-Type']
    g = Graph()
    g.parse(data=resp.text, format='turtle')
    assert 0 < len(g)
    f = Graph().parse("tests/catalog_1.ttl", format='turtle')
    assert isomorphic(g, f)

def test_not_isomorphic():
    "GET request to url returns a 200"
    url = HOST_URL + "/catalogs/1"
    headers = {'Accept': 'text/turtle'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'text/turtle; charset=utf-8' == resp.headers['Content-Type']
    g = Graph()
    g.parse(data=resp.text, format='turtle')
    assert 0 < len(g)
    f = Graph().parse("tests/catalog_2.ttl", format='turtle')
    assert not isomorphic(g, f)

# BAD CASES:
def test_not_found_gives_404():
    "GET request to url returns a 404"
    url = HOST_URL + "/catalogs/ID_NOT_IN_DB"
    resp = requests.get(url)
    assert 404 == resp.status_code
