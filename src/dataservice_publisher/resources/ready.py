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
FUSEKI_HOST_URL = env.get("FUSEKI_HOST_URL", "http://fuseki:3030")


class Ready(Resource):
    """Class representing ready resource."""

    def get(self) -> Any:
        """Ready route function."""
        try:
            resp = requests.get(f"{FUSEKI_HOST_URL}/$/ping")
            if resp.status_code == 200:
                return Response("OK")
        except requests.exceptions.RequestException as e:
            logging.debug(e.response)
            raise e
