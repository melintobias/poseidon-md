"""Define the Poseidon-MD command-line entry point."""

from typing import Annotated

from poseidon_md_core.adapters import YtDlpSourceAcquirer
import typer

from .logger import configure_logger
from .pipeline import ExtractionStage
from .pipeline import IntakeStage
from .pipeline import PipelineStage
from .pipeline.types import PipelineSharedStorage
from .pipeline.types import StageOrchestrator

app = typer.Typer()
"""Typer application exposed by the `poseidon-md` command."""

stages: list[type[PipelineStage]] = [
    IntakeStage,
    ExtractionStage,
]
"""Ordered pipeline stages run by the command-line application."""


@app.command()
def main(
    urls: Annotated[list[str] | None, typer.Argument()] = None,
    debug: Annotated[
        bool,
        typer.Option("--debug", "-d", help="Show diagnostic logging."),
    ] = False,
    welcome: Annotated[
        bool,
        typer.Option(
            "--welcome",
            help="Show a welcome message when no URLs are provided.",
        ),
    ] = True,
) -> None:
    """Process the supplied media URLs through the Poseidon pipeline.

    Args:
        urls: Source URLs to process.
        debug: Whether to include diagnostic debug records.
        welcome: Whether to show a welcome message when no URLs are
            provided.
    """

    shared_storage = PipelineSharedStorage(
        logger=configure_logger(debug=debug),
        input_urls=urls or [],
        welcome_on_no_urls=welcome,
        source_acquirer=YtDlpSourceAcquirer(),
    )
    orchestrator = StageOrchestrator(stages, shared_storage=shared_storage)
    orchestrator.run()


if __name__ == "__main__":
    app()
