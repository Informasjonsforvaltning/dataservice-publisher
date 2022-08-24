"""Repository module for ready."""
import logging
from os import environ as env
from typing import Any

from dotenv import load_dotenv
from flask import make_response, Response
from flask_restful import Resource
import requests

# Get environment
load_dotenv()
FUSEKI_HOST_URL = env.get("FUSEKI_HOST_URL", "http://fuseki:3030")


class Ready(Resource):
    """Class representing ready resource."""

    def get(self) -> Any:
        """Ready route function."""
        try:
            resp = requests.get(f"{FUSEKI_HOST_URL}/fuseki/$/ping")
            if resp.status_code == 200:
                return Response("OK")
            else:
                response = make_response()
                response.status_code = 500
                return response
        except requests.exceptions.RequestException as e:
            logging.critical(f"Got exception from {FUSEKI_HOST_URL}: {type(e)}.")
            raise e
