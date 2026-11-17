"""Contract for writing resolved track metadata into a media file."""

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from poseidon_md_core.models import TrackMetadata


class TagWriter(Protocol):
    """Write track metadata and artwork in the target file's native format."""

    def write(
        self, media_path: Path, metadata: TrackMetadata, artwork_path: Path
    ) -> None:
        """Apply track metadata and artwork to the supplied media file in place.

        Args:
            media_path: Existing media file to update.
            metadata: Track metadata whose populated fields should be applied.
            artwork_path: Local image to embed as front cover artwork.

        Raises:
            ValueError: If the writer rejects the media format or artwork type.
        """
        ...
