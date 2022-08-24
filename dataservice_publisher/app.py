"""Package for making catalog of dataservices available in a Flask API."""
import json
from os import environ as env
from typing import Any

from dotenv import load_dotenv
from flask import (
    Flask,
    make_response,
    Response,
)
from flask_jwt_extended import (
    JWTManager,
)
from flask_restful import Api
import requests
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException

from .exceptions.exceptions import RequestBodyError
from .resources.catalogs import Catalog, Catalogs
from .resources.login import Login
from .resources.ping import Ping
from .resources.ready import Ready


__version__ = "0.1.0"


def create_app(test_config: Any = None) -> Flask:
    """Create and configure the app."""
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # Get environment
    load_dotenv()

    app.config["SECRET_KEY"] = env.get("SECRET_KEY")
    app.config["PROPAGATE_EXCEPTIONS"] = True

    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def unauthorized_callback(msg: str) -> Response:
        response = make_response()
        response.data = json.dumps({"msg": msg})
        response.content_type = "application/json"
        response.headers["WWW-Authenticate"] = 'Bearer token_type="JWT"'
        response.status_code = 401
        return response

    api = Api(app)
    # Routes
    api.add_resource(Login, "/login")
    api.add_resource(Ping, "/ping")
    api.add_resource(Ready, "/ready")
    api.add_resource(Catalogs, "/catalogs")
    api.add_resource(Catalog, "/catalogs/<string:id>")

    @app.errorhandler(SPARQLWrapperException)
    def handle_sparql_wrapper_exceptions(e: SPARQLWrapperException) -> Response:
        # replace the body with JSON
        response = make_response()
        response.data = json.dumps({"msg": e.msg})
        response.content_type = "application/json"
        response.status_code = 500
        return response

    @app.errorhandler(requests.exceptions.RequestException)
    def handle_request_exceptions(e: requests.exceptions.RequestException) -> Response:
        # replace the body with JSON
        response = make_response()
        response.data = json.dumps({"msg": "ConnectionError"})
        response.content_type = "application/json"
        response.status_code = 500
        return response

    @app.errorhandler(RequestBodyError)
    def handle_exceptions(e: RequestBodyError) -> Response:
        # replace the body with JSON
        response = make_response()
        response.data = json.dumps({"msg": e.msg})
        response.content_type = "application/json"
        response.status_code = 400
        return response

    return app
