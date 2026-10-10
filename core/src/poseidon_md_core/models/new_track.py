from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True, slots=True, kw_only=True)
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
        track_number: One-based position on the disc.
        track_total: Total number of tracks on the disc.
        disc_number: One-based disc position in the release.
        disc_total: Total number of discs in the release.
        release_date: Full or partial release date supplied by a provider.
        genres: Ordered genre labels.
        isrc: International Standard Recording Code.
        duration_seconds: Track duration in seconds.
        artwork_url: URL of the selected artwork.
        provenance: Provider selection details for resolved fields.
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


@dataclass(frozen=True, slots=True, kw_only=True)
class Track:
    """Immutable track aggregate passed between media pipeline modules.

    Attributes:
        source: Source URL and provider identity.
        options: Stable processing intent supplied by the user.
        metadata: Metadata state accumulated across relevant stages.
        artifacts: Downloaded, transformed, and stored media references.
        id: Stable identifier retained by every updated copy of the track.
    """

    metadata: TrackMetadata = field(default_factory=TrackMetadata)
