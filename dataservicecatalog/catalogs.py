import functools
import json

from flask import (
    Blueprint, flash, g, redirect, Response, request, session, url_for
)

from dataservicecatalog.db import get_db
from dataservicecatalog.mappers import map_to_rdf

bp = Blueprint('catalogs', __name__, url_prefix='/')

@bp.route('/catalogs')
def catalogs():
    db = get_db()
    catalogs = db.all()
    if request.headers.get('Accept'):
        if 'application/json' == request.headers['Accept']:
            return Response(json.dumps(catalogs), mimetype='application/json')
        elif 'text/turtle' == request.headers['Accept']:
            return Response(map_to_rdf(catalogs,'turtle'), mimetype='text/turtle')
        elif 'application/rdf+xml' == request.headers['Accept']:
            return Response(map_to_rdf(catalogs,'xml'), mimetype='application/rdf+xml')
        elif 'application/ld+json' == request.headers['Accept']:
            return Response(map_to_rdf(catalogs,'json-ld'), mimetype='application/ld+json')
        else:
            return Response(map_to_rdf(catalogs,'turtle'), mimetype='text/turtle')
    else:
        return Response(map_to_rdf(catalogs,'turtle'), mimetype='text/turtle')
