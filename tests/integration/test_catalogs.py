"""Unit test cases for the catalogs route."""
import json
from os import environ as env
from typing import Any, Dict

from aiohttp import hdrs
from aiohttp.test_utils import TestClient as _TestClient
from dotenv import load_dotenv
from multidict import MultiDict
import pytest
from pytest_mock import MockFixture
from rdflib import Graph
from rdflib.compare import graph_diff, isomorphic
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException
import yaml

load_dotenv()
DATASET = env.get("FUSEKI_DATASET_1", "ds")


@pytest.mark.integration
async def test_catalogs(client: _TestClient, mocker: MockFixture) -> None:
    """Should return 200 and a turtle serialization."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value=_mock_query_and_convert_result(),
    )

    response = await client.get("/catalogs")

    assert 200 == response.status
    assert "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    data = await response.text()
    assert 0 < len(data)
    g = Graph().parse(data=data, format="turtle")
    assert 0 < len(g)


@pytest.mark.integration
async def test_catalogs_serializers(client: _TestClient, mocker: MockFixture) -> None:
    """Should return 200 and a turtle serialization."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value=_mock_query_and_convert_result(),
    )
    serializers = [
        "text/turtle",
        "application/n-triples",
        "application/ld+json",
        "application/rdf+xml",
    ]
    for serializer in serializers:
        headers = MultiDict([(hdrs.ACCEPT, serializer)])
        response = await client.get("/catalogs", headers=headers)
        assert 200 == response.status, f"{serializer} failed"
        assert f"{serializer}; charset=utf-8" == response.headers["Content-Type"]
        data = await response.text()
        g = Graph().parse(data=data, format=serializer)
        assert 0 < len(g), f"{serializer} has no triples"

    headers = MultiDict([(hdrs.ACCEPT, "text/*")])
    response = await client.get("/catalogs", headers=headers)
    assert 200 == response.status, "*/* failed"
    assert "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    data = await response.text()
    g = Graph().parse(data=data, format="text/turtle")
    assert 0 < len(g), "*/* has no triples"

    headers = MultiDict([(hdrs.ACCEPT, "*/*")])
    response = await client.get("/catalogs", headers=headers)
    assert 200 == response.status, "*/* failed"
    assert "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    data = await response.text()
    g = Graph().parse(data=data, format="text/turtle")
    assert 0 < len(g), "*/* has no triples"

    headers = MultiDict(
        [(hdrs.ACCEPT, "text/turtle"), (hdrs.ACCEPT, "application/ld+json")]
    )
    response = await client.get("/catalogs", headers=headers)
    assert 200 == response.status, "Multiple headers failed"
    assert "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    data = await response.text()
    g = Graph().parse(data=data, format="text/turtle")
    assert 0 < len(g), "*/* has no triples"

    headers = MultiDict([(hdrs.ACCEPT, "not/acceptable")])
    response = await client.get("/catalogs", headers=headers)
    assert 406 == response.status, "not/acceptable failed"


