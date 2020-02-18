import functools
import json

from flask import (
    Blueprint, flash, g, redirect, Response, request, session, url_for, abort, jsonify
)

from .model.repository import fetch_catalogs, fetch_catalog_by_id
from .lib.mappers import map_catalogs_to_rdf, map_catalog_to_rdf

bp = Blueprint('catalogs', __name__, url_prefix='/catalogs')

@bp.route('', methods=['GET'])
def getCatalogs():
    catalogs = fetch_catalogs()
    if request.headers.get('Accept'):
        if 'application/json' == request.headers['Accept']:
            return Response(json.dumps([dict(c.__dict__) for c in catalogs]), mimetype='application/json')
        elif 'text/turtle' == request.headers['Accept']:
            return Response(map_catalogs_to_rdf(catalogs,'turtle'), mimetype='text/turtle')
        elif 'application/rdf+xml' == request.headers['Accept']:
            return Response(map_catalogs_to_rdf(catalogs,'xml'), mimetype='application/rdf+xml')
        elif 'application/ld+json' == request.headers['Accept']:
            return Response(map_catalogs_to_rdf(catalogs,'json-ld'), mimetype='application/ld+json')
        else:
            return Response(map_catalogs_to_rdf(catalogs,'turtle'), mimetype='text/turtle')
    else:
        return Response(map_catalogs_to_rdf(catalogs,'turtle'), mimetype='text/turtle')

@bp.route('/', methods=['POST'])
# TODO: create a POST where a catalog including dataservices can be posted

@bp.route('/<int:id>', methods=['GET'])
def getCatalogById(id):
    catalog = fetch_catalog_by_id(id)
    if catalog == None:
        abort(404)
    if request.headers.get('Accept'):
        if 'application/json' == request.headers['Accept']:
            return Response(json.dumps(catalog.__dict__), mimetype='application/json')
        elif 'text/turtle' == request.headers['Accept']:
            return Response(map_catalog_to_rdf(catalog,'turtle'), mimetype='text/turtle')
        elif 'application/rdf+xml' == request.headers['Accept']:
            return Response(map_catalog_to_rdf(catalog,'xml'), mimetype='application/rdf+xml')
        elif 'application/ld+json' == request.headers['Accept']:
            return Response(map_catalog_to_rdf(catalog,'json-ld'), mimetype='application/ld+json')
        else:
            return Response(map_catalog_to_rdf(catalog,'turtle'), mimetype='text/turtle')
    else:
        return Response(map_catalog_to_rdf(catalog,'turtle'), mimetype='text/turtle')
