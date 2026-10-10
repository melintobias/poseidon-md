"""Configure level-aware Rich logging for the command-line interface."""

import logging

from rich.console import Console
from rich.logging import RichHandler

from .styles import THEME

CONSOLE = Console(theme=THEME)
"""Shared console configured with the Poseidon-MD terminal theme."""

LOGGER = logging.getLogger("poseidon_md_cli")
"""Shared application logger used by the command-line pipeline."""

RICH_HANDLER = RichHandler(
    console=CONSOLE,
    markup=False,
    rich_tracebacks=True,
    show_path=False,
    show_time=True,
    log_time_format="%H:%M:%S",
)
"""Rich terminal handler responsible for rendering application log records."""

LOGGER.addHandler(RICH_HANDLER)
LOGGER.propagate = False


def configure_logger(*, debug: bool = False) -> logging.Logger:
    """Configure and return the shared application logger.

    Args:
        debug: Whether to include diagnostic debug records.

    Returns:
        The configured shared application logger.
    """

    LOGGER.setLevel(logging.INFO if not debug else logging.DEBUG)
    return LOGGER
