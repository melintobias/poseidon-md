"""Validate, deduplicate, and report URLs entering the CLI pipeline."""

import logging
import typing

from poseidon_md_core.pipeline.intake import validate_url
from rich.progress import track
from rich.prompt import Prompt

from poseidon_md_cli.logger import CONSOLE

from .types import PipelineSharedStorage
from .types import PipelineStage
from .types import StageOrchestrator

if typing.TYPE_CHECKING:
    from pydantic import AnyUrl


class IntakeStage(PipelineStage):
    """Coordinate the URL validation work performed during intake."""

    @classmethod
    def run(cls, shared_storage: PipelineSharedStorage | None = None) -> None:
        """Run all URL intake steps against shared pipeline storage.

        Args:
            shared_storage: Existing pipeline storage, or `None` to create
                empty storage for this run.

        Raises:
            SystemExit: If no input URLs are provided and the `no_prompt` option
                is set.
        """
        if (
            shared_storage
            and shared_storage.no_prompt
            and not shared_storage.input_urls
        ):
            shared_storage.logger.info("No input URLs provided; exiting.")
            raise SystemExit(0)

        StageOrchestrator(
            [InputStage, ValidateUrls],
            shared_storage,
        ).run()


class InputStage(PipelineStage):
    """Prompt for input URLs if none were supplied on the command line."""

    @classmethod
    def run(cls, shared_storage: PipelineSharedStorage) -> None:
        """Prompt for input URLs if none were supplied on the command line."""
        if shared_storage.input_urls:
            return

        welcome()

        shared_storage.logger.debug(
            "No input URLs provided; prompting for input.",
        )
        urls = Prompt.ask("Please enter URLs separated by spaces")
        shared_storage.input_urls = urls.split()


class ValidateUrls(PipelineStage):
    """Validate and deduplicate supplied URLs."""

    @classmethod
    def run(cls, shared_storage: PipelineSharedStorage) -> None:
        """Store valid URLs.

        Args:
            shared_storage: Pipeline storage containing the input URLs and
                receiving the validated URL set.

        Raises:
            SystemExit: If all input URLs are invalid.
        """
        logger = shared_storage.logger

        validated_urls: list[AnyUrl] = []
        total_urls = len(shared_storage.input_urls)
        total_unique_urls = len(set(shared_storage.input_urls))

        logger.info("URL validation started (%d URLs)", total_urls)

        tracked_urls = track(
            shared_storage.input_urls,
            description="URL validation",
            console=CONSOLE,
        )
        for index, url in enumerate(tracked_urls, start=1):
            logger.debug("%d/%d Validating: %s", index, total_urls, url)

            if (validated_url := validate_url(url)) is None:
                logger.error(
                    "%d/%d Invalid URL skipped: %s",
                    index,
                    total_urls,
                    url,
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
            logger.info(
                "%d/%d Valid URL: %s",
                index,
                total_urls,
                validated_url,
            )

        shared_storage.urls = tuple(validated_urls)

        total_success = len(validated_urls) == total_unique_urls
        total_failure = len(validated_urls) == 0 and total_unique_urls > 0

        if total_success:
            level = logging.INFO
        elif total_failure:
            level = logging.CRITICAL
        else:
            level = logging.WARNING

        logger.log(
            level,
            "URL validation completed (%d/%d unique URLs valid)",
            len(validated_urls),
            total_unique_urls,
        )

        if total_failure:
            logger.critical(
                "All %d unique URLs were invalid; exiting.",
                total_unique_urls,
            )
            raise SystemExit(1)


def welcome() -> None:
    """Render a welcome message to the console."""
    # TODO: Improve welcome message
    CONSOLE.print("[bold green]Welcome to Poseidon-MD![/bold green]\n")
