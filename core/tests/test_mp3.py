"""Tests for writing track metadata and artwork to MP3 files."""

import logging
from typing import TYPE_CHECKING

from mutagen.id3 import ID3
from mutagen.id3 import PictureType
from mutagen.mp3 import EasyMP3
from poseidon_md_core.adapters.tagging.mp3 import Mp3TagWriter
from poseidon_md_core.models import TrackMetadata
import pytest

if TYPE_CHECKING:
    from pathlib import Path

MP3_FRAME = bytes((0xFF, 0xFB, 0x90, 0x64)) + bytes(413)
"""Silent 128 kilobits per second, 44.1 kHz MPEG-1 Layer III audio frame."""

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
"""PNG header used to check that the writer embeds the supplied bytes."""


@pytest.fixture
def writer() -> Mp3TagWriter:
    """Create an MP3 tag writer that logs to pytest's capture.

    Returns:
        Writer using a propagating test logger.
    """
    return Mp3TagWriter(logging.getLogger(__name__))


@pytest.fixture
def media_path(tmp_path: Path) -> Path:
    """Create an untagged MP3 file.

    Args:
        tmp_path: Per-test temporary directory.

    Returns:
        Path to the MP3 file.
    """
    path = tmp_path / "track.mp3"
    path.write_bytes(MP3_FRAME * 4)
    return path


@pytest.fixture
def artwork_path(tmp_path: Path) -> Path:
    """Create a PNG artwork file.

    Args:
        tmp_path: Per-test temporary directory.

    Returns:
        Path to the artwork file.
    """
    path = tmp_path / "track.png"
    path.write_bytes(PNG_SIGNATURE)
    return path


def read_tags(media_path: Path) -> dict[str, list[str]]:
    """Read the easy tags saved in an MP3 file.

    Args:
        media_path: MP3 file to read.

    Returns:
        Easy tag values by key.
    """
    return dict(EasyMP3(media_path))


def test_write_applies_text_and_cover(
    writer: Mp3TagWriter, media_path: Path, artwork_path: Path
) -> None:
    """Update text and cover art across retries while preserving other tags."""
    original = EasyMP3(media_path)
    original["copyright"] = ["Example Records"]
    original.save()
    metadata = TrackMetadata(
        title="Song",
        artists=("Artist", "Featured Artist"),
        album="Album",
        album_artist="Album Artist",
        composers=("Composer",),
        track_number=3,
        track_total=12,
        disc_number=1,
        disc_total=2,
        release_date="20240115",
        genres=("Pop", "Rock"),
    )

    writer.write(media_path, metadata, artwork_path)
    writer.write(media_path, metadata, artwork_path)

    assert read_tags(media_path) == {
        "title": ["Song"],
        "artist": ["Artist", "Featured Artist"],
        "album": ["Album"],
        "albumartist": ["Album Artist"],
        "composer": ["Composer"],
        "tracknumber": ["3/12"],
        "discnumber": ["1/2"],
        "date": ["20240115"],
        "genre": ["Pop", "Rock"],
        "copyright": ["Example Records"],
    }
    (cover,) = ID3(media_path).getall("APIC")
    assert cover.type == PictureType.COVER_FRONT
    assert cover.mime == "image/png"
    assert cover.data == PNG_SIGNATURE


@pytest.mark.parametrize(
    ("metadata", "expected"),
    [
        (TrackMetadata(track_number=3, track_total=12), ["3/12"]),
        (TrackMetadata(track_number=3), ["3"]),
        (TrackMetadata(track_total=12), ["0/12"]),
    ],
)
def test_write_formats_track_position(
    writer: Mp3TagWriter,
    media_path: Path,
    artwork_path: Path,
    metadata: TrackMetadata,
    expected: list[str],
) -> None:
    """Combine the track position and total into one tag value."""
    writer.write(media_path, metadata, artwork_path)

    assert read_tags(media_path)["tracknumber"] == expected


def test_write_skips_unpopulated_fields(
    writer: Mp3TagWriter, media_path: Path, artwork_path: Path
) -> None:
    """Leave tags absent for metadata fields without a value."""
    writer.write(media_path, TrackMetadata(title="Song"), artwork_path)

    assert read_tags(media_path) == {"title": ["Song"]}


def test_write_rejects_unsupported_media(
    writer: Mp3TagWriter, tmp_path: Path, artwork_path: Path
) -> None:
    """Reject an unsupported media file before writing ID3 tags into it."""
    media_path = tmp_path / "track.txt"
    media_path.write_bytes(b"not audio")

    with pytest.raises(ValueError, match="Unsupported media format"):
        writer.write(media_path, TrackMetadata(title="Song"), artwork_path)

    assert media_path.read_bytes() == b"not audio"
