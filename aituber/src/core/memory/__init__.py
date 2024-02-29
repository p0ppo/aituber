from .memory_handler import SimpleMemoryHandler, LangchainMemoryHandler

__all__ = [
    "SimpleMemoryHandler",
    "LangchainMemoryHandler",
]

memory_handler_alias = {
    "simple": "SimpleMemoryHandler",
    "langchain": "LangchainMemoryHandler",
}


def make_memory_handler(handler):
    """

    Args:
        handler (str): Identifier understood
            by :func:`~.get`.
        **kwargs (dict): keyword arguments for the handler.

    Returns:
        MemoryHandler
    Examples
        >>> handler = make_memory_handler(handler='langchain')
    """
    return get(handler)()


def get(identifier):
    """Returns a memory handler class from a string (case-insensitive).

    Args:
        identifier (str): the handler name.

    Returns:
        :class:`MemoryHandler`
    """
    if isinstance(identifier, str):
        to_get = {k.lower(): v for k, v in globals().items()}
        cls_name = memory_handler_alias[identifier.lower()]
        cls = to_get.get(cls_name.lower())
        if cls is None:
            raise ValueError(f"Could not interpret memory handler name : {str(identifier)}")
        return cls
    raise ValueError(f"Could not interpret memory handler name : {str(identifier)}")