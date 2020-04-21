"""Test cases for the catalogs paths."""
import json
from typing import Any

import pytest
from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic
import requests


@pytest.mark.contract
def test_catalogs_with_json(http_service: Any) -> None:
    """Should return status code 200 and a json body."""
    url = f"{http_service}/catalogs"
    headers = {"Accept": "application/json"}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert "application/json" == resp.headers["Content-Type"]
    j = json.loads(resp.text)
    assert 0 < len(j)


@pytest.mark.contract
def test_catalogs_no_accept_returns_turtle(http_service: Any) -> None:
    """Should return status code 200 and a turtle body."""
    url = f"{http_service}/catalogs"
    resp = requests.get(url)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert "text/turtle; charset=utf-8" == resp.headers["Content-Type"]
    g = Graph()
    g.parse(data=resp.text, format="turtle")
    assert 0 < len(g)


@pytest.mark.contract
def test_catalogs_with_text_turtle(http_service: Any) -> None:
    """Should return status code 200 and a turtle body."""
    url = f"{http_service}/catalogs"
    headers = {"Accept": "text/turtle"}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert "text/turtle; charset=utf-8" == resp.headers["Content-Type"]
    g = Graph()
    g.parse(data=resp.text, format="turtle")
    assert 0 < len(g)


@pytest.mark.contract
def test_catalogs_with_application_rdf_xml(http_service: Any) -> None:
    """Should return status code 200 and a rdf+xml body."""
    url = f"{http_service}/catalogs"
    headers = {"Accept": "application/rdf+xml"}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert "application/rdf+xml; charset=utf-8" == resp.headers["Content-Type"]
    g = Graph()
    g.parse(data=resp.text, format="xml")
    assert 0 < len(g)


@pytest.mark.contract
def test_catalogs_with_application_ld_json(http_service: Any) -> None:
    """Should return status code 200 and a ld+json body."""
    url = f"{http_service}/catalogs"
    headers = {"Accept": "application/ld+json"}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert "application/ld+json" == resp.headers["Content-Type"]
    g = Graph()
    g.parse(data=resp.text, format="json-ld")
    assert 0 < len(g)


@pytest.mark.contract
def test_catalog_by_id_with_json(http_service: Any) -> None:
    """Should return status code 200 and a json body."""
    url = f"{http_service}/catalogs/1"
    headers = {"Accept": "application/json"}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert "application/json" == resp.headers["Content-Type"]
    j = json.loads(resp.text)
    assert 0 < len(j)


@pytest.mark.contract
def test_catalog_by_id_no_accept_returns_turtle(http_service: Any) -> None:
    """Should return status code 200 and a turtle body."""
    url = f"{http_service}/catalogs/1"
    resp = requests.get(url)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert "text/turtle; charset=utf-8" == resp.headers["Content-Type"]
    g = Graph()
    g.parse(data=resp.text, format="turtle")
    assert 0 < len(g)


@pytest.mark.contract
def test_catalog_by_id_with_text_turtle(http_service: Any) -> None:
    """Should return status code 200 and a turtle body."""
    url = f"{http_service}/catalogs/1"
    headers = {"Accept": "text/turtle"}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert "text/turtle; charset=utf-8" == resp.headers["Content-Type"]
    g = Graph()
    g.parse(data=resp.text, format="turtle")
    assert 0 < len(g)


@pytest.mark.contract
def test_catalog_by_id_with_application_rdf_xml(http_service: Any) -> None:
    """Should return status code 200 and a rdf+xml body."""
    url = f"{http_service}/catalogs/1"
    headers = {"Accept": "application/rdf+xml"}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert "application/rdf+xml; charset=utf-8" == resp.headers["Content-Type"]
    g = Graph()
    g.parse(data=resp.text, format="xml")
    assert 0 < len(g)


@pytest.mark.contract
def test_catalog_by_id_with_application_ld_json(http_service: Any) -> None:
    """Should return status code 200 and a ld+json body."""
    url = f"{http_service}/catalogs/1"
    headers = {"Accept": "application/ld+json"}
    resp = requests.get(url, headers=headers)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert "application/ld+json" == resp.headers["Content-Type"]
    g = Graph()
    g.parse(data=resp.text, format="json-ld")
    assert 0 < len(g)


@pytest.mark.contract
def test_isomorphic(http_service: Any) -> None:
    """Should return a body with a graph that is isomorphic to correct graph."""
    url = f"{http_service}/catalogs/1"
    headers = {"Accept": "text/turtle"}
    resp = requests.get(url, headers=headers)
    g1 = Graph().parse(data=resp.text, format="turtle")

    g2 = Graph().parse("tests/catalog_1.ttl", format="turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic


# - BAD CASES:
@pytest.mark.contract
def test_not_found_gives_404(http_service: Any) -> None:
    """Should return 404."""
    url = f"{http_service}/catalogs/ID_NOT_IN_DB"
    resp = requests.get(url)
    assert 404 == resp.status_code


# ---------------------------------------------------------------------- #
# Utils for displaying debug information


def _dump_diff(g1: Graph, g2: Graph) -> None:
    in_both, in_first, in_second = graph_diff(g1, g2)
    print("\nin both:")
    _dump_turtle(in_both)
    print("\nin first:")
    _dump_turtle(in_first)
    print("\nin second:")
    _dump_turtle(in_second)


def _dump_turtle(g: Graph) -> None:
    for l in g.serialize(format="turtle").splitlines():
        if l:
            print(l.decode())
