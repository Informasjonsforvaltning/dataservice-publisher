"""Repository module for catalogs."""
import asyncio
import json
import logging
from typing import Any, Dict

from aiohttp import hdrs, web
from content_negotiation import decide_content_type, NoAgreeableContentTypeError

from dataservice_publisher.service.catalog_service import (
    create_catalog,
    delete_catalog,
    fetch_catalogs,
    get_catalog_by_id,
    RequestBodyError,
)

SUPPORTED_CONTENT_TYPES = [
    "text/turtle",
    "application/rdf+xml",
    "application/ld+json",
    "application/n-triples",
]


class Catalogs(web.View):
    """Class representing catalogs resoweb.urce."""

    async def get(self) -> web.Response:
        """Get all catalogs."""
        try:
            content_type = decide_content_type(
                self.request.headers.getall(hdrs.ACCEPT), SUPPORTED_CONTENT_TYPES
            )
        except NoAgreeableContentTypeError as e:
            raise web.HTTPNotAcceptable() from e

        catalogs = await fetch_catalogs()
        body = catalogs.serialize(format=content_type, encoding="utf-8")

        return web.Response(
            body=body,
            content_type=content_type,
            charset="utf-8",
        )

    async def post(self) -> web.Response:
        """Create a catalog and return the resulting graph."""
        new_catalog: Dict[str, Any] = await self.request.json()
        if new_catalog and "identifier" in new_catalog:
            try:
                asyncio.create_task(create_catalog(new_catalog))
                return web.Response(
                    body="started catalog creation",
                    content_type="text/plain",
                    charset="utf-8",
                )
            except RequestBodyError as e:
                return web.Response(
                    status=400,
                    body=json.dumps({"msg": str(e)}),
                    content_type="application/json",
                )
        return web.Response(
            status=400,
            body=json.dumps({"msg": "No identifier provided"}),
            content_type="application/json",
        )


class Catalog(web.View):
    """Class representing catalog resource."""

    async def get(self) -> web.Response:
        """Get catalog by id."""
        try:
            content_type = decide_content_type(
                self.request.headers.getall(hdrs.ACCEPT), SUPPORTED_CONTENT_TYPES
            )
        except NoAgreeableContentTypeError as e:
            raise web.HTTPNotAcceptable() from e

        id = self.request.match_info["id"]
        logging.debug(f"Getting catalog with id {id}")

        catalog = await get_catalog_by_id(id)
        if len(catalog) == 0:
            return web.Response(status=404)
        return web.Response(
            body=catalog.serialize(format=content_type, encoding="utf-8"),
            content_type=content_type,
            charset="utf-8",
        )

    async def delete(self) -> web.Response:
        """Delete catalog given by id."""
        id = self.request.match_info["id"]
        logging.debug(f"Delete catalog with id {id}")

        catalog = await get_catalog_by_id(id)
        if len(catalog) == 0:
            return web.Response(status=404)
        result = await delete_catalog(id)
        if result:
            return web.Response(status=204)
        return web.Response(status=400)
