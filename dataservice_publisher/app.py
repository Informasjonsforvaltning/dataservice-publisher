"""Package for making catalog of dataservices available in an API."""
import logging
import os
from typing import Any, List, Optional

from aiohttp import hdrs, web
from aiohttp_middlewares import cors_middleware, error_middleware
from dotenv import load_dotenv
import jwt
from multidict import MultiDict

from .resources.catalogs import Catalog, Catalogs
from .resources.login import Login
from .resources.ping import Ping
from .resources.ready import Ready

DEFAULT_CONTENT_TYPE = {"text": "text/turtle", "application": "application/rdf+xml"}
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


class WeightedMediaRange:
    """Class for handling weighted media ranges."""

    def __init__(self, type: str, q: float = 1.0) -> None:
        """Initialize the weighted media range."""
        self.type = type.split("/")[0]
        self.sub_type = type.split("/")[1]
        self.q = q

    def __eq__(self, other: Any) -> bool:  # pragma: no cover
        """Compare two weighted media ranges."""
        if isinstance(other, str):
            return f"{self.type}/{self.sub_type}" == other
        if isinstance(other, WeightedMediaRange):
            return self.type == other.type and self.sub_type == other.sub_type
        return False

    def __str__(self) -> str:
        """Return the weighted media range as a string."""
        return f"{self.type}/{self.sub_type};q={self.q}"

    def media_range(self) -> str:
        """Return the media range."""
        return f"{self.type}/{self.sub_type}"


async def prepare_weighted_media_ranges(
    accept_weighted_media_ranges: List[str],
) -> List[str]:
    """Prepare the accept weighted media ranges and sort on q-parameter."""
    logging.debug(
        f"Preparing accept weighted media ranges: {accept_weighted_media_ranges}"
    )
    # Assign q-parameter:
    accept_weighted_media_ranges_sorted: List[WeightedMediaRange] = []

    for accept_weighted_media_range in accept_weighted_media_ranges:
        weighted_media_range_split = accept_weighted_media_range.split(";")
        # Instantiate weighted media range:
        try:
            weighted_media_range = WeightedMediaRange(weighted_media_range_split[0])
            logging.debug(
                f"Assigning q-parameter for weighted media range: {accept_weighted_media_range}"
            )
            # If q-parameter is present, assign it:
            for weighted_media_range_part in weighted_media_range_split[1:]:
                if weighted_media_range_part.startswith("q="):
                    weighted_media_range.q = float(
                        weighted_media_range_part.split("=")[1][0:5]
                    )

            accept_weighted_media_ranges_sorted.append(weighted_media_range)
        except IndexError:
            logging.debug(
                "Ignoring invalid weighted media range: %s", accept_weighted_media_range
            )
            pass  # ignore invalid media range

    # Adjust q-parameters with regard to specificity:
    # Highest q-parameter is the most specific:
    for weighted_media_range in accept_weighted_media_ranges_sorted:
        logging.debug(
            f"Ajusting q-parameter for weighted media range: {weighted_media_range}"
        )
        if weighted_media_range.type == "*":
            pass
        elif weighted_media_range.sub_type == "*":
            weighted_media_range.q = weighted_media_range.q + 0.0001
        else:
            weighted_media_range.q = weighted_media_range.q + 0.0002

    # Sort on q-parameter and return list of weighted media ranges:
    accept_weighted_media_ranges_sorted.sort(key=lambda x: x.q, reverse=True)
    logging.debug(
        f"Accept weighted media ranges sorted: {', '.join(str(p) for p in accept_weighted_media_ranges_sorted)}"  # noqa: B950
    )
    return [
        str(weighted_media_range.media_range())
        for weighted_media_range in accept_weighted_media_ranges_sorted
    ]


async def decide_content_type(request: web.Request) -> Optional[str]:
    """Decide the content type of the response."""
    logging.debug("Deciding content type")
    content_type = None
    if hdrs.ACCEPT not in request.headers:
        content_type = DEFAULT_CONTENT_TYPE["text"]  # pragma: no cover
    elif "catalogs" in request.path:
        accept_weighted_media_ranges: List[str] = (
            ",".join(request.headers.getall(hdrs.ACCEPT)).replace(" ", "").split(",")
        )
        accept_weighted_media_ranges_sorted = await prepare_weighted_media_ranges(
            accept_weighted_media_ranges
        )
        for weighted_media_range in accept_weighted_media_ranges_sorted:
            logging.debug(f"Checking weighted media range: {weighted_media_range}")
            if weighted_media_range in SUPPORTED_CONTENT_TYPES:
                content_type = weighted_media_range
                break
            elif weighted_media_range == "*/*":
                content_type = DEFAULT_CONTENT_TYPE["text"]
                break
            else:
                # Assumes valid mimetypes from `prepare_mime_types`
                media_range_type, media_range_subtype = weighted_media_range.split("/")
                if (
                    media_range_subtype == "*"
                    and media_range_type in DEFAULT_CONTENT_TYPE
                ):
                    content_type = DEFAULT_CONTENT_TYPE[media_range_type]
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
