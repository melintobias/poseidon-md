"""Extract source metadata and download media into shared pipeline storage."""

import logging

from poseidon_md_core import Track
from poseidon_md_core.ports import SourceAcquirer
from poseidon_md_core.ports import SourceAcquisitionError
from rich.progress import track

from poseidon_md_cli.logger import CONSOLE

from .types import PipelineSharedStorage
from .types import PipelineStage
from .types import StageOrchestrator


class ExtractionStage(PipelineStage):
    """Coordinate sequential source extraction and download work."""

    @classmethod
    def run(cls, shared_storage: PipelineSharedStorage | None = None) -> None:
        """Run source acquisition steps against shared pipeline storage.

        Args:
            shared_storage: Existing pipeline storage, or `None` to create
                empty storage for this run.
        """
        StageOrchestrator(
            [
                ExtractUrls,
            ],
            shared_storage=shared_storage,
        ).run()


class ExtractUrls(PipelineStage):
    """Acquire validated URLs sequentially through the configured service."""

    @classmethod
    def get_source_acquirer(
        cls,
        shared_storage: PipelineSharedStorage,
        total_urls: int,
    ) -> SourceAcquirer | None:
        """Return configured source acquirer or handle empty-url no-op case.

        Raises:
            RuntimeError: If URLs exist without a configured acquisition
                service.
        """
        source_acquirer = shared_storage.source_acquirer
        if source_acquirer is None:
            if total_urls == 0:
                shared_storage.tracks = ()
                shared_storage.logger.info(
                    "Source acquisition completed (0/0 URLs acquired)",
                )
                return None

            raise RuntimeError("Source acquisition service not configured")

        return source_acquirer

    @classmethod
    def run(cls, shared_storage: PipelineSharedStorage) -> None:
        """Store tracks containing extracted metadata and downloaded media.

        Args:
            shared_storage: Blackboard containing validated URLs, the
                acquisition service, and the destination track collection.

        Raises:
            RuntimeError: If URLs exist without a configured acquisition
                service.
            SystemExit: If every supplied URL fails acquisition.
        """
        logger = shared_storage.logger

        acquired_tracks: list[Track] = []
        total_urls = len(shared_storage.urls)
        logger.info("Source acquisition started (%d URLs)", total_urls)

        source_acquirer = cls.get_source_acquirer(shared_storage, total_urls)
        if source_acquirer is None:
            return

        for index, url in enumerate(
            track(
                shared_storage.urls,
                description="Source acquisition",
                console=CONSOLE,
            ),
            start=1,
        ):
            source_url = str(url)
            logger.debug(
                "%d/%d Acquiring: %s",
                index,
                total_urls,
                source_url,
            )

            try:
                acquisition = source_acquirer.acquire(source_url)
            except SourceAcquisitionError:
                logger.exception(
                    "%d/%d Source acquisition failed for %s",
                    index,
                    total_urls,
                    source_url,
                )
                continue

            acquired_track = Track(source=acquisition.source)
            acquired_track = acquired_track.with_extracted_metadata(
                acquisition.metadata,
            )
            acquired_track = acquired_track.with_downloaded_artifact(
                acquisition.artifact,
            )
            acquired_tracks.append(acquired_track)
            logger.info(
                "%d/%d Source acquired: %s",
                index,
                total_urls,
                acquisition.artifact.location,
            )

        shared_storage.tracks = tuple(acquired_tracks)
        total_failure = not acquired_tracks and total_urls > 0
        level = logging.CRITICAL if total_failure else logging.INFO
        logger.log(
            level,
            "Source acquisition completed (%d/%d URLs acquired)",
            len(acquired_tracks),
            total_urls,
        )

        if total_failure:
            raise SystemExit(1)
