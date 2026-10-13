"""Move tagged audio files to the current working directory."""

import logging
from pathlib import Path
import shutil
from typing import TYPE_CHECKING

from rich import progress

from poseidon_md_cli.logger import CONSOLE
from poseidon_md_cli.logger import log_stage_completion
from poseidon_md_cli.pipeline.types import PipelineStage

if TYPE_CHECKING:
    from poseidon_md_cli.pipeline.types import PipelineSharedStorage


class MovingStage(PipelineStage):
    """Publish each tagged audio file in the current working directory."""

    @classmethod
    def run(cls, storage: PipelineSharedStorage) -> None:
        """Move every tagged track's audio file to the working directory.

        Args:
            storage: Pipeline storage containing the tagged tracks.

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

            destination = Path.cwd() / source.name
            if destination.exists() or destination.is_symlink():
                raise FileExistsError(destination)

            shutil.move(source, destination)
            track.artifacts.tmp_media_path = None
            storage.logger.info(
                'Moved track %s/%s to "%s": %s',
                index,
                len(tracks),
                destination,
                track.url,
            )  # TODO: Encapsulate track path dynamically; replace double quotes

        log_stage_completion(logger, logging.INFO, "Track moving completed.")
