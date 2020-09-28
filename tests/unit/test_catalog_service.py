"""Unit test cases for the catalog module."""
from typing import Any, Dict, List

import pytest
from pytest_mock import MockerFixture
from rdflib import Graph

from dataservice_publisher.service.catalog_service import (
    create_catalog,
    fetch_catalogs,
    get_catalog_by_id,
)


@pytest.mark.unit
def test_create_catalog(mocker: MockerFixture) -> None:
    """Should return True when sucessful."""
    # Set up the mocks
    mocker.patch("yaml.safe_load", return_value=_mock_yaml_load())
    mocker.patch("SPARQLWrapper.SPARQLWrapper.query", return_value=True)

    catalog: Dict[str, Any] = {}
    catalog["title"] = {"en": "Test title"}
    catalog["publisher"] = "http://example.com/publishers/1"
    catalog["identifier"] = "http://dataservice-publisher:8080/catalogs/1"
    catalog["description"] = {"en": "Test description"}
    apis: List[dict] = []
    api = {
        "identifier": "http://example.com/dataservices/1",
        "url": "https://raw.githubusercontent.com/"
        "OAI/OpenAPI-Specification/master/examples/v3.0/petstore.yaml",
    }
    apis.append(api)
    catalog["apis"] = apis

    _result = create_catalog(catalog)

    assert isinstance(_result, str)
    assert _result


@pytest.mark.unit
def test_fetch_catalogs(mocker: MockerFixture) -> None:
    """Should return a Graph."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert", return_value=_mock_queryresult()
    )

    g = fetch_catalogs()
    assert isinstance(g, Graph)
    assert len(g) > 0


@pytest.mark.unit
def test_get_catalog_by_id(mocker: MockerFixture) -> None:
    """Should return a specific graph."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert", return_value=_mock_queryresult()
    )
    g = get_catalog_by_id("1")
    assert isinstance(g, Graph)
    assert len(g) > 0


@pytest.mark.unit
def test_get_catalog_by_id_failure(mocker: MockerFixture) -> None:
    """Should return an empty graph."""
    # Set up the mock
    mocker.patch("SPARQLWrapper.SPARQLWrapper.queryAndConvert", return_value="")
    g = get_catalog_by_id("non-existent")
    assert isinstance(g, Graph)
    assert len(g) == 0


# --
def _mock_yaml_load() -> Dict[str, Any]:
    """Create a mock openAPI-specification dokument."""
    info = dict(title="Swagger petstore")
    return dict(openapi="3.0.3", info=info)


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

    <http://dataservice-publisher:8080/catalogs/1> a dcat:Catalog .
    """
    return response
