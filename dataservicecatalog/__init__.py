import os
import logging
from flask import Flask, Response
import rdflib
from dotenv import load_dotenv

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Load .env if any
    load_dotenv(override=True)
    # Make sure necessary environment variables are set:
    HOST_URL = os.environ.get("HOST_URL")
    if not HOST_URL:
        raise ValueError("No HOST_URL set for Flask application")
    PUBLISHER_URL = os.environ.get("PUBLISHER_URL")
    if not PUBLISHER_URL:
        raise ValueError("No PUBLISHER_URL set for Flask application")


    from .model import db
    db.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import catalogs
    app.register_blueprint(catalogs.bp)

    from . import dataservices
    app.register_blueprint(dataservices.bp)

    @app.route('/ready', methods=['GET'])
    def isReady():
        return "OK"

    @app.route('/ping', methods=['GET'])
    def isAlive():
        return "OK"

    return app
