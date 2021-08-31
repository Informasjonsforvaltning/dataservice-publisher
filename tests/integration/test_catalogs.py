"""Unit test cases for the catalogs route."""
import json
from os import environ as env
from typing import Any, Dict

from dotenv import load_dotenv
from flask import Flask
import pytest
from pytest_mock import MockFixture
from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException
import yaml

load_dotenv()
DATASET = env.get("FUSEKI_DATASET_1", "ds")


@pytest.mark.integration
def test_catalogs(client: Flask, mocker: MockFixture) -> None:
    """Should return 200 and a turtle serialization."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value=_mock_query_and_convert_result(),
    )

    response = client.get("/catalogs")

    assert 200 == response.status_code
    assert "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    assert 0 < len(response.data)
    g = Graph().parse(data=response.data, format="turtle")
    assert 0 < len(g)


@pytest.mark.integration
def test_catalogs_by_id(client: Flask, mocker: MockFixture) -> None:
    """Should return 200 and a turtle serialization."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value=_mock_query_and_convert_result(),
    )

    response = client.get("/catalogs/123")

    assert 200 == response.status_code
    assert "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    assert 0 < len(response.data)
    g = Graph().parse(data=response.data, format="turtle")
    assert 0 < len(g)


@pytest.mark.integration
def test_delete_catalog(client: Flask, mocker: MockFixture) -> None:
    """Should return 204 No Content."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value=_mock_query_and_convert_result(),
    )
    mocker.patch("SPARQLWrapper.SPARQLWrapper.query", return_value=_mock_query_result())

    response = client.delete("/catalogs/123")

    assert 204 == response.status_code


@pytest.mark.integration
def test_delete_catalog_does_not_exist(client: Flask, mocker: MockFixture) -> None:
    """Should return 204 No Content."""
    # Set up the mock
    mocker.patch("SPARQLWrapper.SPARQLWrapper.queryAndConvert", return_value="")
    mocker.patch("SPARQLWrapper.SPARQLWrapper.query", return_value=_mock_query_result())

    response = client.delete("/catalogs/does_not_exist")

    assert 404 == response.status_code


@pytest.mark.integration
def test_delete_catalog_unsuccessful_result(client: Flask, mocker: MockFixture) -> None:
    """Should return 400 Bad Request."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value=_mock_query_and_convert_result(),
    )
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.query",
        return_value=_mock_unsuccesfull_query_result(),
    )

    response = client.delete("/catalogs/123")

    assert 400 == response.status_code


@pytest.mark.integration
def test_delete_catalog_fails_with_exception(
    client: Flask, mocker: MockFixture
) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value=_mock_query_and_convert_result(),
    )
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.query",
        side_effect=SPARQLWrapperException,
    )

    response = client.delete("/catalogs/123")

    assert response.status_code == 500


