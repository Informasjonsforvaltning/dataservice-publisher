"""Repository module for catalogs."""
from flask import abort, make_response, request, Response
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from dataservice_publisher.service.catalog_service import (
    create_catalog,
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

    @jwt_required
    def post(self) -> Response:
        """Create a catalog and return location header."""
        if request.json is None:
            abort(400)
        catalog_identifier = create_catalog(request.json)
        response = make_response()
        response.headers["Location"] = catalog_identifier
        response.status_code = 201
        return response


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
