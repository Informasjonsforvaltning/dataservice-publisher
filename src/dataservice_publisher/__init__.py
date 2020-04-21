"""Package for making catalog of dataservices available in a Flask API."""
import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask

from . import catalogs
from . import dataservices
from .model import db

__version__ = "0.1.0"


def create_app(test_config: Any = None) -> Flask:
    """Create app."""
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

    db.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(catalogs.bp)

    app.register_blueprint(dataservices.bp)

    @app.route("/ready", methods=["GET"])
    def isReady() -> str:
        """Ready route function."""
        return "OK"

    @app.route("/ping", methods=["GET"])
    def isAlive() -> str:
        """Ping route function."""
        return "OK"

    return app
