"""Acquire source metadata and media through yt-dlp."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from poseidon_md_core.models import MediaArtifact
from poseidon_md_core.models import MetadataCandidate
from poseidon_md_core.models import MetadataRecord
from poseidon_md_core.models import TrackSource
from poseidon_md_core.ports import SourceAcquisition
from poseidon_md_core.ports import SourceAcquisitionError

YT_DLP_PROVIDER = "yt-dlp"
"""Stable provider name recorded for values produced through yt-dlp."""

DEFAULT_FORMAT_SELECTOR = "bestaudio/best"
"""Prefer an audio-only stream while retaining a combined-media fallback."""

DEFAULT_OUTPUT_TEMPLATE = "%(extractor)s-%(id)s.%(ext)s"
"""Collision-resistant filename used for downloaded source artifacts."""

type YtDlpInfo = Mapping[str, object]
"""Resolved information dictionary returned by yt-dlp for one media item."""


class QuietYtDlpLogger:
    """Silence yt-dlp output so the calling application reports failures once.

    The adapter raises yt-dlp failures to its caller, which owns user-facing
    logging. This logger prevents yt-dlp from writing the same failure first.
    """

    def debug(self, message: str) -> None:
        """Discard a diagnostic message emitted by yt-dlp.

        Args:
            message: Diagnostic text that is intentionally not displayed.
        """

    def warning(self, message: str) -> None:
        """Discard a warning emitted by yt-dlp.

        Args:
            message: Warning text that is intentionally not displayed.
        """

    def error(self, message: str) -> None:
        """Discard an error message that will be raised to the caller.

        Args:
            message: Error text represented by the raised acquisition error.
        """


class MissingDownloadedFilepathError(ValueError):
    """Indicate that yt-dlp returned no path for the downloaded artifact."""

    def __init__(self) -> None:
        """Initialize the error with its stable diagnostic message."""
        super().__init__("downloaded filepath is missing")


class YtDlpSourceAcquirer:
    """Use one yt-dlp call to extract metadata and download a source URL.

    Attributes:
        download_directory: Optional directory receiving downloaded artifacts.
    """

    def __init__(self, download_directory: Path | None = None) -> None:
        """Configure the artifact destination.

        Args:
            download_directory: Directory passed to yt-dlp, or `None` to use
                yt-dlp's current-working-directory behavior.
        """
        self.download_directory = download_directory

    def acquire(self, url: str) -> SourceAcquisition:
        """Extract metadata and download one URL through the same yt-dlp call.

        Args:
            url: Validated source URL to acquire.

        Returns:
            Provider-neutral source metadata and downloaded artifact details.

        Raises:
            SourceAcquisitionError: If yt-dlp fails or returns an unusable
                result.
        """
        options = self._options()
        try:
            # yt-dlp accepts dynamic option dictionaries beyond its stub shape.
            with YoutubeDL(cast("Any", options)) as downloader:
                raw_info = downloader.extract_info(url, download=True)
        except (DownloadError, OSError) as error:
            msg = f"yt-dlp could not acquire {url}: {error}"
            raise SourceAcquisitionError(msg) from error

        if not isinstance(raw_info, Mapping):
            msg = f"yt-dlp returned no single-item information for {url}"
            raise SourceAcquisitionError(msg)

        try:
            return _source_acquisition(url, raw_info)
        except (TypeError, ValueError) as error:
            msg = f"yt-dlp returned incomplete information for {url}: {error}"
            raise SourceAcquisitionError(msg) from error

    # TODO: Convert to `@property`.
    def _options(self) -> dict[str, Any]:
        """Build yt-dlp options for a source acquisition.

        Returns:
            Fresh options selecting one best audio-capable media item.
        """
        options: dict[str, Any] = {
            # Prefer source audio without coupling to transformation.
            "format": DEFAULT_FORMAT_SELECTOR,
            # Treat an ambiguous URL as one track instead of a playlist.
            "noplaylist": True,  # TODO: Make optional for playlist support.
            # Keep yt-dlp output behind the application's own logging boundary.
            "quiet": True,
            # Surface failures through exceptions rather than warning text.
            "no_warnings": True,
            # Let the caller report errors once through its application logger.
            "logger": QuietYtDlpLogger(),
            # Name temporary source artifacts independently of mutable titles.
            "outtmpl": DEFAULT_OUTPUT_TEMPLATE,
        }
        if self.download_directory is not None:
            options["paths"] = {
                # Place the artifact in the configured directory.
                "home": str(self.download_directory),
            }

        return options


def _source_acquisition(url: str, info: YtDlpInfo) -> SourceAcquisition:
    """Convert a single yt-dlp item into Poseidon's source acquisition objects.

    Args:
        url: Original validated URL supplied to yt-dlp.
        info: Resolved yt-dlp information for the downloaded item.

    Returns:
        Provider-neutral source, metadata, and artifact values.

    Raises:
        ValueError: If required source or filepath information is absent.
    """
    source_id = _optional_text(info.get("id"))
    if source_id is None:
        raise ValueError("Source ID missing")

    webpage_url = _optional_text(info.get("webpage_url"))
    artifact_path = _downloaded_filepath(info)
    return SourceAcquisition(
        source=TrackSource(
            url=url,
            normalized_url=webpage_url,
            provider=YT_DLP_PROVIDER,
            source_id=source_id,
        ),
        metadata=MetadataCandidate(
            provider=YT_DLP_PROVIDER,
            metadata=_metadata_record(info),
        ),
        artifact=MediaArtifact(
            path=artifact_path,
            format=_optional_text(info.get("ext"))
            or artifact_path.suffix.removeprefix(".")
            or None,
        ),
    )


def _metadata_record(info: YtDlpInfo) -> MetadataRecord:
    """Map supported yt-dlp fields to provider-independent metadata.

    Args:
        info: Resolved yt-dlp information for one downloaded item.

    Returns:
        Source metadata suitable for later validation and cleaning.
    """
    artists = _text_tuple(info.get("artists"))
    if not artists:
        artists = _first_text_tuple(
            info,
            "artist",
            "creator",
            "uploader",
        )

    return MetadataRecord(
        title=_first_text(info, "track", "title"),
        artists=artists,
        album=_optional_text(info.get("album")),
        album_artist=_optional_text(info.get("album_artist")),
        composers=_text_tuple(info.get("composers"))
        or _text_tuple(info.get("composer")),
        track_number=_optional_integer(info.get("track_number")),
        track_total=_optional_integer(info.get("track_count")),
        disc_number=_optional_integer(info.get("disc_number")),
        disc_total=_optional_integer(info.get("disc_count")),
        release_date=_first_text(info, "release_date", "upload_date"),
        genres=_text_tuple(info.get("genres")),
        isrc=_optional_text(info.get("isrc")),
        duration_seconds=_optional_float(info.get("duration")),
        artwork_url=_optional_text(info.get("thumbnail")),
    )


def _downloaded_filepath(info: YtDlpInfo) -> Path:
    """Read the local artifact path recorded by yt-dlp.

    Args:
        info: Resolved yt-dlp information after downloading.

    Returns:
        Path of the downloaded media item.

    Raises:
        MissingDownloadedFilepathError: If yt-dlp did not report a filepath.
    """
    requested_downloads = info.get("requested_downloads")
    if isinstance(requested_downloads, Sequence) and not isinstance(
        requested_downloads,
        (str, bytes),
    ):
        for requested_download in requested_downloads:
            if not isinstance(requested_download, Mapping):
                # TODO: Raise?
                continue
            filepath = _optional_text(requested_download.get("filepath"))
            if filepath is not None:
                return Path(filepath)

    filepath = _first_text(info, "filepath", "_filename")
    if filepath is None:
        raise MissingDownloadedFilepathError
    return Path(filepath)


def _first_text(info: YtDlpInfo, *keys: str) -> str | None:
    """Return the first non-blank textual value for ordered yt-dlp keys.

    Args:
        info: yt-dlp information to inspect.
        *keys: Keys in descending preference order.

    Returns:
        First present non-blank text, or `None`.
    """
    for key in keys:
        value = _optional_text(info.get(key))
        if value is not None:
            return value
    return None


def _first_text_tuple(info: YtDlpInfo, *keys: str) -> tuple[str, ...]:
    """Return the first nonempty tuple of text for ordered yt-dlp keys.

    Args:
        info: yt-dlp information to inspect.
        *keys: Keys in descending preference order.

    Returns:
        First nonempty tuple, or an empty tuple.
    """
    for key in keys:
        values = _text_tuple(info.get(key))
        if values:
            return values
    return ()


def _optional_text(value: object) -> str | None:
    """Return stripped text when an external value is a non-blank string.

    Args:
        value: Untyped value supplied by yt-dlp.

    Returns:
        Stripped non-blank text, or `None`.
    """
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _text_tuple(value: object) -> tuple[str, ...]:
    """Normalize one string or a sequence of strings to a text tuple.

    Args:
        value: Untyped scalar or collection supplied by yt-dlp.

    Returns:
        Ordered non-blank textual values.
    """
    if isinstance(value, str):
        text = _optional_text(value)
        return () if text is None else (text,)
    if not isinstance(value, Sequence) or isinstance(value, bytes):
        return ()
    return tuple(
        text for item in value if (text := _optional_text(item)) is not None
    )


def _optional_integer(value: object) -> int | None:
    """Return an integer when yt-dlp supplied a non-boolean integer.

    Args:
        value: Untyped value supplied by yt-dlp.

    Returns:
        Integer value, or `None` for another type.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _optional_float(value: object) -> float | None:
    """Return a floating-point number for a numeric yt-dlp value.

    Args:
        value: Untyped value supplied by yt-dlp.

    Returns:
        Floating-point value, or `None` for another type.
    """
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value)
