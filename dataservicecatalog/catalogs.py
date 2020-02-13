import functools
import json

from flask import (
    Blueprint, flash, g, redirect, Response, request, session, url_for
)

from dataservicecatalog.db import get_db

bp = Blueprint('catalogs', __name__, url_prefix='/')

@bp.route('/catalogs')
def catalogs():
    db = get_db()
    catalogs = db.all()
    return Response(json.dumps(catalogs), mimetype='application/json')
