"""Configure level-aware Rich logging for the command-line interface."""

import logging

from rich.console import Console
from rich.logging import RichHandler

from .styles import THEME


class DebugTracebackFilter(logging.Filter):
    """Suppress exception tracebacks unless debug logging is enabled.

    Attributes:
        debug: Whether exception details and tracebacks should be retained.
    """

    def __init__(self) -> None:
        """Initialize the filter with exception tracebacks disabled."""
        super().__init__()
        self.debug = False

    def filter(self, record: logging.LogRecord) -> bool:
        """Keep a record and remove its exception details outside debug mode.

        Args:
            record: Log record to inspect and optionally update.

        Returns:
            Always `True`, since this filter changes traceback visibility but
            doesn't discard log records.
        """
        if not self.debug:
            record.exc_info = None
            record.exc_text = None

        return True


DEBUG_TRACEBACK_FILTER = DebugTracebackFilter()
"""Shared filter controlling traceback visibility for the CLI logger."""

CONSOLE = Console(theme=THEME)
"""Shared console configured with the Poseidon-MD terminal theme."""

LOGGER = logging.getLogger("poseidon_md_cli")
"""Shared application logger used by the command-line pipeline."""

RICH_HANDLER = RichHandler(
    console=CONSOLE,
    markup=False,
    rich_tracebacks=False,
    show_path=False,
    show_time=True,
    log_time_format="%H:%M:%S",
)
"""Rich terminal handler responsible for rendering application log records."""

LOGGER.addHandler(RICH_HANDLER)
LOGGER.propagate = False
RICH_HANDLER.addFilter(DEBUG_TRACEBACK_FILTER)


def get_logger(*, debug: bool = False) -> logging.Logger:
    """Configure and return the shared application logger.

    Args:
        debug: Whether to include diagnostic debug records and exception
            tracebacks.

    Returns:
        The configured shared application logger.
    """
    LOGGER.setLevel(logging.INFO if not debug else logging.DEBUG)
    DEBUG_TRACEBACK_FILTER.debug = debug
    RICH_HANDLER.rich_tracebacks = debug
    return LOGGER


def log_stage_completion(
    logger: logging.Logger,
    level: int,
    message: object,
    *args: object,
) -> None:
    """Log a stage outcome and separate it from following terminal output.

    The supplied logger retains control of the message level and formatting; the
    shared Rich console then draws a horizontal rule after the log record.

    Args:
        logger: Application logger used for the completion record.
        level: Numeric logging level chosen for the stage outcome.
        message: Logging format string or message object.
        *args: Values interpolated into the message using logging's formatting.
    """
    logger.log(level, message, *args)
    CONSOLE.rule()
