"""Move tagged audio files to the pipeline's output directory."""

import logging
import shutil
from typing import TYPE_CHECKING

from rich import progress

from posidon_cli.logger import CONSOLE
from posidon_cli.logger import log_stage_completion
from posidon_cli.pipeline.types import PipelineStage

if TYPE_CHECKING:
    from posidon_cli.pipeline.types import PipelineSharedStorage


class MovingStage(PipelineStage):
    """Publish each tagged audio file in the output directory."""

    @classmethod
    def run(cls, storage: PipelineSharedStorage) -> None:
        """Move every tagged track's audio file to the output directory.

        Args:
            storage: Pipeline storage containing the tagged tracks and the
                output directory receiving their audio files.

        Raises:
            ValueError: If the track has no downloaded audio file.
            FileExistsError: If an output with the same name already exists.
        """
        logger = storage.logger
        tracks = storage.tracks

        tracked_tracks = progress.track(
            tracks, description="Track moving", console=CONSOLE
        )
        for index, track in enumerate(tracked_tracks, start=1):
            source = track.artifacts.tmp_media_path
            if source is None:
                msg = f"Track has no downloaded audio file: {track.url}"
                raise ValueError(msg)

            destination = storage.output_directory / source.name
            if destination.exists() or destination.is_symlink():
                raise FileExistsError(destination)

            shutil.move(source, destination)
            track.artifacts.tmp_media_path = None
            storage.logger.info(
                "Moved track %s/%s to %r: %s",
                index,
                len(tracks),
                str(destination),
                track.url,
            )

        log_stage_completion(logger, logging.INFO, "Track moving completed.")
