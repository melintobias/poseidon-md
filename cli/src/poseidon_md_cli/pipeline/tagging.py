"""Apply downloaded source metadata to audio files."""

from __future__ import annotations

import json
import logging
from mimetypes import guess_type
from typing import cast, TYPE_CHECKING

from mutagen.id3 import APIC
from mutagen.id3 import ID3
from mutagen.id3 import PictureType
from rich import progress

from poseidon_md_cli.logger import CONSOLE
from poseidon_md_cli.logger import log_stage_completion
from poseidon_md_cli.pipeline.types import PipelineStage

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from poseidon_md_core.models import Track

    from poseidon_md_cli.pipeline.types import PipelineSharedStorage


def _texts(info: Mapping[str, object], *keys: str) -> list[str]:
    """Return the first non-empty text field or list of text values.

    Args:
        info: Downloaded yt-dlp metadata.
        keys: Source fields in preference order.

    Returns:
        Nonblank text values from the first populated field.
    """
    for key in keys:
        value = info.get(key)
        values = value if isinstance(value, list) else [value]
        texts = [
            item.strip()
            for item in values
            if isinstance(item, str) and item.strip()
        ]
        if texts:
            return texts
    return []


def _number(info: Mapping[str, object], key: str) -> int | None:
    """Read a positive track or disc number from downloaded metadata.

    Args:
        info: Downloaded yt-dlp metadata.
        key: Source field containing the number.

    Returns:
        A positive integer, or ``None`` when the field is absent or invalid.
    """
    value = info.get(key)
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    return None


def _number_pair(
    info: Mapping[str, object], number_key: str, total_key: str
) -> list[str]:
    """Format a position and optional total for Mutagen's easy tags.

    Args:
        info: Downloaded yt-dlp metadata.
        number_key: Source field containing the position.
        total_key: Source field containing the total.

    Returns:
        One position and/or total string, or an empty list when both are absent.
    """
    number = _number(info, number_key)
    total = _number(info, total_key)
    if number is None:
        return [f"0/{total}"] if total is not None else []
    return [f"{number}/{total}" if total is not None else str(number)]


class TaggingStage(PipelineStage):
    """Write source metadata and thumbnail artwork into each MP3 file."""

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

            TaggingStage.tag_track(storage, track)

        log_stage_completion(logger, logging.INFO, "Track tagging completed.")

    @staticmethod
    def load_metadata(metadata_path: Path) -> Mapping[str, object]:
        """Load and validate downloaded metadata from a JSON file.

        Args:
            metadata_path: Path to the downloaded metadata sidecar.

        Returns:
            Metadata fields from the JSON object.

        Raises:
            TypeError: If the JSON value is not an object.
        """
        info = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(info, dict):
            msg = (
                "Downloaded metadata is not a valid JSON object: "
                f"{metadata_path}"
            )
            raise TypeError(msg)
        return cast("Mapping[str, object]", info)

    @staticmethod
    def tag_track(storage: PipelineSharedStorage, track: Track) -> None:
        """Write downloaded metadata and front cover art to an MP3 file.

        Args:
            storage: Existing pipeline storage.
            track: Track with downloaded media, metadata, and thumbnail paths.

        Raises:
            ValueError: If a downloaded path is missing or the thumbnail has
                an unrecognized image type.
            TypeError: If the downloaded metadata is not an object.
        """
        media_path = track.artifacts.tmp_media_path
        metadata_path = track.artifacts.tmp_metadata_path
        thumbnail_path = track.artifacts.tmp_thumbnail_path

        if (
            media_path is None
            or metadata_path is None
            or thumbnail_path is None
        ):
            msg = f"Track has no valid download artifact: {track.url}"
            raise ValueError(msg)

        TaggingStage.add_tags(storage, track)
        TaggingStage.add_track_thumbnail(storage, track)

    @staticmethod
    def add_track_thumbnail(
        storage: PipelineSharedStorage, track: Track
    ) -> None:
        """Write the downloaded thumbnail into the MP3 file.

        Args:
            storage: Existing pipeline storage.
            track: Track with downloaded thumbnail and media paths.

        Raises:
            ValueError: If the media path is missing or the thumbnail has
                an unrecognized image type.
        """
        logger = storage.logger
        media_path = track.artifacts.tmp_media_path
        thumbnail_path = track.artifacts.tmp_thumbnail_path

        if media_path is None:
            msg = f"Track download artifact is invalid: {track.url}"
            raise ValueError(msg)

        if thumbnail_path is None:
            logger.warning("Track has no thumbnail: %s", track.url)
            return

        mime_type = guess_type(thumbnail_path.name)[0]
        if mime_type is None or not mime_type.startswith("image/"):
            msg = f"Unsupported thumbnail image type: {thumbnail_path}"
            raise ValueError(msg)

        image_data = thumbnail_path.read_bytes()

        file = ID3(media_path)

        file.add(
            APIC(
                encoding=3,
                mime=mime_type,
                type=PictureType.COVER_FRONT,
                desc="",
                data=image_data,
            )
        )

        file.save(media_path)

    @staticmethod
    def add_tags(
        storage: PipelineSharedStorage, track: Track
    ) -> dict[str, object]:
        metadata_path = track.artifacts.tmp_metadata_path
        if metadata_path is None:
            raise ValueError("Temporary metadata path not found")

        info = TaggingStage.load_metadata(metadata_path)

        tags = {
            # Use the music track name, falling back to the source title.
            "title": _texts(info, "title"),
            # Keep the ordered artist credits when yt-dlp provides them.
            "artist": _texts(info, "artists", "artist", "creator", "uploader"),
            # Write the release name.
            "album": _texts(info, "album"),
            # Write the album-level artist credit.
            "albumartist": _texts(info, "album_artist"),
            # Preserve the ordered composer credits.
            "composer": _texts(info, "composers", "composer"),
            # Store the track position and total count on its disc.
            "tracknumber": _number_pair(info, "track_number", "track_count"),
            # Store the disc position and total count in its release.
            "discnumber": _number_pair(info, "disc_number", "disc_count"),
            # Prefer release date to upload date.
            "date": _texts(info, "release_date", "upload_date"),
            # Preserve ordered genre labels.
            "genre": _texts(info, "genres", "genre"),
        }

        if track.audio_object is None:
            track.create_audio_object()
            assert track.audio_object is not None  # noqa: S101

        for key, values in tags.items():
            if values:
                storage.logger.debug("Set key %s to value %s", key, values)
                track.audio_object[key] = values

        track.audio_object.save(track.artifacts.tmp_media_path)

        return tags
