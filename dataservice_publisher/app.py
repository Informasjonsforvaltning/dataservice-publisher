"""Package for making catalog of dataservices available in an API."""
import logging
import os
from typing import Any, Dict, List, Optional

from aiohttp import hdrs, web
from aiohttp_middlewares import cors_middleware, error_middleware
from dotenv import load_dotenv
import jwt
from multidict import MultiDict

from .resources.catalogs import Catalog, Catalogs
from .resources.login import Login
from .resources.ping import Ping
from .resources.ready import Ready

DEFAULT_CONTENT_TYPE = {"text": "text/turtle", "application": "application/ld+json"}
SUPPORTED_CONTENT_TYPES = [
    "text/turtle",
    "application/ld+json",
    "application/rdf+xml",
    "application/n-triples",
]

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


async def prepare_mime_types(accept_mime_types: List[str]) -> List[str]:
    """Prepare the accept mime types and sort on q-parameter."""
    logging.debug(f"Prcoessing accept mime types: {accept_mime_types}")
    # Assign q-parameter:
    accept_mime_types_sorted: List[Dict[str, str]] = []
    for mime_type in accept_mime_types:
        mime_type_split = mime_type.split(";")
        mime_type_with_q = {
            "type": mime_type_split[0],
            "q": "1",
        }
            for mime_type_part in mime_type_split[1:]:

                if mime_type_part.startswith("q="):
                    mime_type_with_q = {
                        "type": mime_type_split[0],
                        "q": mime_type_part[2:],
                    }

            accept_mime_types_sorted.append(mime_type_with_q)

    # Adjust q-parameters with regard to specificity:
    for mime_type_with_q in accept_mime_types_sorted:
        if mime_type_with_q["type"].split("/")[0] == "*":
            pass
        elif mime_type_with_q["type"].split("/")[1] == "*":
            mime_type_with_q["q"] = str(float(mime_type_with_q["q"]) * 10)
        else:
            mime_type_with_q["q"] = str(float(mime_type_with_q["q"]) * 100)

    # Sort on q-parameter:
    accept_mime_types_sorted.sort(key=lambda x: x["q"], reverse=True)
    logging.debug(f"Prcoessing accept mime types sorted: {accept_mime_types_sorted}")
    return [mime_type_dict["type"] for mime_type_dict in accept_mime_types_sorted]


async def decide_content_type(request: web.Request) -> Optional[str]:
    """Decide the content type of the response."""
    logging.debug("Deciding content type")
    if not request.headers.getone(hdrs.ACCEPT, None):
        content_type = DEFAULT_CONTENT_TYPE["text"]  # pragma: no cover
    elif "catalogs" in request.path:
        accept_mime_types: List[str] = (
            ",".join(request.headers.getall(hdrs.ACCEPT)).replace(" ", "").split(",")
        )
        accept_mime_types_sorted = await prepare_mime_types(accept_mime_types)
        for mime_type in accept_mime_types_sorted:
            logging.debug(f"Processing mime type: {mime_type}")
            if mime_type in SUPPORTED_CONTENT_TYPES:
                content_type = mime_type
                break
            elif mime_type == "*/*":
                content_type = DEFAULT_CONTENT_TYPE["text"]
                break
            elif mime_type == "text/*":
                content_type = DEFAULT_CONTENT_TYPE["text"]
                break
            elif mime_type == "application/*":
                content_type = DEFAULT_CONTENT_TYPE["application"]
                break
            else:
                content_type = None
    else:
        content_type = "application/json"
    return content_type


@web.middleware
async def content_negotiation_middleware(
    request: web.Request, handler: Any
) -> web.Response:
    """Middleware to check if we can respond in accordance to the user's accept-header."""
    logging.debug("content_negotiation_middleware called")
    content_type = await decide_content_type(request)
    if content_type:
        request.app["content_type"] = content_type
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
