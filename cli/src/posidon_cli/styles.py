"""Define the shared Rich theme and console for the command-line interface."""

from rich.theme import Theme

TITLE = "posidon.title"
"""Theme style name for prominent titles and branded highlights."""

BORDER = "posidon.border"
"""Theme style name for borders around tables and panels."""

HEADING = "posidon.heading"
"""Theme style name for headings inside structured output."""

EMPHASIS = "posidon.emphasis"
"""Theme style name for text requiring neutral emphasis."""

SUCCESS = "posidon.success"
"""Theme style name for successful outcomes."""

SUCCESS_DETAIL = "posidon.success.detail"
"""Theme style name for secondary successful-outcome details."""

WARNING = "posidon.warning"
"""Theme style name for warnings and non-fatal exceptional outcomes."""

WARNING_DETAIL = "posidon.warning.detail"
"""Theme style name for secondary warning details."""

ERROR = "posidon.error"
"""Theme style name for failed or rejected outcomes."""

ERROR_TEXT = "posidon.error.text"
"""Theme style name for content associated with an error."""

ERROR_DETAIL = "posidon.error.detail"
"""Theme style name for secondary error details."""

THEME = Theme({
    # TITLE highlights prominent titles and branded content.
    TITLE: "bold white",
    # BORDER gives structured components a consistent outline.
    BORDER: "cyan",
    # HEADING distinguishes column and section headings.
    HEADING: "bold white",
    # EMPHASIS highlights important text without status semantics.
    EMPHASIS: "bold",
    # SUCCESS identifies accepted and completed outcomes.
    SUCCESS: "bold green",
    # SUCCESS_DETAIL de-emphasizes supporting success information.
    SUCCESS_DETAIL: "green",
    # WARNING identifies duplicate or cautionary outcomes.
    WARNING: "bold yellow",
    # WARNING_DETAIL styles supporting warning information.
    WARNING_DETAIL: "yellow",
    # ERROR identifies invalid or failed outcomes.
    ERROR: "bold red",
    # ERROR_TEXT marks the content responsible for an error.
    ERROR_TEXT: "red",
    # ERROR_DETAIL de-emphasizes supporting error information.
    ERROR_DETAIL: "red",
})
"""Shared semantic theme for all Posidon terminal output."""
