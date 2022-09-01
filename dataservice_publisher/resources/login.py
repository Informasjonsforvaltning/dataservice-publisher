"""Repository module for ping."""
import json
from os import environ as env
from typing import Optional

from aiohttp import web
from dotenv import load_dotenv
import jwt

# Get environment
load_dotenv()
ADMIN_USERNAME = env.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = env.get("ADMIN_PASSWORD")
SHARED_SECRET = env.get("SECRET_KEY", None)


class Login(web.View):
    """Class representing login resource."""

    async def post(self) -> web.Response:
        """Login to create a jwt token."""
        if not self.request.headers.getone("Content-Type") == "application/json":
            raise web.HTTPUnsupportedMediaType()
        try:
            body = await self.request.json()
        except json.decoder.JSONDecodeError as e:
            raise web.HTTPUnauthorized() from e

        username = body.get("username", None)
        password = body.get("password", None)

        if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
            raise web.HTTPUnauthorized()

        # Identity can be any data that is json serializable
        access_token = await _get_token(identity=username)
        if not access_token:
            raise web.HTTPInternalServerError(reason="Could not create token")

        body = json.dumps({"access_token": access_token})
        return web.Response(status=200, content_type="application/json", body=body)


async def _get_token(identity: str) -> Optional[str]:
    if not SHARED_SECRET:
        return None
    return jwt.encode({"username": identity}, SHARED_SECRET)
