"""Define the Poseidon-MD command-line entry point."""

from typing import Annotated

from typer import Argument
from typer import Option
from typer import Typer

from poseidon_md_cli.pipeline.retrieval import RetrievalStage
from poseidon_md_cli.pipeline.tagging import TaggingStage

from .logger import get_logger
from .pipeline import IntakeStage
from .pipeline import MovingStage
from .pipeline import PipelineStage
from .pipeline.types import PipelineSharedStorage
from .pipeline.types import StageOrchestrator

app = Typer()
"""Typer application exposed by the `poseidon-md` command."""

stages: list[type[PipelineStage]] = [
    IntakeStage,
    RetrievalStage,
    TaggingStage,
    MovingStage,
]
"""Ordered pipeline stages run by the command-line application."""


@app.command()
def main(
    urls: Annotated[list[str] | None, Argument()] = None,
    *,
    debug: Annotated[
        bool, Option("--debug", "-d", help="Show diagnostic logging.")
    ] = False,
    no_prompt: Annotated[
        bool,
        Option(
            "--no-prompt",
            help="Exit when no URLs are provided, instead of prompting for "
            "input.",
        ),
    ] = False,
) -> None:
    """Process the supplied media URLs through the Poseidon pipeline.

    Args:
        urls: Source URLs to process.
        debug: Whether to include diagnostic debug records.
        no_prompt: Whether to exit when no URLs are provided, instead of
            prompting for input.
    """
    storage = PipelineSharedStorage(
        logger=get_logger(debug=debug),
        input_urls=urls or [],
        no_prompt=no_prompt,
    )
    orchestrator = StageOrchestrator(stages, storage)
    orchestrator.run()


if __name__ == "__main__":
    app()
