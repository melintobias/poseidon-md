"""Models for yt-dlp integration."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True, kw_only=True)
class DownloadArtifact:
    """References to downloaded media and metadata.

    Attributes:
        metadata_path: Path to the downloaded metadata JSON file.
        thumbnail_path: Path to the first downloaded thumbnail image file.
        media_path: Path to the final downloaded media file.
    """

    metadata_path: Path
    thumbnail_path: Path
    media_path: Path
