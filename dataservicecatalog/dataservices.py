from flask import (Blueprint, Response, request, abort)
from .model.repository import fetch_dataservices, fetch_dataservice_by_id
from .lib.mappers import map_dataservices_to_rdf, map_dataservice_to_rdf
import jsonpickle
jsonpickle.set_preferred_backend('json')


bp = Blueprint('dataservices', __name__, url_prefix='/dataservices')


@bp.route('', methods=['GET'])
def getDataservices():
    dataservices = fetch_dataservices()
    if request.headers.get('Accept'):
        if 'application/json' == request.headers['Accept']:
            return Response(jsonpickle.encode(dataservices, unpicklable=False),
                            mimetype='application/json')
        elif 'text/turtle' == request.headers['Accept']:
            return Response(map_dataservices_to_rdf(dataservices, 'turtle'),
                            mimetype='text/turtle')
        elif 'application/rdf+xml' == request.headers['Accept']:
            return Response(map_dataservices_to_rdf(dataservices, 'xml'),
                            mimetype='application/rdf+xml')
        elif 'application/ld+json' == request.headers['Accept']:
            return Response(map_dataservices_to_rdf(dataservices, 'json-ld'),
                            mimetype='application/ld+json')
        return Response(map_dataservices_to_rdf(dataservices, 'turtle'),
                        mimetype='text/turtle')
    return Response(map_dataservices_to_rdf(dataservices, 'turtle'),
                    mimetype='text/turtle')


@bp.route('/<int:id>', methods=['GET'])
def getDataserviceById(id):
    dataservice = fetch_dataservice_by_id(id)
    if dataservice is None:
        abort(404)
    if request.headers.get('Accept'):
        if 'application/json' == request.headers['Accept']:
            return Response(jsonpickle.encode(dataservice, unpicklable=False),
                            mimetype='application/json')
        elif 'text/turtle' == request.headers['Accept']:
            return Response(map_dataservice_to_rdf(dataservice, 'turtle'),
                            mimetype='text/turtle')
        elif 'application/rdf+xml' == request.headers['Accept']:
            return Response(map_dataservice_to_rdf(dataservice, 'xml'),
                            mimetype='application/rdf+xml')
        elif 'application/ld+json' == request.headers['Accept']:
            return Response(map_dataservice_to_rdf(dataservice, 'json-ld'),
                            mimetype='application/ld+json')
        return Response(map_dataservice_to_rdf(dataservice, 'turtle'),
                        mimetype='text/turtle')
    return Response(map_dataservice_to_rdf(dataservice, 'turtle'),
                    mimetype='text/turtle')
