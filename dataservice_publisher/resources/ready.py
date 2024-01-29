"""Repository module for ready."""

import logging
from os import environ as env
from typing import Any

from aiohttp import ClientConnectionError, ClientSession
from aiohttp import web
from dotenv import load_dotenv

# Get environment
load_dotenv()
FUSEKI_HOST = env.get("FUSEKI_HOST", "http://fuseki")
FUSEKI_PORT = int(env.get("FUSEKI_PORT", 8080))


class Ready(web.View):
    """Class representing ready resource."""

    async def get(self) -> Any:
        """Ready route function."""
        url = f"{FUSEKI_HOST}:{FUSEKI_PORT}/fuseki/$/ping"
        try:
            # Get ready status from fuseki
            async with ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return web.Response(text="OK")
        except ClientConnectionError as e:
            logging.critical(f"Got exception from {url}: {type(e)}\n{e}.")
            pass
        return web.Response(status=500)
