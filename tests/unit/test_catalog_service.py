"""Unit test cases for the catalog module."""
import json
from typing import Any, Dict

import pytest
from pytest_mock import MockFixture
from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic
import yaml

from dataservice_publisher.service.catalog_service import (
    create_catalog,
    fetch_catalogs,
    get_catalog_by_id,
)


@pytest.mark.unit
def test_create_catalog(mocker: MockFixture) -> None:
    """Should return True when sucessful."""
    # Set up the mocks
    mocker.patch("yaml.safe_load", return_value=_mock_yaml_load())
    mocker.patch("SPARQLWrapper.SPARQLWrapper.query", return_value=True)

    with open("./tests/files/catalog_1.json") as json_file:
        catalog = json.load(json_file)

    _result = create_catalog(catalog)

    assert isinstance(_result, Graph), "result is not a Graph"
    g2 = Graph().parse("tests/files/catalog_1.ttl", format="turtle")

    _isomorphic = isomorphic(_result, g2)
    _dump_turtle(_result)
    _dump_turtle(g2)
    assert len(_result) == len(g2), "Graphs are of unequal length"
    if not _isomorphic:
        _dump_diff(_result, g2)
        pass
    assert _isomorphic, "Graphs are not isomorphic"


@pytest.mark.unit
def test_fetch_catalogs(mocker: MockFixture) -> None:
    """Should return a Graph."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert", return_value=_mock_queryresult()
    )

    g = fetch_catalogs()
    assert isinstance(g, Graph)
    assert len(g) > 0


@pytest.mark.unit
def test_get_catalog_by_id(mocker: MockFixture) -> None:
    """Should return a specific graph."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert", return_value=_mock_queryresult()
    )
    g = get_catalog_by_id("1")
    assert isinstance(g, Graph)
    assert len(g) > 0


@pytest.mark.unit
def test_get_catalog_by_id_failure(mocker: MockFixture) -> None:
    """Should return an empty graph."""
    # Set up the mock
    mocker.patch("SPARQLWrapper.SPARQLWrapper.queryAndConvert", return_value="")
    g = get_catalog_by_id("non-existent")
    assert isinstance(g, Graph)
    assert len(g) == 0


# --
def _mock_yaml_load() -> Dict[str, Any]:
    """Create a mock openAPI-specification dokument."""
    with open("./tests/files/petstore.yaml", "r") as file:
        _yaml = yaml.safe_load(file)

    return _yaml


def _mock_queryresult() -> str:
    """Create a mock catalog collection response."""
    response = """
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
    @prefix xml: <http://www.w3.org/XML/1998/namespace> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    <http://localhost:8000/catalogs/1> a dcat:Catalog .
    """
    return response


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
