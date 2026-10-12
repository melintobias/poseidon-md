"""Move tagged audio files to the current working directory."""

from pathlib import Path
import shutil
from typing import TYPE_CHECKING

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
        for track in storage.tracks:
            source = track.artifacts.tmp_media_path
            if source is None:
                msg = f"Track has no downloaded audio file: {track.url}"
                raise ValueError(msg)

            destination = Path.cwd() / source.name
            if destination.exists() or destination.is_symlink():
                raise FileExistsError(destination)

            shutil.move(source, destination)
            track.artifacts.tmp_media_path = None
            storage.logger.info("Moved track to %s", destination)
