"""CLI option dataclass."""

from dataclasses import dataclass
from dataclasses import fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typer import Context


@dataclass(frozen=True, slots=True, kw_only=True)
class CliOptions:
    """Command settings available to pipeline stages.

    Attributes:
        urls: Source URLs supplied on the command line or at the prompt.
        debug: Whether diagnostic logging is enabled.
        no_prompt: Whether to exit when no URLs were supplied.
    """

    urls: list[str] | None = None

    debug: bool = False
    no_prompt: bool = False

    @staticmethod
    def get_context_options(ctx: Context) -> CliOptions:
        """Convert parsed Typer parameters to pipeline options.

        Args:
            ctx: Context containing parsed command parameters.

        Returns:
            Options with URL arguments stored as an immutable tuple.
        """
        names = {item.name for item in fields(CliOptions)}
        values = {
            name: value for name, value in ctx.params.items() if name in names
        }

        return CliOptions(**values)


DEFAULT_CLI_OPTIONS = CliOptions()
"""Default settings shown and applied by the CLI."""
