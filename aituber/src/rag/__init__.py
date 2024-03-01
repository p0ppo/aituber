from .database import *
from .vectorize import vectorize


def get_db(identifier):
    """Returns a database function from a string (case-insensitive).

    Args:
        identifier (str): the handler name.

    Returns:
        :func:
    """
    if isinstance(identifier, str):
        to_get = {k.lower(): v for k, v in globals().items()}
        func = to_get.get(identifier.lower())
        if func is None:
            raise ValueError(f"Could not interpret memory handler name : {str(identifier)}")
        return func
    raise ValueError(f"Could not interpret memory handler name : {str(identifier)}")