"""Repository module for ready."""
import logging
from os import environ as env
from typing import Any

from dotenv import load_dotenv
from flask import Response
from flask_restful import Resource
import requests

# Get environment
load_dotenv()
FUSEKI_HOST = env.get("FUSEKI_HOST", "fuseki")
FUSEKI_PORT = int(env.get("FUSEKI_PORT", "3030"))


class Ready(Resource):
    """Class representing ready resource."""

    def get(self) -> Any:
        """Ready route function."""
        try:
            resp = requests.get(f"http://{FUSEKI_HOST}:{FUSEKI_PORT}/$/ping")
            if resp.status_code == 200:
                return Response("OK")
        except requests.exceptions.RequestException as e:
            logging.debug(e.response)
            raise e
