"""Repository module for catalogs."""
from typing import Any, Dict

from flask import make_response, request, Response
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from dataservice_publisher.service.catalog_service import (
    create_catalog,
    delete_catalog,
    fetch_catalogs,
    get_catalog_by_id,
)


class Catalogs(Resource):
    """Class representing catalogs resource."""

    def get(self) -> Response:
        """Get all catalogs."""
        catalogs = fetch_catalogs()
        return Response(
            catalogs.serialize(format="text/turtle", encoding="utf-8"),
            mimetype="text/turtle",
        )

    @jwt_required()
    def post(self) -> Response:
        """Create a catalog and return the resulting graph."""
        new_catalog: Dict[str, Any] = request.json  # type: ignore
        catalog = create_catalog(new_catalog)
        return Response(
            catalog.serialize(format="text/turtle", encoding="utf-8"),
            mimetype="text/turtle",
        )


class Catalog(Resource):
    """Class representing catalog resource."""

    def get(self, id: str) -> Response:
        """Get catalog by id."""
        catalog = get_catalog_by_id(id)
        response = make_response()
        if len(catalog) == 0:
            response.status_code = 404
            return response
        return Response(
            catalog.serialize(format="text/turtle", encoding="utf-8"),
            mimetype="text/turtle",
        )

    def delete(self, id: str) -> Response:
        """Delete catalog given by id."""
        catalog = get_catalog_by_id(id)
        response = make_response()
        if len(catalog) == 0:
            response.status_code = 404
            return response
        result = delete_catalog(id)
        if result:
            response.status_code = 204
            return response
        response.status_code = 400
        return response
