"""Track object."""

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from tempfile import mkdtemp
from typing import TYPE_CHECKING

from mutagen.mp3 import EasyMP3

if TYPE_CHECKING:
    from poseidon_md_cli.models.yt_dlp import DownloadArtifact
    from pydantic import AnyUrl


@dataclass(slots=True, kw_only=True)
class TrackMetadata:
    """Provider-independent values describing a track.

    Dates remain strings because music providers commonly return partial dates
    such as a year or a year and month. Extracted and external records may still
    contain semantically invalid values; validation occurs when a record is
    promoted to cleaned or resolved metadata.

    Attributes:
        title: Track title.
        artists: Ordered primary and featured artist names.
        album: Album or release title.
        album_artist: Credited album-level artist.
        composers: Ordered composer names.
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
    release_date: str | None = None
    genres: tuple[str, ...] = ()
    isrc: str | None = None
    duration_seconds: float | None = None
    artwork_url: str | None = None


@dataclass(slots=True, kw_only=True)
class TrackArtifacts:
    """References to downloaded, transformed, and stored media.

    Attributes:
        tmp_directory: Temporary directory for downloaded media.
        tmp_media_path: Path to the final downloaded media file.
        tmp_metadata_path: Path to the downloaded metadata JSON file.
        tmp_thumbnail_path: Path to the first downloaded thumbnail image file.
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
    """Immutable track aggregate passed between media pipeline modules.

    Attributes:
        url: Track URL and provider identity.
        audio_object: Mutable audio object.
        metadata: Metadata state accumulated across relevant stages.
        artifacts: Downloaded, transformed, and stored media references.
    """

    url: AnyUrl
    audio_object: EasyMP3 | None = field(default=None)
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

    def create_audio_object(self, *, replace_existing: bool = True) -> EasyMP3:
        if not replace_existing and self.audio_object:
            return self.audio_object

        if not self.artifacts.tmp_media_path:
            self.audio_object = EasyMP3()
            return self.audio_object

        self.audio_object = EasyMP3(str(self.artifacts.tmp_media_path))
        return self.audio_object
