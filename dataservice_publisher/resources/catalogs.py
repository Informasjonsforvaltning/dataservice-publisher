"""Repository module for catalogs."""
import json
import logging
from typing import Any, Dict

from aiohttp import web

from dataservice_publisher.service.catalog_service import (
    create_catalog,
    delete_catalog,
    fetch_catalogs,
    get_catalog_by_id,
    RequestBodyError,
)


class Catalogs(web.View):
    """Class representing catalogs resoweb.urce."""

    async def get(self) -> web.Response:
        """Get all catalogs."""
        catalogs = fetch_catalogs()
        return web.Response(
            body=catalogs.serialize(format="text/turtle", encoding="utf-8"),
            content_type="text/turtle",
            charset="utf-8",
        )

    async def post(self) -> web.Response:
        """Create a catalog and return the resulting graph."""
        new_catalog: Dict[str, Any] = await self.request.json()
        if new_catalog and "identifier" in new_catalog:
            try:
                catalog = create_catalog(new_catalog)
                return web.Response(
                    body=catalog.serialize(format="text/turtle", encoding="utf-8"),
                    content_type="text/turtle",
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
        id = self.request.match_info["id"]
        logging.debug(f"Getting catalog with id {id}")

        catalog = get_catalog_by_id(id)
        if len(catalog) == 0:
            return web.Response(status=404)
        return web.Response(
            body=catalog.serialize(format="text/turtle", encoding="utf-8"),
            content_type="text/turtle",
            charset="utf-8",
        )

    async def delete(self) -> web.Response:
        """Delete catalog given by id."""
        id = self.request.match_info["id"]
        logging.debug(f"Delete catalog with id {id}")

        catalog = get_catalog_by_id(id)
        if len(catalog) == 0:
            return web.Response(status=404)
        result = delete_catalog(id)
        if result:
            return web.Response(status=204)
        return web.Response(status=400)
