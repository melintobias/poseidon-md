"""Validate, deduplicate, and report URLs entering the CLI pipeline."""

from logging import CRITICAL
from logging import DEBUG
from logging import INFO
from logging import WARNING
from typing import TYPE_CHECKING

from poseidon_md_core.models import Track
from poseidon_md_core.pipeline.intake import validate_url
from rich.progress import track
from rich.prompt import Prompt

from poseidon_md_cli.logger import CONSOLE
from poseidon_md_cli.logger import log_stage_completion

from .types import PipelineSharedStorage
from .types import PipelineStage
from .types import StageOrchestrator

if TYPE_CHECKING:
    from pydantic import AnyUrl


class IntakeStage(PipelineStage):
    """Coordinate the URL validation work performed during intake."""

    @classmethod
    def run(cls, storage: PipelineSharedStorage | None = None) -> None:
        """Run all URL intake steps against shared pipeline storage.

        Args:
            storage: Existing pipeline storage, or `None` to create
                empty storage for this run.

        Raises:
            SystemExit: If no input URLs are provided and the `no_prompt` option
                is set.
        """
        if storage and storage.no_prompt and not storage.input_urls:
            storage.logger.info("No input URLs provided; exiting.")
            raise SystemExit(0)

        StageOrchestrator(
            [InputSubStage, UrlValidationSubStage, TrackCreationSubStage],
            storage,
        ).run()


class InputSubStage(PipelineStage):
    """Prompt for input URLs if none were supplied on the command line."""

    @classmethod
    def run(cls, storage: PipelineSharedStorage) -> None:
        """Prompt for input URLs if none were supplied on the command line."""
        if storage.input_urls:
            return

        welcome()

        storage.logger.debug("No input URLs provided; prompting for input.")
        urls = Prompt.ask("Please enter URLs separated by spaces")
        storage.input_urls = urls.split()


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

        validated_urls: list[AnyUrl] = []
        total_urls = len(storage.input_urls)
        total_unique_urls = len(set(storage.input_urls))

        logger.info("URL validation started (%d URLs)", total_urls)

        tracked_urls = track(
            storage.input_urls, description="URL validation", console=CONSOLE
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


def welcome() -> None:
    """Render a welcome message to the console."""
    # TODO: Improve welcome message
    CONSOLE.print("[bold green]Welcome to Poseidon-MD![/bold green]\n")
