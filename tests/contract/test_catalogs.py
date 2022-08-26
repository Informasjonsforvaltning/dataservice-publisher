"""Test cases for the catalogs paths."""
import json
from os import environ as env
from typing import Any

from dotenv import load_dotenv
import pytest
from rdflib import DCAT, Graph, RDF
from rdflib.compare import graph_diff, isomorphic
import requests

# Get environment
load_dotenv()
ADMIN_USERNAME = env.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = env.get("ADMIN_PASSWORD")


@pytest.mark.contract
@pytest.fixture(scope="session")
def access_token(http_service: Any) -> Any:
    """Ensure that HTTP service is up and responsive."""
    """Should return status code 200 and an access_token."""

    headers = {"Content-Type": "application/json"}
    data = dict(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)

    url = f"{http_service}/login"
    response = requests.post(url, json=data, headers=headers)

    data = response.json()
    return data["access_token"]


@pytest.mark.contract
def test_create_catalog_unauthenticated(http_service: Any) -> None:
    """Should return status code 401."""
    url = f"{http_service}/catalogs"
    with open("./tests/files/catalog_1.json") as json_file:
        data = json.load(json_file)
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=data, headers=headers)
    assert 401 == resp.status_code
    assert resp.headers["WWW-Authenticate"]


@pytest.mark.contract
def test_create_catalog(http_service: Any, access_token: str) -> None:
    """Should return status code 201 and a valid location header."""
    url = f"{http_service}/catalogs"
    with open("./tests/files/catalog_1.json") as json_file:
        data = json.load(json_file)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    resp = requests.post(url, json=data, headers=headers)
    assert 200 == resp.status_code, "error creating catalog"
    assert 0 < len(resp.content)
    assert "text/turtle; charset=utf-8" == resp.headers["Content-Type"]
    g = Graph()
    g.parse(data=resp.text, format="turtle")
    assert 0 < len(g)

    # Check that the catalog is in the catalogs graph, and extract the catalog's URI:
    catalog_url: str = g.value(None, RDF.type, DCAT.Catalog, any=False)
    assert catalog_url

    # Get the catalog's graph and check that it is isomorphic with the one we created:
    resp = requests.get(catalog_url)
    assert 200 == resp.status_code, f"new catalog not found: {catalog_url}"
    assert 0 < len(resp.text)
    g1 = Graph()
    assert g1.parse(data=resp.text, format="turtle")
    assert 0 < len(g1)

    g2 = Graph().parse("tests/files/catalog_1.ttl", format="turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "graphs are not isomorphic"


@pytest.mark.contract
def test_get_catalogs(http_service: Any) -> None:
    """Should return status code 200 and many catalogs in a turtle body."""
    url = f"{http_service}/catalogs"
    resp = requests.get(url)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert "text/turtle; charset=utf-8" == resp.headers["Content-Type"]
    g = Graph()
    g.parse(data=resp.text, format="turtle")
    assert 0 < len(g)


@pytest.mark.contract
def test_get_catalog_by_id(http_service: Any) -> None:
    """Should return status code 200 and single catalog in a turtle body."""
    url = f"{http_service}/catalogs/1"
    resp = requests.get(url)
    assert 200 == resp.status_code
    assert 0 < len(resp.content)
    assert "text/turtle; charset=utf-8" == resp.headers["Content-Type"]
    g = Graph()
    g.parse(data=resp.text, format="turtle")
    assert 0 < len(g)


@pytest.mark.contract
def test_delete_catalog_unauthenticated(http_service: Any) -> None:
    """Should return status code 401."""
    url = f"{http_service}/catalogs/1"

    resp = requests.delete(url)
    assert 401 == resp.status_code
    assert resp.headers["WWW-Authenticate"]


@pytest.mark.contract
def test_delete_catalog_by_id(http_service: Any, access_token: str) -> None:
    """Should return status code 204."""
    url = f"{http_service}/catalogs/1"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    resp = requests.delete(url, headers=headers)
    assert 204 == resp.status_code
    assert 0 == len(resp.content)


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
    for _l in g.serialize(format="turtle").splitlines():
        if _l:
            print(_l)
