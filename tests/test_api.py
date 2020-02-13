import requests
import rdflib

def test_catalogs_with_text_turtle():
    "GET request to url returns a 200"
    url = 'http://localhost:8080/catalogs'
    headers = {'Accept': 'text/turtle'}
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 200
    assert len(resp.content) > 0

def test_catalogs_with_application_rdf_xml():
    "GET request to url returns a 200"
    url = 'http://localhost:8080/catalogs'
    headers = {'Accept': 'application/rdf+xml'}
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 200
    assert len(resp.content) > 0
    assert resp.headers == 'application/rdf+xml'

def test_catalogs_with_application_ld_json():
    "GET request to url returns a 200"
    url = 'http://localhost:8080/catalogs'
    headers = {'Accept': 'application/ld+json'}
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 200
    assert len(resp.content) > 0
    assert resp.headers == 'application/ld+json'

def test_that_catalog_parses_well():
    url = 'http://localhost:8080/catalogs'
    g=rdflib.Graph()
    assert g.parse(url, format='turtle')
    assert len(g) > 0

def test_ping():
    "Get request to /ping returns a 200"
    url = 'http://localhost:8080/ping'
    resp = requests.get(url)
    assert resp.status_code == 200

def test_ready():
    "Get request to /ready returns a 200"
    url = 'http://localhost:8080/ready'
    resp = requests.get(url)
    assert resp.status_code == 200
