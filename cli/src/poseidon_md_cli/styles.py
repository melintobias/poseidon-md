"""Define the shared Rich theme and console for the command-line interface."""

from rich.theme import Theme

TITLE = "poseidon.title"
"""Theme style name for prominent titles and branded highlights."""

BORDER = "poseidon.border"
"""Theme style name for borders around tables and panels."""

HEADING = "poseidon.heading"
"""Theme style name for headings inside structured output."""

EMPHASIS = "poseidon.emphasis"
"""Theme style name for text requiring neutral emphasis."""

SUCCESS = "poseidon.success"
"""Theme style name for successful outcomes."""

SUCCESS_DETAIL = "poseidon.success.detail"
"""Theme style name for secondary successful-outcome details."""

WARNING = "poseidon.warning"
"""Theme style name for warnings and non-fatal exceptional outcomes."""

WARNING_DETAIL = "poseidon.warning.detail"
"""Theme style name for secondary warning details."""

ERROR = "poseidon.error"
"""Theme style name for failed or rejected outcomes."""

ERROR_TEXT = "poseidon.error.text"
"""Theme style name for content associated with an error."""

ERROR_DETAIL = "poseidon.error.detail"
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
"""Shared semantic theme for all Poseidon-MD terminal output."""
