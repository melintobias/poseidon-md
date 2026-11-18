"""CLI option definitions shared by the command and pipeline stages."""

from dataclasses import dataclass
from dataclasses import fields
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typer import Context

OUTPUT_DIR_OPTION = "--output-dir"
"""Long flag choosing the directory that receives finished audio files.

Warnings about a missing output directory name this flag, so it is shared with
the command definition to keep both in sync.
"""


class OutputFormat(StrEnum):
    """Audio formats the CLI can produce and tag."""

    MP3 = "mp3"
    """MPEG Layer III audio with ID3 metadata."""


@dataclass(frozen=True, slots=True, kw_only=True)
class CliOptions:
    """Command settings available to pipeline stages.

    Attributes:
        urls: Source URLs supplied on the command line or at the prompt.
        debug: Whether diagnostic logging is enabled.
        no_prompt: Whether to exit when no URLs were supplied.
        output_format: Audio format produced by retrieval and used for tagging.
        output_dir: Directory chosen to receive finished audio files, or `None`
            to use the platform's music directory. The path may not exist;
            intake then falls back to the working directory.
    """

    urls: list[str] | None = None

    debug: bool = False
    no_prompt: bool = False
    output_format: OutputFormat = OutputFormat.MP3
    output_dir: Path | None = None

    def __post_init__(self) -> None:
        """Convert the raw output format and directory from Typer to models.

        Typer keeps raw values in `Context.params`, so options built from the
        context receive the format's value instead of a member and the output
        directory as a string instead of a path.

        Raises:
            ValueError: If the output format is unsupported.
        """
        object.__setattr__(
            self, "output_format", OutputFormat(self.output_format)
        )
        if self.output_dir is not None:
            object.__setattr__(self, "output_dir", Path(self.output_dir))

    @staticmethod
    def get_context_options(ctx: Context) -> CliOptions:
        """Convert parsed Typer parameters to pipeline options.

        Args:
            ctx: Context containing parsed command parameters.

        Returns:
            Options built from the parameters that match option fields.
        """
        names = {item.name for item in fields(CliOptions)}
        values = {
            name: value for name, value in ctx.params.items() if name in names
        }

        return CliOptions(**values)


DEFAULT_CLI_OPTIONS = CliOptions()
"""Default settings shown and applied by the CLI."""
