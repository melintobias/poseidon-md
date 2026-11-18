"""Tests for the track model and its downloaded metadata loading."""

import json
from typing import TYPE_CHECKING

from posidon_core.models import TrackMetadata
from pydantic import ValidationError
import pytest

if TYPE_CHECKING:
    from pathlib import Path


def write_metadata(path: Path, info: object) -> Path:
    """Write downloaded metadata as a JSON sidecar.

    Args:
        path: Destination of the metadata file.
        info: JSON-serializable metadata value.

    Returns:
        The written metadata path.
    """
    path.write_text(json.dumps(info), encoding="utf-8")
    return path


def test_read_metadata_file_reads_preferred_fields(tmp_path: Path) -> None:
    """Map each preferred yt-dlp field to its track metadata field."""
    metadata_path = write_metadata(
        tmp_path / "info.json",
        {
            "title": "Song",
            "artists": ["Artist", "Featured Artist"],
            "artist": "Artist, Featured Artist",
            "album": "Album",
            "album_artist": "Album Artist",
            "composers": ["Composer"],
            "track_number": 3,
            "track_count": 12,
            "disc_number": 1,
            "disc_count": 2,
            "release_date": "20240115",
            "upload_date": "20240101",
            "genres": ["Pop", "Rock"],
        },
    )

    assert TrackMetadata.read_metadata_file(metadata_path) == TrackMetadata(
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


def test_read_metadata_file_uses_fallback_fields(tmp_path: Path) -> None:
    """Fall back to secondary yt-dlp fields when preferred ones are absent."""
    metadata_path = write_metadata(
        tmp_path / "info.json",
        {
            "title": "Song",
            "uploader": "Uploader",
            "composer": "Composer",
            "upload_date": "20240101",
            "genre": "Pop",
        },
    )

    assert TrackMetadata.read_metadata_file(metadata_path) == TrackMetadata(
        title="Song",
        artists=("Uploader",),
        album="Song",
        composers=("Composer",),
        release_date="20240101",
        genres=("Pop",),
    )


def test_read_metadata_file_ignores_blank_and_invalid_values(
    tmp_path: Path,
) -> None:
    """Strip text values, and skip blank text and invalid positions."""
    metadata_path = write_metadata(
        tmp_path / "info.json",
        {
            "title": "  Song  ",
            "artists": [" ", None],
            "artist": [" Artist ", "", 7],
            "album": "",
            "composers": [],
            "track_number": 0,
            "track_count": True,
            "disc_number": -1,
            "disc_count": "2",
            "release_date": "  ",
            "genres": [" Pop "],
        },
    )

    assert TrackMetadata.read_metadata_file(metadata_path) == TrackMetadata(
        title="Song", artists=("Artist",), album="Song", genres=("Pop",)
    )


@pytest.mark.parametrize("content", ["[]", '"Song"', "{"])
def test_read_metadata_file_rejects_non_object_json(
    tmp_path: Path, content: str
) -> None:
    """Reject metadata files that do not contain a JSON object."""
    metadata_path = tmp_path / "info.json"
    metadata_path.write_text(content, encoding="utf-8")

    with pytest.raises(ValidationError):
        TrackMetadata.read_metadata_file(metadata_path)
