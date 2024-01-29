"""Repository module for ping."""

from aiohttp import web


class Ping(web.View):
    """Class representing ping resource."""

    async def get(self) -> web.Response:
        """Ping route function."""
        return web.Response(text="OK")
