"""Test cases for the catalogs paths."""
import asyncio
import json
from os import environ as env
from typing import Any

from aiohttp import ClientSession, hdrs
from dotenv import load_dotenv
import pytest
from rdflib import DCAT, Graph, RDF
from rdflib.compare import graph_diff, isomorphic

# Get environment
load_dotenv()
ADMIN_USERNAME = env.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = env.get("ADMIN_PASSWORD")


@pytest.fixture(scope="session")
def event_loop(request: Any) -> Any:
    """Redefine the event_loop fixture to have the same scope."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.contract
@pytest.mark.asyncio
@pytest.fixture(scope="session")
@pytest.skip
async def access_token(http_service: Any) -> Any:
    """Ensure that HTTP service is up and responsive."""
    """Should return status code 200 and an access_token."""

    headers = {"Content-Type": "application/json"}
    data = dict(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)

    url = f"{http_service}/login"
    async with ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            assert 200 == resp.status
            data = await resp.json()

    return data["access_token"]


@pytest.mark.contract
@pytest.mark.asyncio
@pytest.skip
async def test_create_catalog_unauthenticated(http_service: Any) -> None:
    """Should return status code 401."""
    url = f"{http_service}/catalogs"
    with open("./tests/files/catalog_1.json") as json_file:
        data = json.load(json_file)
    headers = {"Content-Type": "application/json"}
    async with ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            assert 401 == resp.status
            assert resp.headers["WWW-Authenticate"]


@pytest.mark.contract
@pytest.mark.asyncio
@pytest.skip
async def test_create_catalog(http_service: Any, access_token: str) -> None:
    """Should return status code 201 and a valid location header."""
    url = f"{http_service}/catalogs"
    with open("./tests/files/catalog_1.json") as json_file:
        data = json.load(json_file)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    async with ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            assert 200 == resp.status, "error creating catalog"
            assert "text/turtle; charset=utf-8" == resp.headers[hdrs.CONTENT_TYPE]
            data = await resp.text()

            assert 0 < len(data)
            g = Graph().parse(data=data, format="turtle")
            assert 0 < len(g)

            # Check that the catalog is in the catalogs graph, and extract the catalog's URI:
            catalog_url: str = g.value(None, RDF.type, DCAT.Catalog, any=False)
            assert catalog_url

        # Get the catalog's graph and check that it is isomorphic with the one we created:
        async with session.get(catalog_url) as resp:
            assert 200 == resp.status, f"new catalog not found: {catalog_url}"
            data = await resp.text()
            assert 0 < len(data)
            g1 = Graph().parse(data=data, format="turtle")
            assert 0 < len(g1)

    g2 = Graph().parse("tests/files/catalog_1.ttl", format="turtle")

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic, "graphs are not isomorphic"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_catalogs(http_service: Any) -> None:
    """Should return status code 200 and many catalogs in a turtle body."""
    url = f"{http_service}/catalogs"
    async with ClientSession() as session:
        async with session.get(url) as resp:
            assert 200 == resp.status
            assert "text/turtle; charset=utf-8" == resp.headers[hdrs.CONTENT_TYPE]
            data = await resp.text()
            assert 0 < len(data)
            g = Graph().parse(data=data, format="turtle")
            assert 0 < len(g)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_catalog_by_id(http_service: Any) -> None:
    """Should return status code 200 and single catalog in a turtle body."""
    url = f"{http_service}/catalogs/1"
    async with ClientSession() as session:
        async with session.get(url) as resp:
            assert 200 == resp.status
            assert "text/turtle; charset=utf-8" == resp.headers[hdrs.CONTENT_TYPE]
            data = await resp.text()
            assert 0 < len(data)
            g = Graph().parse(data=data, format="turtle")
            assert 0 < len(g)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_catalog_by_id_json_ld(http_service: Any) -> None:
    """Should return status code 200 and single catalog in a json-ld body."""
    url = f"{http_service}/catalogs/1"
    headers = {"Accept": "application/ld+json"}
    async with ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            assert 200 == resp.status
            assert (
                "application/ld+json; charset=utf-8" == resp.headers[hdrs.CONTENT_TYPE]
            )
            data = await resp.json()
            assert 0 < len(data)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_catalog_by_id_json(http_service: Any) -> None:
    """Should return status code 406."""
    url = f"{http_service}/catalogs/1"
    headers = {"Accept": "application/json"}
    async with ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            assert 406 == resp.status


@pytest.mark.contract
@pytest.mark.asyncio
async def test_delete_catalog_unauthenticated(http_service: Any) -> None:
    """Should return status code 401."""
    url = f"{http_service}/catalogs/1"
    async with ClientSession() as session:
        async with session.delete(url) as resp:
            assert 401 == resp.status
            assert resp.headers["WWW-Authenticate"]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_delete_catalog_by_id(http_service: Any, access_token: str) -> None:
    """Should return status code 204."""
    url = f"{http_service}/catalogs/1"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    async with ClientSession() as session:
        async with session.delete(url, headers=headers) as resp:
            assert 204 == resp.status
            data = await resp.text()
    assert 0 == len(data)


# - BAD CASES:
@pytest.mark.contract
async def test_not_found_gives_404(http_service: Any) -> None:
    """Should return 404."""
    url = f"{http_service}/catalogs/ID_NOT_IN_DB"
    async with ClientSession() as session:
        async with session.get(url) as resp:
            assert 404 == resp.status


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
