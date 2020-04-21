"""Catalogs module for mapping a catalog to rdf."""
from flask import abort, Blueprint, request, Response
import jsonpickle

from .mapper.mappers import map_catalog_to_rdf, map_catalogs_to_rdf
from .model.repository import fetch_catalog_by_id, fetch_catalogs

jsonpickle.set_preferred_backend("json")

bp = Blueprint("catalogs", __name__, url_prefix="/catalogs")


@bp.route("", methods=["GET"])
def getCatalogs() -> Response:
    """Get all catalogs."""
    catalogs = fetch_catalogs()
    if request.headers.get("Accept"):
        if "application/json" == request.headers["Accept"]:
            return Response(
                jsonpickle.encode(catalogs, unpicklable=False),
                mimetype="application/json",
            )
        elif "text/turtle" == request.headers["Accept"]:
            return Response(
                map_catalogs_to_rdf(catalogs, "turtle"), mimetype="text/turtle"
            )
        elif "application/rdf+xml" == request.headers["Accept"]:
            return Response(
                map_catalogs_to_rdf(catalogs, "xml"), mimetype="application/rdf+xml"
            )
        elif "application/ld+json" == request.headers["Accept"]:
            return Response(
                map_catalogs_to_rdf(catalogs, "json-ld"), mimetype="application/ld+json"
            )
        return Response(map_catalogs_to_rdf(catalogs, "turtle"), mimetype="text/turtle")
    return Response(map_catalogs_to_rdf(catalogs, "turtle"), mimetype="text/turtle")


@bp.route("/<int:id>", methods=["GET"])
def getCatalogById(id: int) -> Response:
    """Get catalog by id."""
    catalog = fetch_catalog_by_id(id)
    if catalog is None:
        abort(404)
    if request.headers.get("Accept"):
        if "application/json" == request.headers["Accept"]:
            return Response(
                jsonpickle.encode(catalog, unpicklable=False),
                mimetype="application/json",
            )
        elif "text/turtle" == request.headers["Accept"]:
            return Response(
                map_catalog_to_rdf(catalog, "turtle"), mimetype="text/turtle"
            )
        elif "application/rdf+xml" == request.headers["Accept"]:
            return Response(
                map_catalog_to_rdf(catalog, "xml"), mimetype="application/rdf+xml"
            )
        elif "application/ld+json" == request.headers["Accept"]:
            return Response(
                map_catalog_to_rdf(catalog, "json-ld"), mimetype="application/ld+json"
            )
        return Response(map_catalog_to_rdf(catalog, "turtle"), mimetype="text/turtle")
    return Response(map_catalog_to_rdf(catalog, "turtle"), mimetype="text/turtle")
