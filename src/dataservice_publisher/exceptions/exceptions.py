"""Exeptions module for dataservice-publisher."""
from typing import Optional


class RequestBodyError(Exception):
    """Base class for exceptions."""

    def __init__(self, msg: Optional[str] = None) -> None:
        """Inits the exception."""
        Exception.__init__(self, msg)
        self.msg = msg
