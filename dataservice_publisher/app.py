"""Package for making catalog of dataservices available in an API."""
import logging
import os
from typing import Any

from aiohttp import hdrs, web
from aiohttp_middlewares import cors_middleware, error_middleware
from dotenv import load_dotenv
import jwt
from multidict import MultiDict

from .resources.catalogs import Catalog, Catalogs
from .resources.login import Login
from .resources.ping import Ping
from .resources.ready import Ready


load_dotenv()
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
CONFIG = os.getenv("CONFIG", "production")
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = "HS256"


async def authenticated(request: web.Request) -> bool:
    """For relevant methods and paths, check if the user is authenticated."""
    # All read methods are allowed without authentication.
    if request.method in ["OPTIONS", "GET", "HEAD"] or request.path == "/login":
        return True
    # Extract jwt_token from authorization header in request
    logging.debug("Verifying authorization token")

    authorization = request.headers.getone(hdrs.AUTHORIZATION, None)
    if authorization:
        logging.debug(f"Got authorization header: {authorization}")
        jwt_token = str.replace(str(authorization), "Bearer ", "")
        try:
            jwt.decode(jwt_token, SECRET_KEY, algorithms=[JWT_ALGORITHM])  # type: ignore
        except (jwt.DecodeError, jwt.ExpiredSignatureError) as e:
            logging.debug(f"Got exception decoding jwt: {e}")
            return False
        return True
    logging.debug("Got NO auhtorization header!")
    return False


@web.middleware
async def content_negotiation_middleware(
    request: web.Request, handler: Any
) -> web.Response:
    """Middleware to check if we can respond in accordance to the user's accept-header."""
    logging.debug("content_negotiation_middleware called")

    if not request.headers.getone(hdrs.ACCEPT, None):
        pass  # pragma: no cover
    elif "catalogs" in request.path:
        content_types = (
            ",".join(request.headers.getall(hdrs.ACCEPT)).replace(" ", "").split(",")
        )
        if "text/turtle" in content_types:
            pass
        elif "application/ld+json" in content_types:
            pass
        elif "application/rdf+xml" in content_types:
            pass
        elif "application/n-triples" in content_types:
            pass
        elif "*/*" in content_types:
            pass
        else:
            raise web.HTTPNotAcceptable()

    response = await handler(request)
    logging.debug("content_negotiation_middleware finished")
    return response


@web.middleware
async def authenticate_middleware(request: web.Request, handler: Any) -> web.Response:
    """Middleware to check if the user is authenticated."""
    logging.debug("authenticate_middleware called")

    if not await authenticated(request):
        headers = MultiDict([(hdrs.WWW_AUTHENTICATE, 'Bearer token_type="JWT"')])

        raise web.HTTPUnauthorized(headers=headers)

    response = await handler(request)
    logging.debug("authenticate_middleware finished")
    return response


async def create_app() -> web.Application:
    """Create and configure the app."""
    app = web.Application(
        middlewares=[
            cors_middleware(allow_all=True),
            content_negotiation_middleware,
            authenticate_middleware,
            error_middleware(),  # default error handler for whole application
        ]
    )

    # Routes
    app.add_routes(
        [
            web.view("/login", Login),
            web.view("/ping", Ping),
            web.view("/ready", Ready),
            web.view("/catalogs", Catalogs),
            web.view("/catalogs/{id}", Catalog),
        ]
    )
    # logging configurataion:
    logging.basicConfig(
        format="%(asctime)s,%(msecs)d %(levelname)s - %(module)s:%(lineno)d: %(message)s",
        datefmt="%H:%M:%S",
        level=LOGGING_LEVEL,
    )
    logging.getLogger("chardet.charsetprober").setLevel(LOGGING_LEVEL)

    return app
