"""Apply downloaded source metadata to audio files."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from poseidon_md_core.adapters.tagging.mp3 import Mp3TagWriter
from poseidon_md_core.models import TrackMetadata
from pydantic import ValidationError
from rich import progress

from poseidon_md_cli.logger import CONSOLE
from poseidon_md_cli.logger import log_stage_completion
from poseidon_md_cli.options import OutputFormat
from poseidon_md_cli.pipeline.types import PipelineStage

if TYPE_CHECKING:
    from collections.abc import Callable

    from poseidon_md_core.models import Track
    from poseidon_md_core.ports import TagWriter

    from poseidon_md_cli.pipeline.types import PipelineSharedStorage


_TAG_WRITERS: dict[OutputFormat, Callable[[logging.Logger], TagWriter]] = {
    # Write ID3 metadata and artwork into MP3 files.
    OutputFormat.MP3: Mp3TagWriter
}
"""Factories that build tag writers for the supported output formats."""


class TaggingStage(PipelineStage):
    """Apply metadata and artwork with the writer for the output format."""

    @classmethod
    def run(cls, storage: PipelineSharedStorage) -> None:
        """Run all tagging steps against shared pipeline storage.

        Args:
            storage: Existing pipeline storage.
        """
        logger = storage.logger
        tracks = storage.tracks

        tracked_tracks = progress.track(
            tracks, description="Track tagging", console=CONSOLE
        )

        for index, track in enumerate(tracked_tracks, start=1):
            logger.info(
                "Tagging track %d/%d: %s", index, len(tracks), track.url
            )

            cls.add_file_metadata(storage, track)

        log_stage_completion(logger, logging.INFO, "Track tagging completed.")

    @staticmethod
    def add_file_metadata(storage: PipelineSharedStorage, track: Track) -> None:
        """Read downloaded metadata and tag the track's media file.

        Log invalid metadata and skip tagging the track when parsing fails.

        Args:
            storage: Existing pipeline storage.
            track: Track with downloaded media, metadata, and thumbnail paths.

        Raises:
            ValueError: If a downloaded artifact path is missing or the writer
                rejects the media file or thumbnail type.
        """
        media_path = track.artifacts.tmp_media_path
        metadata_path = track.artifacts.tmp_metadata_path
        thumbnail_path = track.artifacts.tmp_thumbnail_path

        if (
            media_path is None
            or metadata_path is None
            or thumbnail_path is None
        ):
            # TODO: Enhance error msg
            msg = f"Track has no valid download artifact: {track.url}"
            raise ValueError(msg)

        try:
            metadata = TrackMetadata.read_metadata_file(metadata_path)
        except ValidationError:
            storage.logger.exception("Applying metadata failed: %s", track.url)
            return

        tag_writer = _TAG_WRITERS[storage.options.output_format](storage.logger)
        tag_writer.write(media_path, metadata, thumbnail_path)
        track.metadata = metadata
