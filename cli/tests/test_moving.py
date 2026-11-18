"""Tests for moving tagged audio files into the output directory."""

import logging
from typing import TYPE_CHECKING

from poseidon_md_cli.pipeline.moving import MovingStage
from poseidon_md_cli.pipeline.types import PipelineSharedStorage
from poseidon_md_core.models import Track
from pydantic import AnyUrl
import pytest

if TYPE_CHECKING:
    from pathlib import Path

AUDIO = b"tagged audio"
"""Placeholder media bytes used to check that a file arrives unchanged."""


@pytest.fixture
def track(tmp_path: Path) -> Track:
    """Create a track whose tagged audio file waits in a download directory.

    Args:
        tmp_path: Per-test temporary directory.

    Returns:
        Track whose temporary media path names an existing audio file.
    """
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    media_path = downloads / "track.mp3"
    media_path.write_bytes(AUDIO)

    track = Track(url=AnyUrl("https://example.com/track"))
    track.artifacts.tmp_media_path = media_path
    return track


def test_run_moves_audio_into_output_directory(
    tmp_path: Path, track: Track
) -> None:
    """Move the audio file into the output directory and clear its path."""
    output_directory = tmp_path / "music"
    output_directory.mkdir()
    storage = PipelineSharedStorage(
        logger=logging.getLogger(__name__),
        tracks=(track,),
        output_directory=output_directory,
    )

    MovingStage.run(storage)

    assert (output_directory / "track.mp3").read_bytes() == AUDIO
    assert not (tmp_path / "downloads" / "track.mp3").exists()
    assert track.artifacts.tmp_media_path is None


def test_run_rejects_existing_output_file(tmp_path: Path, track: Track) -> None:
    """Keep both files when the output directory has a same-named file."""
    existing = tmp_path / "track.mp3"
    existing.write_bytes(b"existing audio")
    storage = PipelineSharedStorage(
        logger=logging.getLogger(__name__),
        tracks=(track,),
        output_directory=tmp_path,
    )

    with pytest.raises(FileExistsError):
        MovingStage.run(storage)

    assert existing.read_bytes() == b"existing audio"
    assert track.artifacts.tmp_media_path is not None
    assert track.artifacts.tmp_media_path.read_bytes() == AUDIO
