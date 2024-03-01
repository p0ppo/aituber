from .ff14_scraper import FF14Scraper


__all__ = [
    "FF14Scraper",
]

scraper_alias = {
    "ff14": "FF14Scraper",
}


def get_scraper(identifier):
    """Returns a scraper class from a string (case-insensitive).

    Args:
        identifier (str): the scraper name.

    Returns:
        :class:`Scraper`
    """
    if isinstance(identifier, str):
        to_get = {k.lower(): v for k, v in globals().items()}
        cls_name = scraper_alias[identifier.lower()]
        cls = to_get.get(cls_name.lower())
        if cls is None:
            raise ValueError(f"Could not interpret scraper name : {str(identifier)}")
        return cls
    raise ValueError(f"Could not interpret scraper name : {str(identifier)}")