import requests
import rdflib
import json

def test_dataservices_with_json():
    "GET request to url returns a 200"
    url = 'http://localhost:8080/dataservices'
    headers = {'Accept': 'application/json'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'application/json' == resp.headers['Content-Type']
    j = json.loads(resp.text)
    assert 0 < len(j)

def test_dataservices_no_accept_returns_turtle():
    "GET request to url returns a 200"
    url = 'http://localhost:8080/dataservices'
    resp = requests.get(url)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'text/turtle; charset=utf-8' == resp.headers['Content-Type']
    g = rdflib.Graph()
    g.parse(data=resp.text, format='turtle')
    assert 0 < len(g)

def test_dataservices_with_text_turtle():
    "GET request to url returns a 200"
    url = 'http://localhost:8080/dataservices'
    headers = {'Accept': 'text/turtle'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'text/turtle; charset=utf-8' == resp.headers['Content-Type']
    g = rdflib.Graph()
    g.parse(data=resp.text, format='turtle')
    assert 0 < len(g)

def test_dataservices_with_application_rdf_xml():
    "GET request to url returns a 200"
    url = 'http://localhost:8080/dataservices'
    headers = {'Accept': 'application/rdf+xml'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'application/rdf+xml; charset=utf-8' == resp.headers['Content-Type']
    g = rdflib.Graph()
    g.parse(data=resp.text, format='xml')
    assert 0 < len(g)

def test_dataservices_with_application_ld_json():
    "GET request to url returns a 200"
    url = 'http://localhost:8080/dataservices'
    headers = {'Accept': 'application/ld+json'}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert 'application/ld+json' == resp.headers['Content-Type']
    g = rdflib.Graph()
    g.parse(data=resp.text, format='json-ld')
    assert 0 < len(g)
