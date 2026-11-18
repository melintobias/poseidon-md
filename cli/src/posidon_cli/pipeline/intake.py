"""Validate the URLs and output directory entering the CLI pipeline."""

from dataclasses import replace
from logging import CRITICAL
from logging import DEBUG
from logging import INFO
from logging import WARNING
from pathlib import Path
from typing import TYPE_CHECKING

from posidon_core.models import Track
from posidon_core.pipeline.intake import validate_url
from rich.progress import track
from rich.prompt import Prompt

from posidon_cli.directories import get_music_directory
from posidon_cli.logger import CONSOLE
from posidon_cli.logger import log_stage_completion
from posidon_cli.options import OUTPUT_DIR_OPTION

from .types import PipelineSharedStorage
from .types import PipelineStage
from .types import StageOrchestrator

if TYPE_CHECKING:
    from pydantic import AnyUrl

_MISSING_OUTPUT_DIRECTORY = (
    "Output directory %r does not exist; saving tracks to the current "
    "directory %r instead. Pass an existing directory with %s."
)
"""Warning for a missing directory chosen on the command line.

Formatted with the chosen directory, the working directory, and the option.
"""

_MISSING_MUSIC_DIRECTORY = (
    "Music directory %r was not found; saving tracks to the current "
    "directory %r instead. Choose a directory with %s."
)
"""Warning for a missing default music directory.

Formatted with the music directory, the working directory, and the option.
"""


class IntakeStage(PipelineStage):
    """Coordinate the URL and output directory checks performed at intake."""

    @classmethod
    def run(cls, storage: PipelineSharedStorage) -> None:
        """Run all intake steps against shared pipeline storage.

        Args:
            storage: Existing pipeline storage for this run.

        Raises:
            SystemExit: If no input URLs are provided and the `no_prompt` option
                is set.
        """
        options = storage.options
        if options.no_prompt and not options.urls:
            storage.logger.info("No input URLs provided; exiting.")
            raise SystemExit(0)

        StageOrchestrator(
            [
                InputSubStage,
                UrlValidationSubStage,
                TrackCreationSubStage,
                OutputDirectorySubStage,
            ],
            storage,
        ).run()


class InputSubStage(PipelineStage):
    """Prompt for input URLs if none were supplied on the command line."""

    @classmethod
    def run(cls, storage: PipelineSharedStorage) -> None:
        """Prompt for input URLs if none were supplied on the command line."""
        options = storage.options
        if options.urls:
            return

        welcome()

        storage.logger.debug("No input URLs provided; prompting for input.")
        urls = Prompt.ask("Please enter URLs separated by spaces")

        storage.options = replace(storage.options, urls=tuple(urls.split()))


class UrlValidationSubStage(PipelineStage):
    """Validate and deduplicate supplied URLs."""

    @classmethod
    def run(cls, storage: PipelineSharedStorage) -> None:
        """Store valid URLs.

        Args:
            storage: Pipeline storage containing the input URLs and
                receiving the validated URL set.

        Raises:
            SystemExit: If all input URLs are invalid.
        """
        logger = storage.logger
        input_urls = storage.options.urls or ()

        validated_urls: list[AnyUrl] = []
        total_urls = len(input_urls)
        total_unique_urls = len(set(input_urls))

        logger.info("URL validation started (%d URLs)", total_urls)

        tracked_urls = track(
            input_urls, description="URL validation", console=CONSOLE
        )
        for index, url in enumerate(tracked_urls, start=1):
            logger.debug("%d/%d Validating: %s", index, total_urls, url)

            if (validated_url := validate_url(url)) is None:
                logger.error(
                    "%d/%d Invalid URL skipped: %s", index, total_urls, url
                )
                continue

            if validated_url in validated_urls:
                logger.warning(
                    "%d/%d Duplicate URL skipped: %s",
                    index,
                    total_urls,
                    validated_url,
                )
                continue

            validated_urls.append(validated_url)
            logger.info("%d/%d Valid URL: %s", index, total_urls, validated_url)

        storage.urls = tuple(validated_urls)

        total_success = len(validated_urls) == total_unique_urls
        total_failure = len(validated_urls) == 0 and total_unique_urls > 0

        if total_success:
            level = INFO
        elif total_failure:
            level = CRITICAL
        else:
            level = WARNING

        log_stage_completion(
            logger,
            level,
            "URL validation completed (%d/%d unique URLs valid)",
            len(validated_urls),
            total_unique_urls,
        )

        if total_failure:
            logger.critical(
                "All %d unique URLs were invalid; exiting.", total_unique_urls
            )
            raise SystemExit(1)


class TrackCreationSubStage(PipelineStage):
    """Create track objects from URLs accepted by validation."""

    @classmethod
    def run(cls, storage: PipelineSharedStorage) -> None:
        """Create `Track` objects for each validated URL.

        Args:
            storage: Pipeline storage containing the validated URLs and
                receiving the created Track objects.
        """
        logger = storage.logger

        tracks: list[Track] = []
        total_urls = len(storage.urls)

        logger.debug("Track creation started (%d URLs)", total_urls)

        for index, url in enumerate(storage.urls, start=1):
            logger.debug("%d/%d Creating Track for: %s", index, total_urls, url)

            track = Track(url=url)
            tracks.append(track)

            logger.debug("%d/%d Track created: %s", index, total_urls, track)

        storage.tracks = tuple(tracks)

        log_stage_completion(
            logger,
            DEBUG,
            "Track creation completed (%d/%d Tracks created)",
            len(tracks),
            total_urls,
        )


class OutputDirectorySubStage(PipelineStage):
    """Choose the existing directory that receives finished audio files."""

    @classmethod
    def run(cls, storage: PipelineSharedStorage) -> None:
        """Store the chosen or default output directory, or the fallback.

        A directory chosen with the output directory option takes precedence
        over the platform's music directory. If the selected directory doesn't
        exist, a warning specific to its source names it and the option, and
        the current working directory is used instead.

        Args:
            storage: Pipeline storage containing the command options and
                receiving the output directory.
        """
        logger = storage.logger

        if storage.options.output_dir is not None:
            directory = storage.options.output_dir
            missing_warning = _MISSING_OUTPUT_DIRECTORY
        else:
            directory = get_music_directory()
            missing_warning = _MISSING_MUSIC_DIRECTORY

        if not directory.is_dir():
            fallback = Path.cwd()
            logger.warning(
                missing_warning,
                str(directory),
                str(fallback),
                OUTPUT_DIR_OPTION,
            )
            directory = fallback

        storage.output_directory = directory

        log_stage_completion(
            logger, DEBUG, "Output directory selected: %r", str(directory)
        )


def welcome() -> None:
    """Render a welcome message to the console."""
    # TODO: Improve welcome message
    CONSOLE.print("[bold green]Welcome to Posidon![/bold green]\n")
