"""Repository module for ping."""
from flask import Response
from flask_restful import Resource


class Ping(Resource):
    """Class representing ping resource."""

    def get(self) -> Response:
        """Ping route function."""
        return Response("OK")
