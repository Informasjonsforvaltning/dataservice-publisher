import functools
import json
import jsonpickle
jsonpickle.set_preferred_backend('json')

from flask import (
    Blueprint, flash, g, redirect, Response, request, session, url_for, abort, jsonify
)

from .model.repository import fetch_dataservices, fetch_dataservice_by_id
from .lib.mappers import map_dataservices_to_rdf, map_dataservice_to_rdf

bp = Blueprint('dataservices', __name__, url_prefix='/dataservices')

@bp.route('', methods=['GET'])
def getDataservices():
    dataservices = fetch_dataservices()
    if request.headers.get('Accept'):
        if 'application/json' == request.headers['Accept']:
            return Response(jsonpickle.encode(dataservices, unpicklable=False), mimetype='application/json')
        elif 'text/turtle' == request.headers['Accept']:
            return Response(map_dataservices_to_rdf(dataservices,'turtle'), mimetype='text/turtle')
        elif 'application/rdf+xml' == request.headers['Accept']:
            return Response(map_dataservices_to_rdf(dataservices,'xml'), mimetype='application/rdf+xml')
        elif 'application/ld+json' == request.headers['Accept']:
            return Response(map_dataservices_to_rdf(dataservices,'json-ld'), mimetype='application/ld+json')
        else:
            return Response(map_dataservices_to_rdf(dataservices,'turtle'), mimetype='text/turtle')
    else:
        return Response(map_dataservices_to_rdf(dataservices,'turtle'), mimetype='text/turtle')

@bp.route('/', methods=['POST'])
def create_dataservice():
    # print('request.headers: ', request.headers)
    # print('request.mimetype: ', request.mimetype)
    # print('request.get_json: ', request.get_json(silent=False, force=True))
    # print('request.json: ', request.json)
    # print('request.data: ', request.data)
    abort(501)
# TODO: create a POST endpoint where at the minimum a pointer to an openapi-spec can be posted.

@bp.route('/<int:id>', methods=['GET'])
def getDataserviceById(id):
    dataservice = fetch_dataservice_by_id(id)
    if dataservice == None:
        abort(404)
    if request.headers.get('Accept'):
        if 'application/json' == request.headers['Accept']:
            return Response(jsonpickle.encode(dataservice, unpicklable=False), mimetype='application/json')
        elif 'text/turtle' == request.headers['Accept']:
            return Response(map_dataservice_to_rdf(dataservice,'turtle'), mimetype='text/turtle')
        elif 'application/rdf+xml' == request.headers['Accept']:
            return Response(map_dataservice_to_rdf(dataservice,'xml'), mimetype='application/rdf+xml')
        elif 'application/ld+json' == request.headers['Accept']:
            return Response(map_dataservice_to_rdf(dataservice,'json-ld'), mimetype='application/ld+json')
        else:
            return Response(map_dataservice_to_rdf(dataservice,'turtle'), mimetype='text/turtle')
    else:
        return Response(map_dataservice_to_rdf(dataservice,'turtle'), mimetype='text/turtle')
