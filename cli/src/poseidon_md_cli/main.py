"""Define the Poseidon-MD command-line entry point."""

from __future__ import annotations

from typing import Annotated

from typer import Argument
from typer import Context
from typer import Option
from typer import Typer

from .logger import get_logger
from .options import CliOptions
from .options import DEFAULT_CLI_OPTIONS
from .pipeline import IntakeStage
from .pipeline import MovingStage
from .pipeline import PipelineStage
from .pipeline.retrieval import RetrievalStage
from .pipeline.tagging import TaggingStage
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
    ctx: Context,
    urls: Annotated[list[str] | None, Argument()] = None,  # noqa: ARG001
    *,
    debug: Annotated[
        bool, Option("--debug", "-d", help="Show diagnostic logging.")
    ] = DEFAULT_CLI_OPTIONS.debug,
    no_prompt: Annotated[  # noqa: ARG001
        bool,
        Option(
            "--no-prompt",
            help="Exit when no URLs are provided, instead of prompting for "
            "input.",
        ),
    ] = DEFAULT_CLI_OPTIONS.no_prompt,
) -> None:
    """Process the supplied media URLs through the Poseidon pipeline.

    Args:
        ctx: Typer command context.
        urls: Source URLs to process.
        debug: Whether to include diagnostic debug records.
        no_prompt: Whether to exit when no URLs are provided, instead of
            prompting for input.
    """
    storage = PipelineSharedStorage(
        options=CliOptions.get_context_options(ctx),
        logger=get_logger(debug=debug),
    )
    orchestrator = StageOrchestrator(stages, storage)
    orchestrator.run()


if __name__ == "__main__":
    app()