@pytest.mark.integration
def test_get_catalog_by_id_does_not_exist(client: Flask, mocker: MockFixture) -> None:
    """Should return 404."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value="",
    )

    response = client.get("/catalogs/123")

    assert 404 == response.status_code
    assert 0 == len(response.data)


@pytest.mark.integration
def test_create_catalog_unauthenticated_fails(
    client: Flask, mocker: MockFixture
) -> None:
    """Should return 401."""
    # Set up the mocks
    mocker.patch("yaml.safe_load", return_value=_mock_yaml_load())
    mocker.patch("SPARQLWrapper.SPARQLWrapper.query", return_value=True)

    headers = {"Content-Type": "application/json"}
    with open("./tests/files/catalog_1.json") as json_file:
        data = json.load(json_file)

    response = client.post("/catalogs", headers=headers, data=json.dumps(data))

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == 'Bearer token_type="JWT"'


@pytest.mark.integration
def test_create_catalog_success(client: Flask, mocker: MockFixture) -> None:
    """Should return 201 and location header."""
    # Set up the mocks
    mocker.patch("yaml.safe_load", return_value=_mock_yaml_load())
    mocker.patch("SPARQLWrapper.SPARQLWrapper.query", return_value=True)
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value=_mock_full_query_result(),
    )

    headers = {"Content-Type": "application/json", "Authorizaton": "Bearer dummy"}
    with open("./tests/files/catalog_1.json") as json_file:
        data = json.load(json_file)

    response = client.post("/catalogs", headers=headers, data=json.dumps(data))

    assert response.status_code == 200
    assert "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    assert 0 < len(response.data)
    g1 = Graph().parse(data=response.data, format="turtle")
    assert 0 < len(g1)

    # Verify that all of the input is created:
    response = client.get("/catalogs/1234")

    assert 200 == response.status_code
    assert "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    assert 0 < len(response.data)
    g2 = Graph().parse(data=response.data, format="turtle")
    assert 0 < len(g2)

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic


@pytest.mark.integration
def test_create_catalog_failure(client: Flask, mocker: MockFixture) -> None:
    """Should return status_code 400."""
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")

    response = client.post("/catalogs")

    assert response.status_code == 400


@pytest.mark.integration
def test_create_catalog_key_error_failure(client: Flask, mocker: MockFixture) -> None:
    """Should return status_code 400 and message."""
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")

    headers = {"Content-Type": "application/json"}
    data = dict(identifier="http://dataservice-publisher:8080/catalogs/1")

    response = client.post("/catalogs", headers=headers, data=json.dumps(data))

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["msg"] == "KeyError when processing request body"


@pytest.mark.integration
def test_create_catalog_type_error_failure(client: Flask, mocker: MockFixture) -> None:
    """Should return status_code 400 and message."""
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")

    headers = {"Content-Type": "application/json"}
    # Point here is that apis array should have dicts, not strings as members:
    data = dict(
        identifier="http://dataservice-publisher:8080/catalogs/1",
        title={"en": "Title with language tag"},
        description={"en": "description with language tag"},
        publisher="http://example.com/publishers/1",
        apis=["http://api.url.com"],
    )

    response = client.post("/catalogs", headers=headers, data=json.dumps(data))

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["msg"] == "TypeError when processing request body"


@pytest.mark.integration
def test_get_catalog_fails_with_exception(client: Flask, mocker: MockFixture) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        side_effect=SPARQLWrapperException,
    )

    response = client.get("/catalogs")

    assert response.status_code == 500


@pytest.mark.integration
def test_catalog_by_id_fails_with_exception(client: Flask, mocker: MockFixture) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        side_effect=SPARQLWrapperException,
    )

    response = client.get("/catalogs/123")

    assert response.status_code == 500


@pytest.mark.integration
def test_create_catalog_fails_with_exception(
    client: Flask, mocker: MockFixture
) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.query", side_effect=SPARQLWrapperException
    )

    headers = {"Content-Type": "application/json"}
    with open("./tests/files/catalog_1.json") as json_file:
        data = json.load(json_file)

    response = client.post("/catalogs", headers=headers, data=json.dumps(data))

    assert response.status_code == 500


def _mock_query_and_convert_result() -> str:
    """Create a mock catalog collection response."""
    result = """
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
    @prefix xml: <http://www.w3.org/XML/1998/namespace> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    <http://dataservice-publisher:8080/catalogs/1> a dcat:Catalog .
    """
    return result


def _mock_query_result() -> Any:
    """Create a mock query result."""
    response = type("response", (object,), {"status": 200})
    result = type("result", (object,), {"response": response})
    return result


def _mock_unsuccesfull_query_result() -> Any:
    """Create a mock query result."""
    response = type("response", (object,), {"status": 500})
    result = type("result", (object,), {"response": response})
    return result


def _mock_full_query_result() -> str:
    """Create a mock catalog collection response."""
    with open("./tests/files/catalog_1.ttl", "r") as file:
        data = file.read()
    return data


def _mock_yaml_load() -> Dict[str, Any]:
    """Create a mock openAPI-specification dokument."""
    with open("./tests/files/petstore.yaml", "r") as file:
        _yaml = yaml.safe_load(file)

    return _yaml


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
