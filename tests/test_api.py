import requests
import rdflib
import json

def test_catalogs_with_json():
    "GET request to url returns a 200"
    url = 'http://localhost:8080/catalogs'
    headers = {'Accept': 'application/json'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'application/json' == resp.headers['Content-Type']
    print('resp.text >', resp.text, '<')
    j = json.loads(resp.text)
    assert 0 < len(j)

def test_catalogs_no_accept_returns_turtle():
    "GET request to url returns a 200"
    url = 'http://localhost:8080/catalogs'
    resp = requests.get(url)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'text/turtle; charset=utf-8' == resp.headers['Content-Type']
    g = rdflib.Graph()
    g.parse(data=resp.text, format='turtle')
    assert 0 < len(g)

def test_catalogs_with_text_turtle():
    "GET request to url returns a 200"
    url = 'http://localhost:8080/catalogs'
    headers = {'Accept': 'text/turtle'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'text/turtle; charset=utf-8' == resp.headers['Content-Type']
    g = rdflib.Graph()
    g.parse(data=resp.text, format='turtle')
    assert 0 < len(g)

def test_catalogs_with_application_rdf_xml():
    "GET request to url returns a 200"
    url = 'http://localhost:8080/catalogs'
    headers = {'Accept': 'application/rdf+xml'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'application/rdf+xml; charset=utf-8' == resp.headers['Content-Type']
    g = rdflib.Graph()
    g.parse(data=resp.text, format='xml')
    assert 0 < len(g)

def test_catalogs_with_application_ld_json():
    "GET request to url returns a 200"
    url = 'http://localhost:8080/catalogs'
    headers = {'Accept': 'application/ld+json'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'application/ld+json' == resp.headers['Content-Type']
    g = rdflib.Graph()
    g.parse(data=resp.text, format='json-ld')
    assert 0 < len(g)

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
