"""Track object."""

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from tempfile import mkdtemp
from typing import TYPE_CHECKING

from pydantic import JsonValue
from pydantic import TypeAdapter

if TYPE_CHECKING:
    from collections.abc import Mapping

    from poseidon_md_cli.models.yt_dlp import DownloadArtifact
    from pydantic import AnyUrl

_METADATA_FILE_ADAPTER = TypeAdapter(dict[str, JsonValue])
"""Validator for yt-dlp metadata files, which must contain a JSON object."""


@dataclass(slots=True, kw_only=True)
class TrackMetadata:
    """Provider-independent values describing a track.

    Dates remain strings because music providers commonly return partial dates
    such as a year or a year and month.

    Attributes:
        title: Track title.
        artists: Ordered primary and featured artist names.
        album: Album or release title.
        album_artist: Credited album-level artist.
        composers: Ordered composer names.
        track_number: One-based position on the disc.
        track_total: Total number of tracks on the disc.
        disc_number: One-based disc position in the release.
        disc_total: Total number of discs in the release.
        release_date: Full or partial release date supplied by a provider.
        genres: Ordered genre labels.
        isrc: International Standard Recording Code.
        duration_seconds: Track duration in seconds.
        artwork_url: URL of the selected artwork.
    """

    title: str | None = None
    artists: tuple[str, ...] = ()
    album: str | None = None
    album_artist: str | None = None
    composers: tuple[str, ...] = ()
    track_number: int | None = None
    track_total: int | None = None
    disc_number: int | None = None
    disc_total: int | None = None
    release_date: str | None = None
    genres: tuple[str, ...] = ()
    isrc: str | None = None
    duration_seconds: float | None = None
    artwork_url: str | None = None

    @staticmethod
    def read_metadata_file(path: Path) -> TrackMetadata:
        """Load track metadata from a downloaded yt-dlp metadata JSON file.

        Text values are stripped, and blank text or non-positive positions are
        ignored, so every populated field is usable as a tag value.

        Args:
            path: Path to the downloaded metadata sidecar.

        Returns:
            Metadata read from the populated fields of the JSON object.

        Raises:
            ValidationError: If the file does not contain a JSON object.
        """
        # TODO: Ensure utf-8 encoding on initial metadata file creation.
        info = _METADATA_FILE_ADAPTER.validate_json(
            path.read_text(encoding="utf-8")
        )

        return TrackMetadata(
            title=_text(info, "title"),
            # Keep the ordered artist credits when yt-dlp provides them.
            artists=_texts(info, "artists", "artist", "creator", "uploader"),
            # Use the release name, falling back to the source title.
            album=_text(info, "album", "title"),
            album_artist=_text(info, "album_artist"),
            composers=_texts(info, "composers", "composer"),
            track_number=_number(info, "track_number"),
            track_total=_number(info, "track_count"),
            disc_number=_number(info, "disc_number"),
            disc_total=_number(info, "disc_count"),
            # Prefer release date to upload date.
            release_date=_text(info, "release_date", "upload_date"),
            genres=_texts(info, "genres", "genre"),
        )


@dataclass(slots=True, kw_only=True)
class TrackArtifacts:
    """References to downloaded, transformed, and stored media.

    Attributes:
        tmp_directory: Temporary directory for downloaded media.
        tmp_media_path: Path to the final downloaded media file.
        tmp_metadata_path: Path to the downloaded metadata JSON file.
        tmp_thumbnail_path: Path to the thumbnail ready for tagging.
    """

    tmp_directory: Path | None = None
    tmp_media_path: Path | None = None
    tmp_metadata_path: Path | None = None
    tmp_thumbnail_path: Path | None = None

    def apply_download_artifact(self, artifact: DownloadArtifact) -> None:
        """Store the downloaded artifact in the track artifacts.

        Args:
            artifact: Downloaded media and metadata references.
        """
        self.tmp_metadata_path = artifact.metadata_path
        self.tmp_thumbnail_path = artifact.thumbnail_path
        self.tmp_media_path = artifact.media_path


@dataclass(slots=True, kw_only=True)
class Track:
    """Track aggregate passed between media pipeline modules.

    Attributes:
        url: Track URL and provider identity.
        metadata: Metadata state accumulated across relevant stages.
        artifacts: Downloaded, transformed, and stored media references.
    """

    url: AnyUrl
    artifacts: TrackArtifacts = field(default_factory=TrackArtifacts)
    metadata: TrackMetadata = field(default_factory=TrackMetadata)

    def generate_track_tmp_directory(
        self, base_directory: Path | None = None
    ) -> Path:
        """Generate and store a temporary directory for the track.

        Args:
            base_directory: Optional base directory for the temporary directory.

        Returns:
            Path to the created temporary directory.
        """
        self.artifacts.tmp_directory = Path(
            mkdtemp(prefix="poseidon_md_", dir=base_directory)
        )
        return self.artifacts.tmp_directory

    @property
    def tmp_directory(self) -> Path:
        """Get the temporary directory for the track.

        If the temporary directory has not yet been generated, one automatically
        will be.

        Returns:
            Path to the temporary directory.
        """
        return (
            self.artifacts.tmp_directory or self.generate_track_tmp_directory()
        )

    def apply_download_artifact(self, artifact: DownloadArtifact) -> None:
        """Store the downloaded artifact in the track artifacts.

        Args:
            artifact: Downloaded media and metadata references.
        """
        self.artifacts.apply_download_artifact(artifact)


def _text(info: Mapping[str, object], *keys: str) -> str | None:
    """Return the first non-blank text field, stripped.

    Args:
        info: Downloaded yt-dlp metadata.
        keys: Source fields in preference order.

    Returns:
        Stripped text from the first populated field, or `None` when no field
        contains non-blank text.
    """
    for key in keys:
        value = info.get(key)
        if isinstance(value, str) and (text := value.strip()):
            return text
    return None


def _texts(info: Mapping[str, object], *keys: str) -> tuple[str, ...]:
    """Return the stripped text values of the first populated field.

    A field may contain one text value or a list of them. Blank and non-text
    list items are discarded.

    Args:
        info: Downloaded yt-dlp metadata.
        keys: Source fields in preference order.

    Returns:
        Stripped text values from the first populated field, or an empty tuple
        when no field contains non-blank text.
    """
    for key in keys:
        value = info.get(key)
        values = value if isinstance(value, list) else [value]
        texts = tuple(
            item.strip()
            for item in values
            if isinstance(item, str) and item.strip()
        )
        if texts:
            return texts
    return ()


def _number(info: Mapping[str, object], key: str) -> int | None:
    """Read a positive track or disc number from downloaded metadata.

    Args:
        info: Downloaded yt-dlp metadata.
        key: Source field containing the number.

    Returns:
        A positive integer, or `None` when the field is absent or invalid.
    """
    value = info.get(key)
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    return None
