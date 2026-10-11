"""Validate source URLs before they enter the media pipeline."""

from pydantic import AnyUrl


def validate_url(url: str) -> AnyUrl | None:
    """Parse an HTTP URL, returning `None` when Pydantic rejects the input.

    Args:
        url: Raw source URL supplied by the caller.

    Returns:
        A parsed URL for valid input, or `None` for invalid input.
    """
    try:
        return AnyUrl(url)
    except ValueError:
        return None