@pytest.mark.integration
async def test_catalogs_content_negotiation(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 200 and correct content-type."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value=_mock_query_and_convert_result(),
    )

    header_value = "text/turtle, application/ld+json"
    headers = MultiDict([(hdrs.ACCEPT, header_value)])
    response = await client.get("/catalogs", headers=headers)
    assert 200 == response.status, f"'{header_value}' failed"
    assert (
        "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    ), f"For header-value '{header_value}', content-Type in response-header should be text/turtle."  # noqa: B950

    header_value = "application/ld+json, text/turtle"
    headers = MultiDict([(hdrs.ACCEPT, header_value)])
    response = await client.get("/catalogs", headers=headers)
    assert 200 == response.status, f"'{header_value}' failed"
    assert (
        "application/ld+json; charset=utf-8" == response.headers["Content-Type"]
    ), f"For '{header_value}', content-Type in response-header should be application/ld+json."

    header_value = "not/acceptable, */*"
    headers = MultiDict([(hdrs.ACCEPT, header_value)])
    response = await client.get("/catalogs", headers=headers)
    assert 200 == response.status, f"'{header_value}' failed"
    assert (
        "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    ), f"For header-value '{header_value}', content-Type in response-header should be text/turtle."  # noqa: B950

    header_value = "text/plain,*/*"
    headers = MultiDict([(hdrs.ACCEPT, header_value)])
    response = await client.get("/catalogs", headers=headers)
    assert 200 == response.status, f"'{header_value}' failed"
    assert (
        "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    ), f"For header-value '{header_value}', content-Type in response-header should be text/turtle."  # noqa: B950

    header_value = "*/*,text/plain"
    headers = MultiDict([(hdrs.ACCEPT, header_value)])
    response = await client.get("/catalogs", headers=headers)
    assert 200 == response.status, f"'{header_value}' failed"
    assert (
        "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    ), f"For header-value '{header_value}', content-Type in response-header should be text/turtle."  # noqa: B950

    header_value = "application/json,application/*,*/*"
    headers = MultiDict([(hdrs.ACCEPT, header_value)])
    response = await client.get("/catalogs", headers=headers)
    assert 200 == response.status, f"'{header_value}' failed"
    assert (
        "application/ld+json; charset=utf-8" == response.headers["Content-Type"]
    ), f"For header-value '{header_value}', content-Type in response-header should be application/ld+json."  # noqa: B950

    header_value = "*/*;q=0.8,text/plain,application/signed-exchange;q=0.9,application/ld+json"  # noqa: B950
    headers = MultiDict([(hdrs.ACCEPT, header_value)])
    response = await client.get("/catalogs", headers=headers)
    assert 200 == response.status, f"'{header_value}' failed"
    assert (
        "application/ld+json; charset=utf-8" == response.headers["Content-Type"]
    ), f"For header-value '{header_value}', content-Type in response-header should be application/ld+json."  # noqa: B950

    header_value = "*/*;q=0.8;v=b3,text/plain,application/signed-exchange;v=b3;q=0.9,application/ld+json"  # noqa: B950
    headers = MultiDict([(hdrs.ACCEPT, header_value)])
    response = await client.get("/catalogs", headers=headers)
    assert 200 == response.status, f"'{header_value}' failed"
    assert (
        "application/ld+json; charset=utf-8" == response.headers["Content-Type"]
    ), f"For header-value '{header_value}', content-Type in response-header should be application/ld+json."  # noqa: B950


@pytest.mark.integration
async def test_catalogs_by_id(client: _TestClient, mocker: MockFixture) -> None:
    """Should return 200 and a turtle serialization."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value=_mock_query_and_convert_result(),
    )

    response = await client.get("/catalogs/123")

    assert 200 == response.status
    assert "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    data = await response.text()
    assert 0 < len(data)
    g = Graph().parse(data=data, format="turtle")
    assert 0 < len(g)


@pytest.mark.integration
async def test_delete_catalog(client: _TestClient, mocker: MockFixture) -> None:
    """Should return 204 No Content."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value=_mock_query_and_convert_result(),
    )
    mocker.patch("SPARQLWrapper.SPARQLWrapper.query", return_value=_mock_query_result())
    mocker.patch("jwt.decode", return_value={"sub": "123"})
    headers = MultiDict([(hdrs.AUTHORIZATION, "Bearer blablabla")])

    response = await client.delete("/catalogs/123", headers=headers)

    assert 204 == response.status


@pytest.mark.integration
async def test_delete_catalog_does_not_exist(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 204 No Content."""
    # Set up the mock
    mocker.patch("SPARQLWrapper.SPARQLWrapper.queryAndConvert", return_value="")
    mocker.patch("SPARQLWrapper.SPARQLWrapper.query", return_value=_mock_query_result())
    mocker.patch("jwt.decode", return_value={"sub": "123"})
    headers = MultiDict([(hdrs.AUTHORIZATION, "Bearer blablabla")])

    response = await client.delete("/catalogs/does_not_exist", headers=headers)

    assert 404 == response.status


@pytest.mark.integration
async def test_delete_catalog_unsuccessful_result(
    client: _TestClient, mocker: MockFixture
) -> None:
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
    mocker.patch("jwt.decode", return_value={"sub": "123"})
    headers = MultiDict([(hdrs.AUTHORIZATION, "Bearer blablabla")])

    response = await client.delete("/catalogs/123", headers=headers)

    assert 400 == response.status


@pytest.mark.integration
async def test_delete_catalog_fails_with_exception(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value=_mock_query_and_convert_result(),
    )
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.query",
        side_effect=SPARQLWrapperException(response=b"An error occurred"),
    )
    mocker.patch("jwt.decode", return_value={"sub": "123"})
    headers = MultiDict([(hdrs.AUTHORIZATION, "Bearer blablabla")])

    response = await client.delete("/catalogs/123", headers=headers)

    assert response.status == 500


@pytest.mark.integration
async def test_get_catalog_by_id_does_not_exist(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 404."""
    # Set up the mock
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value="",
    )

    response = await client.get("/catalogs/123")

    assert 404 == response.status
    data = await response.text()
    assert 0 == len(data)


@pytest.mark.integration
async def test_create_catalog_unauthenticated_fails(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401."""
    # Set up the mocks
    mocker.patch("yaml.safe_load", return_value=_mock_yaml_load())
    mocker.patch("SPARQLWrapper.SPARQLWrapper.query", return_value=True)
    headers = MultiDict(
        [
            (hdrs.CONTENT_TYPE, "application/json"),
            (hdrs.AUTHORIZATION, "Bearer blablabla"),
        ]
    )
    with open("./tests/files/catalog_1.json") as json_file:
        data = json.load(json_file)

    response = await client.post("/catalogs", headers=headers, data=json.dumps(data))

    assert response.status == 401
    assert response.headers["WWW-Authenticate"] == 'Bearer token_type="JWT"'


@pytest.mark.integration
async def test_delete_catalog_unauthenticated_fails(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 401."""
    # Set up the mocks
    mocker.patch("yaml.safe_load", return_value=_mock_yaml_load())
    mocker.patch("SPARQLWrapper.SPARQLWrapper.query", return_value=True)

    response = await client.delete("/catalogs")

    assert response.status == 401
    assert response.headers["WWW-Authenticate"] == 'Bearer token_type="JWT"'


@pytest.mark.integration
async def test_create_catalog_success(client: _TestClient, mocker: MockFixture) -> None:
    """Should return 201 and location header."""
    # Set up the mocks
    mocker.patch("yaml.safe_load", return_value=_mock_yaml_load())
    mocker.patch("SPARQLWrapper.SPARQLWrapper.query", return_value=True)
    mocker.patch("jwt.decode", return_value={"sub": "123"})
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        return_value=_mock_full_query_result(),
    )
    headers = MultiDict(
        [
            (hdrs.CONTENT_TYPE, "application/json"),
            (hdrs.AUTHORIZATION, "Bearer blablabla"),
        ]
    )

    with open("./tests/files/catalog_1.json") as json_file:
        data = json.load(json_file)

    response = await client.post("/catalogs", headers=headers, data=json.dumps(data))

    assert response.status == 200
    assert "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    data = await response.text()
    assert 0 < len(data)
    g1 = Graph().parse(data=data, format="turtle")
    assert 0 < len(g1)

    # Verify that all of the input is created:
    response = await client.get("/catalogs/1234")

    assert 200 == response.status
    assert "text/turtle; charset=utf-8" == response.headers["Content-Type"]
    data = await response.text()
    assert 0 < len(data)
    g2 = Graph().parse(data=data, format="turtle")
    assert 0 < len(g2)

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic


@pytest.mark.integration
async def test_create_catalog_failure(client: _TestClient, mocker: MockFixture) -> None:
    """Should return status_code 400."""
    mocker.patch("jwt.decode", return_value={"sub": "123"})
    headers = MultiDict(
        [
            (hdrs.CONTENT_TYPE, "application/json"),
            (hdrs.AUTHORIZATION, "Bearer blablabla"),
        ]
    )

    response = await client.post("/catalogs", headers=headers, data="{}")

    assert response.status == 400


@pytest.mark.integration
async def test_create_catalog_key_error_failure(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return status_code 400 and message."""
    mocker.patch("jwt.decode", return_value={"sub": "123"})
    headers = MultiDict(
        [
            (hdrs.AUTHORIZATION, "Bearer blablabla"),
            (hdrs.CONTENT_TYPE, "application/json"),
        ]
    )
    data = dict(identifier="http://localhost:8000/catalogs/1")

    response = await client.post("/catalogs", headers=headers, data=json.dumps(data))

    assert response.status == 400

    data = await response.json()
    assert data["msg"] == "KeyError when processing request body"


@pytest.mark.integration
async def test_create_catalog_type_error_failure(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return status_code 400 and message."""
    mocker.patch("jwt.decode", return_value={"sub": "123"})
    headers = MultiDict(
        [
            (hdrs.AUTHORIZATION, "Bearer blablabla"),
            (hdrs.CONTENT_TYPE, "application/json"),
        ]
    )
    # Point here is that apis array should have dicts, not strings as members:
    data = dict(
        identifier="http://localhost:8000/catalogs/1",
        title={"en": "Title with language tag"},
        description={"en": "description with language tag"},
        publisher="http://example.com/publishers/1",
        apis=["http://api.url.com"],
    )

    response = await client.post("/catalogs", headers=headers, data=json.dumps(data))

    assert response.status == 400

    data = await response.json()
    assert data["msg"] == "TypeError when processing request body"


@pytest.mark.integration
async def test_get_catalog_fails_with_exception(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        side_effect=SPARQLWrapperException(response=b"An error occurred"),
    )

    response = await client.get("/catalogs")

    assert response.status == 500


@pytest.mark.integration
async def test_catalog_by_id_fails_with_exception(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.queryAndConvert",
        side_effect=SPARQLWrapperException(response=b"An error occurred"),
    )

    response = await client.get("/catalogs/123")

    assert response.status == 500


@pytest.mark.integration
async def test_create_catalog_fails_with_exception(
    client: _TestClient, mocker: MockFixture
) -> None:
    """Should return 500."""
    # Configure the mock to return a response with an OK status code.
    mocker.patch("jwt.decode", return_value={"sub": "123"})
    mocker.patch(
        "SPARQLWrapper.SPARQLWrapper.query",
        side_effect=SPARQLWrapperException(response=b"An error occurred"),
    )

    headers = MultiDict(
        [
            (hdrs.AUTHORIZATION, "Bearer blablabla"),
            (hdrs.CONTENT_TYPE, "application/json"),
        ]
    )
    with open("./tests/files/catalog_1.json") as json_file:
        data = json.load(json_file)

    response = await client.post("/catalogs", headers=headers, data=json.dumps(data))

    assert response.status == 500


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

    <http://localhost:8000/catalogs/1> a dcat:Catalog .
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
