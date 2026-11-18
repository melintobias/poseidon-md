"""Write text tags and front cover artwork to MP3 files using Mutagen."""

from mimetypes import guess_file_type
from typing import TYPE_CHECKING

from mutagen import id3
from mutagen.mp3 import HeaderNotFoundError
from mutagen.mp3 import MP3

if TYPE_CHECKING:
    from logging import Logger
    from pathlib import Path

    from posidon_core.models import TrackMetadata


def _number_pair(number: int | None, total: int | None) -> str | None:
    """Format a track or disc position with its optional total.

    Args:
        number: One-based position on the disc or in the release.
        total: Total number of tracks on the disc or discs in the release.

    Returns:
        The position, a position/total pair with zero for an unknown position,
        or `None` when both are absent.
    """
    if number is None:
        return f"0/{total}" if total is not None else None
    return f"{number}/{total}" if total is not None else str(number)


class Mp3TagWriter:
    """Apply populated metadata fields and artwork in one ID3 save.

    Attributes:
        logger: Logger that receives diagnostic tag assignments.
    """

    def __init__(self, logger: Logger) -> None:
        """Configure diagnostic logging for the writer.

        Args:
            logger: Application logger that receives tag assignments.
        """
        self.logger = logger

    def write(
        self, media_path: Path, metadata: TrackMetadata, artwork_path: Path
    ) -> None:
        """Update the MP3's ID3 tags in place.

        Args:
            media_path: Existing MP3 file to update.
            metadata: Track metadata whose populated fields are applied.
            artwork_path: Image file to embed as the front cover.

        Raises:
            ValueError: If the media has no MPEG audio header or the artwork
                filename has an unrecognized image type.
            OSError: If reading the artwork file fails.
            mutagen.MutagenError: If opening or saving the media file fails.
        """
        mime_type = guess_file_type(artwork_path)[0]
        if mime_type is None or not mime_type.startswith("image/"):
            msg = f"Unsupported thumbnail image type: {artwork_path}"
            raise ValueError(msg)

        artwork = id3.APIC(
            encoding=id3.Encoding.UTF8,
            mime=mime_type,
            type=id3.PictureType.COVER_FRONT,
            desc="",  # TODO: Weigh desc options
            data=artwork_path.read_bytes(),
        )
        try:
            audio = MP3(media_path)
        except HeaderNotFoundError as error:
            msg = f"Unsupported media format: {media_path}"
            raise ValueError(msg) from error

        tags = audio.tags if audio.tags is not None else id3.ID3()
        text_frames = {
            # track title
            id3.TIT2: metadata.title,
            # artists (ordered!)
            id3.TPE1: list(metadata.artists),
            # media title, NOT necessarily album
            id3.TALB: metadata.album,
            # album artist(s)
            id3.TPE2: metadata.album_artist,
            # composers (ordered!)
            id3.TCOM: list(metadata.composers),
            # track number + total number of tracks in the release
            id3.TRCK: _number_pair(metadata.track_number, metadata.track_total),
            # disc number + total number of disks in the release
            id3.TPOS: _number_pair(metadata.disc_number, metadata.disc_total),
            # full or partial release date
            id3.TDRC: metadata.release_date,
            # genres (ordered!)
            id3.TCON: list(metadata.genres),
        }
        for frame, value in text_frames.items():
            if value:
                self.logger.debug(
                    "Set ID3 frame %s to %r", frame.__name__, value
                )
                tags.add(frame(encoding=id3.Encoding.UTF8, text=value))

        tags.add(artwork)
        tags.save(media_path)
