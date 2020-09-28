"""Unit test cases for the catalogs route."""
import json
from os import environ as env
from typing import Any, Dict

from dotenv import load_dotenv
from flask import Flask
import pytest
from pytest_mock import MockerFixture
from rdflib import Graph
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException


load_dotenv()
DATASET = env.get("FUSEKI_DATASET_1", "ds")


@pytest.mark.unit
def test_catalogs(client: Flask, mocker: MockerFixture) -> None:
    """Should return 200 and a turtle serialization."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert", return_value=_mock_queryresult()
    )

    response = client.get("/catalogs")

    assert 200 == response.status_code
    assert "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    assert 0 < len(response.data)
    g = Graph().parse(data=response.data, format="turtle")
    assert 0 < len(g)


@pytest.mark.unit
def test_catalogs_by_id(client: Flask, mocker: MockerFixture) -> None:
    """Should return 200 and a turtle serialization."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert", return_value=_mock_queryresult()
    )

    response = client.get("/catalogs/123")

    assert 200 == response.status_code
    assert "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    assert 0 < len(response.data)
    g = Graph().parse(data=response.data, format="turtle")
    assert 0 < len(g)


@pytest.mark.unit
def test_catalogs_by_id_does_not_exist(client: Flask, mocker: MockerFixture) -> None:
    """Should return 404."""
    # Set up the mock
    mocker.patch("SPARQLWrapper.SPARQLWrapper.queryAndConvert", return_value="")

    response = client.get("/catalogs/123")

    assert 404 == response.status_code
    assert 0 == len(response.data)


@pytest.mark.unit
def test_create_catalog_unauthenticated_fails(
    client: Flask, mocker: MockerFixture
) -> None:
    """Should return 401."""
    # Set up the mocks
    mocker.patch("yaml.safe_load", return_value=_mock_yaml_load())
    mocker.patch("SPARQLWrapper.SPARQLWrapper.query", return_value=True)

    headers = {"Content-Type": "application/json"}
    data = dict(
        identifier="http://dataservice-publisher:8080/catalogs/1234",
        title={"en": "A dataservice catalog"},
        publisher="http://example.com/publisher/1234",
        description={"en": "bladibladibla"},
        apis=[
            {
                "identifier": "http://example.com/dataservice/1",
                "url": "https://raw.githubusercontent.com/"
                "OAI/OpenAPI-Specification/master/examples/v3.0/petstore.yaml",
            }
        ],
    )

    response = client.post("/catalogs", headers=headers, data=json.dumps(data))

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == 'Bearer token_type="JWT"'


@pytest.mark.unit
def test_create_catalog_success(client: Flask, mocker: MockerFixture) -> None:
    """Should return 201 and location header."""
    # Set up the mocks
    mocker.patch("yaml.safe_load", return_value=_mock_yaml_load())
    mocker.patch("SPARQLWrapper.SPARQLWrapper.query", return_value=True)
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")

    headers = {"Content-Type": "application/json", "Authorizaton": "Bearer dummy"}
    data = dict(
        identifier="http://dataservice-publisher:8080/catalogs/1234",
        title={"en": "A dataservice catalog"},
        publisher="http://example.com/publisher/1234",
        description={"en": "bladibladibla"},
        apis=[
            {
                "identifier": "http://example.com/dataservice/1",
                "url": "https://raw.githubusercontent.com/"
                "OAI/OpenAPI-Specification/master/examples/v3.0/petstore.yaml",
            }
        ],
    )

    response = client.post("/catalogs", headers=headers, data=json.dumps(data))

    assert response.status_code == 201
    assert (
        response.headers["Location"]
        == "http://dataservice-publisher:8080/catalogs/1234"
    )


@pytest.mark.unit
def test_create_catalog_failure(client: Flask, mocker: MockerFixture) -> None:
    """Should return status_code 400."""
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")

    response = client.post("/catalogs")

    assert response.status_code == 400


@pytest.mark.unit
def test_catalogs_fails_with_exception(client: Flask, mocker: MockerFixture) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        side_effect=SPARQLWrapperException,
    )

    response = client.get("/catalogs")

    assert response.status_code == 500


@pytest.mark.unit
def test_catalog_by_id_fails_with_exception(
    client: Flask, mocker: MockerFixture
) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        side_effect=SPARQLWrapperException,
    )

    response = client.get("/catalogs/123")

    assert response.status_code == 500


@pytest.mark.unit
def test_create_catalog_fails_with_exception(
    client: Flask, mocker: MockerFixture
) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.query", side_effect=SPARQLWrapperException
    )

    headers = {"Content-Type": "application/json"}
    data = dict(
        identifier="http://dataservice-publisher:8080/catalogs/1234",
        title={"en": "A dataservice catalog"},
        publisher="http://example.com/publisher/1234",
        description={"en": "bladibladibla"},
        apis=[
            {
                "identifier": "http://example.com/dataservice/1",
                "url": "https://raw.githubusercontent.com/"
                "OAI/OpenAPI-Specification/master/examples/v3.0/petstore.yaml",
            }
        ],
    )

    response = client.post("/catalogs", headers=headers, data=json.dumps(data))

    assert response.status_code == 500


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


def _mock_yaml_load() -> Dict[str, Any]:
    """Create a mock openAPI-specification dokument."""
    info = dict(title="Swagger petstore")
    return dict(openapi="3.0.3", info=info)
