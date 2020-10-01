"""Repository module for ping."""
import json
from os import environ as env

from dotenv import load_dotenv
from flask import make_response, request, Response
from flask_jwt_extended import create_access_token
from flask_restful import Resource

# Get environment
load_dotenv()
ADMIN_USERNAME = env.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = env.get("ADMIN_PASSWORD")


class Login(Resource):
    """Class representing ping resource."""

    def post(self) -> Response:
        """Login to create a jwt token."""
        response = make_response()
        if not request.is_json:
            response.data = json.dumps({"msg": "Missing JSON in request"})
            response.status_code = 401
            return response

        username = request.json.get("username", None)
        password = request.json.get("password", None)

        if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
            response.data = json.dumps({"msg": "Bad username or password"})
            response.status_code = 401
            return response

        # Identity can be any data that is json serializable
        access_token = create_access_token(identity=username)
        response.data = json.dumps({"access_token": access_token})
        response.status_code = 200
        return response
