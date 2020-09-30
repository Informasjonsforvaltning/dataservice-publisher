"""Exeptions module for dataservice-publisher."""


class ErrorInRequstBodyException(Exception):
    """Base class for exceptions."""

    def __init__(self, msg: str = None) -> None:
        """Inits the exception."""
        Exception.__init__(self, msg)
        self.msg = msg
