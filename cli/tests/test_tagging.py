"""Tests for writing downloaded metadata to audio file tags."""

import json
import logging
from typing import TYPE_CHECKING

from mutagen.id3 import ID3
from mutagen.mp3 import EasyMP3
from poseidon_md_cli.models.yt_dlp import DownloadArtifact
from poseidon_md_cli.options import OutputFormat
from poseidon_md_cli.pipeline.tagging import _TAG_WRITERS  # noqa: PLC2701
from poseidon_md_cli.pipeline.tagging import TaggingStage
from poseidon_md_cli.pipeline.types import PipelineSharedStorage
from poseidon_md_core.models import Track
from poseidon_md_core.models import TrackMetadata
from pydantic import AnyUrl
import pytest

if TYPE_CHECKING:
    from pathlib import Path

MP3_FRAME = bytes((0xFF, 0xFB, 0x90, 0x64)) + bytes(413)
"""Silent 128 kilobits per second, 44.1 kHz MPEG-1 Layer III audio frame."""

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
"""PNG header used to check that the stage embeds the downloaded thumbnail."""


@pytest.fixture
def storage() -> PipelineSharedStorage:
    """Create pipeline storage whose log records reach pytest's capture.

    Returns:
        Pipeline storage with a propagating test logger.
    """
    return PipelineSharedStorage(logger=logging.getLogger(__name__))


@pytest.fixture
def track(tmp_path: Path) -> Track:
    """Create a track with downloaded untagged MP3 media and thumbnail bytes.

    The metadata sidecar path is set, but each test writes its own content.

    Args:
        tmp_path: Per-test temporary directory.

    Returns:
        Track whose artifact paths are in `tmp_path`.
    """
    media_path = tmp_path / "track.mp3"
    media_path.write_bytes(MP3_FRAME * 4)
    thumbnail_path = tmp_path / "track.png"
    thumbnail_path.write_bytes(PNG_SIGNATURE)

    track = Track(url=AnyUrl("https://example.com/track"))
    track.apply_download_artifact(
        DownloadArtifact(
            media_path=media_path,
            metadata_path=tmp_path / "track.info.json",
            thumbnail_path=thumbnail_path,
        )
    )
    return track


def write_metadata(track: Track, info: object) -> None:
    """Write the downloaded metadata sidecar of a track as JSON.

    Args:
        track: Track whose metadata path receives the content.
        info: JSON-serializable metadata value.
    """
    assert track.artifacts.tmp_metadata_path is not None
    track.artifacts.tmp_metadata_path.write_text(
        json.dumps(info), encoding="utf-8"
    )


def read_tags(track: Track) -> dict[str, list[str]]:
    """Read the easy tags saved in a track's media file.

    Args:
        track: Track whose media file is read.

    Returns:
        Easy tag values by key.
    """
    return dict(EasyMP3(track.artifacts.tmp_media_path))


@pytest.mark.parametrize("output_format", list(OutputFormat))
def test_every_output_format_has_tag_writer(
    output_format: OutputFormat,
) -> None:
    """Map each output format accepted by the CLI to a tag writer."""
    assert output_format in _TAG_WRITERS


def test_add_file_metadata_tags_media_and_stores_metadata(
    storage: PipelineSharedStorage, track: Track
) -> None:
    """Write downloaded metadata and the thumbnail, then store the metadata."""
    write_metadata(track, {"title": "Song", "artists": ["Artist"]})

    TaggingStage.add_file_metadata(storage, track)

    assert track.metadata == TrackMetadata(
        title="Song", artists=("Artist",), album="Song"
    )
    assert read_tags(track) == {
        "title": ["Song"],
        "artist": ["Artist"],
        "album": ["Song"],
    }
    (cover,) = ID3(track.artifacts.tmp_media_path).getall("APIC")
    assert cover.data == PNG_SIGNATURE


def test_add_file_metadata_logs_invalid_metadata(
    storage: PipelineSharedStorage,
    track: Track,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Log invalid downloaded metadata and leave the media file untagged."""
    write_metadata(track, [])

    TaggingStage.add_file_metadata(storage, track)

    assert track.metadata == TrackMetadata()
    assert read_tags(track) == {}
    assert [record.getMessage() for record in caplog.records] == [
        "Applying metadata failed: https://example.com/track"
    ]


def test_add_file_metadata_rejects_missing_thumbnail(
    storage: PipelineSharedStorage, track: Track
) -> None:
    """Reject a track whose downloaded artifacts have no thumbnail path."""
    track.artifacts.tmp_thumbnail_path = None

    with pytest.raises(ValueError, match="no valid download artifact"):
        TaggingStage.add_file_metadata(storage, track)


def test_add_file_metadata_leaves_media_intact_when_artwork_is_unreadable(
    storage: PipelineSharedStorage, track: Track
) -> None:
    """Leave the file and track metadata intact if artwork cannot be read."""
    assert track.artifacts.tmp_thumbnail_path is not None
    track.artifacts.tmp_thumbnail_path.unlink()
    write_metadata(track, {"title": "Song"})

    with pytest.raises(FileNotFoundError):
        TaggingStage.add_file_metadata(storage, track)

    assert track.metadata == TrackMetadata()
    assert track.artifacts.tmp_media_path is not None
    assert track.artifacts.tmp_media_path.read_bytes() == MP3_FRAME * 4
