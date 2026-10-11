"""Domain state passed between media pipeline stages."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from dataclasses import replace
from enum import StrEnum
from pathlib import Path
from typing import Self
from uuid import UUID
from uuid import uuid4


def _require_non_blank(value: str, field_name: str) -> None:
    """Reject a required string containing no visible characters.

    Args:
            value: String to validate.
            field_name: Human-readable field name used in the error message.

    Raises:
            ValueError: If `value` is blank.
    """
    if not value.strip():
        raise ValueError(f"{field_name} must not be blank")


def _validate_optional_non_blank(value: str | None, field_name: str) -> None:
    """Reject a present optional string when it is blank.

    Args:
            value: Optional string to validate.
            field_name: Human-readable field name used in the error message.

    Raises:
            ValueError: If `value` is present but blank.
    """
    if value is not None:
        _require_non_blank(value, field_name)


@dataclass(frozen=True, slots=True, kw_only=True)
class TrackSource:
    """Location and provider identity of the source track.

    Attributes:
            url: Original URL submitted for the track.
            normalized_url: Canonical URL produced by the intake stage, if known.
            provider: Source adapter selected for the URL, if known.
            source_id: Provider-specific stable identifier, if known.
    """

    url: str
    normalized_url: str | None = None
    provider: str | None = None
    source_id: str | None = None

    def __post_init__(self) -> None:
        """Validate required and optional source identifiers.

        Raises:
                ValueError: If a supplied source value is blank.
        """
        _require_non_blank(self.url, "source URL")
        _validate_optional_non_blank(
            self.normalized_url,
            "normalized source URL",
        )
        _validate_optional_non_blank(self.provider, "source provider")
        _validate_optional_non_blank(self.source_id, "source ID")

    @property
    def effective_url(self) -> str:
        """Return the normalized URL when one is available.

        Returns:
                The normalized URL, or the original URL before normalization.
        """
        return self.normalized_url or self.url


@dataclass(frozen=True, slots=True, kw_only=True)
class TrackOptions:
    """User intent that remains stable while a track is processed.

    Attributes:
            output_format: Requested output container or file format.
            quality: Adapter-independent quality preset, if supplied.
            output_directory: Requested destination directory, if supplied.
            embed_metadata: Whether resolved tags should be embedded in outputs.
            embed_artwork: Whether selected artwork should be embedded in outputs.
            overwrite: Whether existing destination files may be replaced.
            keep_temporary_files: Whether intermediate artifacts should be retained.
    """

    output_format: str = "mp3"
    quality: str | None = None
    output_directory: Path | None = None
    embed_metadata: bool = True
    embed_artwork: bool = True
    overwrite: bool = False
    keep_temporary_files: bool = False

    def __post_init__(self) -> None:
        """Validate textual processing options.

        Raises:
                ValueError: If the output format or supplied quality is blank.
        """
        _require_non_blank(self.output_format, "output format")
        _validate_optional_non_blank(self.quality, "quality")


@dataclass(frozen=True, slots=True, kw_only=True)
class MetadataProvenance:
    """Provider selected for one resolved metadata field.

    Attributes:
            field_name: Name of the resolved field.
            provider: Provider from which the selected value originated.
            confidence: Optional score in the inclusive range 0 through 1.
    """

    field_name: str
    provider: str
    confidence: float | None = None

    def __post_init__(self) -> None:
        """Validate provenance identity and confidence.

        Raises:
            ValueError: If names are blank or confidence is outside 0 through 1.
        """
        _require_non_blank(self.field_name, "metadata field name")
        _require_non_blank(self.provider, "metadata provider")
        _validate_confidence(self.confidence)


@dataclass(frozen=True, slots=True, kw_only=True)
class MetadataRecord:
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
    provenance: tuple[MetadataProvenance, ...] = ()


def _validate_positive(value: int | None, field_name: str) -> None:
    """Validate an optional one-based integer.

    Args:
            value: Optional number to validate.
            field_name: Human-readable field name used in the error message.

    Raises:
            ValueError: If `value` is less than one.
    """
    if value is not None and value < 1:
        raise ValueError(f"{field_name} must be positive")


def _validate_clean_metadata(metadata: MetadataRecord) -> None:
    """Validate semantics required of cleaned and resolved metadata.

    Args:
            metadata: Record crossing a validated pipeline boundary.

    Raises:
            ValueError: If numbering is not positive or duration is negative.
    """
    _validate_positive(metadata.track_number, "track number")
    _validate_positive(metadata.track_total, "track total")
    _validate_positive(metadata.disc_number, "disc number")
    _validate_positive(metadata.disc_total, "disc total")
    if metadata.duration_seconds is not None and metadata.duration_seconds < 0:
        raise ValueError("duration must not be negative")


def _validate_confidence(confidence: float | None) -> None:
    """Validate an optional normalized confidence score.

    Args:
            confidence: Optional score expected in the inclusive range 0 through 1.

    Raises:
            ValueError: If `confidence` is outside the permitted range.
    """
    if confidence is not None and not 0 <= confidence <= 1:
        raise ValueError("metadata confidence must be between 0 and 1")


@dataclass(frozen=True, slots=True, kw_only=True)
class MetadataCandidate:
    """Metadata supplied by a source or external provider.

    Attributes:
        provider: Stable name of the provider that supplied the values.
        metadata: Provider-independent metadata values.
        confidence: Optional candidate score in the inclusive range 0 through 1.
    """

    provider: str
    metadata: MetadataRecord
    confidence: float | None = None

    def __post_init__(self) -> None:
        """Validate candidate provider and confidence.

        Raises:
                ValueError: If the provider is blank or confidence is invalid.
        """
        _require_non_blank(self.provider, "metadata provider")
        _validate_confidence(self.confidence)


class MetadataLookupStatus(StrEnum):
    """Outcome of an attempted external metadata lookup.

    Attributes:
            SUCCEEDED: Provider returned at least one candidate.
            NO_MATCH: Provider completed successfully without a candidate.
            FAILED: Provider lookup failed before producing a usable candidate.
    """

    SUCCEEDED = "succeeded"
    """The provider returned at least one candidate."""
    NO_MATCH = "no_match"
    """The provider completed successfully without a candidate."""
    FAILED = "failed"
    """The provider failed before producing a usable candidate."""


@dataclass(frozen=True, slots=True, kw_only=True)
class MetadataLookupResult:
    """Result of one external provider lookup.

    The absence of a result for a provider means that it was not attempted.

    Attributes:
            provider: Stable name of the queried external provider.
            status: Outcome of the provider attempt.
            candidates: Candidates returned by a successful lookup.
            error: Safe diagnostic message retained for a failed lookup.
    """

    provider: str
    status: MetadataLookupStatus
    candidates: tuple[MetadataCandidate, ...] = ()
    error: str | None = None

    def __post_init__(self) -> None:
        """Validate consistency among status, candidates, and error.

        Raises:
                ValueError: If the provider is blank or result fields conflict.
        """
        _require_non_blank(self.provider, "metadata provider")
        _validate_optional_non_blank(self.error, "metadata lookup error")

        if any(
            candidate.provider != self.provider for candidate in self.candidates
        ):
            raise ValueError("lookup candidates must match the lookup provider")
        if (
            self.status is MetadataLookupStatus.SUCCEEDED
            and not self.candidates
        ):
            raise ValueError("a successful lookup must contain a candidate")
        if (
            self.status is not MetadataLookupStatus.SUCCEEDED
            and self.candidates
        ):
            raise ValueError("only a successful lookup may contain candidates")
        if self.status is MetadataLookupStatus.FAILED and self.error is None:
            raise ValueError("a failed lookup must describe its error")
        if (
            self.status is not MetadataLookupStatus.FAILED
            and self.error is not None
        ):
            raise ValueError("only a failed lookup may contain an error")

    @classmethod
    def succeeded(
        cls,
        provider: str,
        candidates: tuple[MetadataCandidate, ...],
    ) -> Self:
        """Create a successful provider result.

        Args:
                provider: Stable name of the queried provider.
                candidates: Nonempty candidates returned by the provider.

        Returns:
                A validated successful lookup result.

        Raises:
                ValueError: If candidates are empty or belong to another provider.
        """
        return cls(
            provider=provider,
            status=MetadataLookupStatus.SUCCEEDED,
            candidates=candidates,
        )

    @classmethod
    def no_match(cls, provider: str) -> Self:
        """Create a result for a provider that found no candidates.

        Args:
                provider: Stable name of the queried provider.

        Returns:
                A validated no-match lookup result.
        """
        return cls(provider=provider, status=MetadataLookupStatus.NO_MATCH)

    @classmethod
    def failed(cls, provider: str, error: str) -> Self:
        """Create a failed result without retaining an exception object.

        Args:
                provider: Stable name of the queried provider.
                error: Safe diagnostic message describing the failure.

        Returns:
                A validated failed lookup result.

        Raises:
                ValueError: If the provider or error is blank.
        """
        return cls(
            provider=provider,
            status=MetadataLookupStatus.FAILED,
            error=error,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class TrackMetadata:
    """Metadata accumulated through extraction and reconciliation.

    Attributes:
            extracted: Candidate extracted directly from the source URL.
            cleaned: Validated and normalized form of the source candidate.
            external_results: Latest attempted result for each external provider.
            resolved: Canonical metadata selected during reconciliation.
    """

    extracted: MetadataCandidate | None = None
    cleaned: MetadataCandidate | None = None
    external_results: tuple[MetadataLookupResult, ...] = ()
    resolved: MetadataRecord | None = None

    def __post_init__(self) -> None:
        """Validate metadata states that can be constructed directly.

        Raises:
                ValueError: If providers repeat or validated records are invalid.
        """
        providers = tuple(result.provider for result in self.external_results)
        if len(providers) != len(set(providers)):
            raise ValueError("external metadata providers must be unique")
        if self.cleaned is not None:
            _validate_clean_metadata(self.cleaned.metadata)
        if self.resolved is not None:
            _validate_clean_metadata(self.resolved)

    @property
    def candidates(self) -> tuple[MetadataCandidate, ...]:
        """Return the best source candidate followed by external candidates.

        Returns:
                The cleaned source candidate when available, otherwise the extracted
                candidate, followed by successful external candidates.
        """
        source_candidate = self.cleaned or self.extracted
        external_candidates = tuple(
            candidate
            for result in self.external_results
            for candidate in result.candidates
        )
        if source_candidate is None:
            return external_candidates
        return (source_candidate, *external_candidates)

    def with_external_result(self, result: MetadataLookupResult) -> Self:
        """Add or replace the latest result for one external provider.

        Args:
                result: Completed external metadata lookup result.

        Returns:
                A new metadata state containing the provider's latest result.
        """
        results = list(self.external_results)
        for index, existing in enumerate(results):
            if existing.provider == result.provider:
                results[index] = result
                break
        else:
            results.append(result)
        return replace(self, external_results=tuple(results))


@dataclass(frozen=True, slots=True, kw_only=True)
class MediaArtifact:
    """Reference to a downloaded, transformed, or stored media file.

    Attributes:
            path: Local filesystem path represented by the artifact, if applicable.
            uri: Durable or remote storage URI, if applicable.
            format: Media container or file format, if known.
            mime_type: Media MIME type, if known.
            checksum: Content checksum including its algorithm convention, if known.
    """

    path: Path | None = None
    uri: str | None = None
    format: str | None = None
    mime_type: str | None = None
    checksum: str | None = None

    def __post_init__(self) -> None:
        """Validate optional textual artifact descriptors.

        Raises:
                ValueError: If no location exists or a descriptor is blank.
        """
        if self.path is None and self.uri is None:
            raise ValueError("a media artifact must have a path or URI")
        _validate_optional_non_blank(self.uri, "media URI")
        _validate_optional_non_blank(self.format, "media format")
        _validate_optional_non_blank(self.mime_type, "media MIME type")
        _validate_optional_non_blank(self.checksum, "media checksum")

    @property
    def location(self) -> str:
        """Return the preferred portable artifact location.

        Returns:
                The remote URI when present, otherwise the local path as text.
        """
        if self.uri is not None:
            return self.uri
        if self.path is None:
            raise RuntimeError("validated artifact has no location")
        return str(self.path)


@dataclass(frozen=True, slots=True, kw_only=True)
class TrackArtifacts:
    """Media artifacts produced while processing a track.

    Attributes:
            downloaded: Temporary artifact retrieved from the source.
            transformed: Verified artifacts produced by media transformation.
            stored: Final artifacts published to durable storage.
    """

    downloaded: MediaArtifact | None = None
    transformed: tuple[MediaArtifact, ...] = ()
    stored: tuple[MediaArtifact, ...] = ()


def _without_published_outputs(artifacts: TrackArtifacts) -> TrackArtifacts:
    """Clear transformed and stored artifacts after upstream state changes.

    Args:
            artifacts: Current artifact state.

    Returns:
            Artifact state retaining only the source download, when present.
    """
    return replace(artifacts, transformed=(), stored=())


@dataclass(frozen=True, slots=True, kw_only=True)
class Track:
    """Immutable aggregate passed between media pipeline modules.

    Attributes:
            source: Source URL and provider identity.
            options: Stable processing intent supplied by the user.
            metadata: Metadata state accumulated across relevant stages.
            artifacts: Downloaded, transformed, and stored media references.
            id: Stable identifier retained by every updated copy of the track.
    """

    source: TrackSource
    options: TrackOptions = field(default_factory=TrackOptions)
    metadata: TrackMetadata = field(default_factory=TrackMetadata)
    artifacts: TrackArtifacts = field(default_factory=TrackArtifacts)
    id: UUID = field(default_factory=uuid4)

    def with_source(self, source: TrackSource) -> Self:
        """Return a copy containing updated source information.

        Args:
            source: Source state produced by URL normalization or extraction.

        Returns:
            A new track retaining its identity while clearing dependent state.
        """
        return replace(
            self,
            source=source,
            metadata=TrackMetadata(),
            artifacts=TrackArtifacts(),
        )

    def with_extracted_metadata(self, candidate: MetadataCandidate) -> Self:
        """Return a copy containing metadata extracted from the source.

        Args:
            candidate: Metadata candidate returned by the source adapter.

        Returns:
            A new track containing the candidate with later state cleared.
        """
        return replace(
            self,
            metadata=TrackMetadata(extracted=candidate),
            artifacts=TrackArtifacts(),
        )

    def with_cleaned_metadata(self, candidate: MetadataCandidate) -> Self:
        """Return a copy containing validated and cleaned source metadata.

        Args:
            candidate: Validated and normalized source candidate.

        Returns:
            A new track containing the candidate with later state cleared.

        Raises:
            ValueError: If the candidate violates cleaned metadata invariants.
        """
        _validate_clean_metadata(candidate.metadata)
        return replace(
            self,
            metadata=TrackMetadata(
                extracted=self.metadata.extracted,
                cleaned=candidate,
            ),
            artifacts=_without_published_outputs(self.artifacts),
        )

    def with_external_metadata(self, result: MetadataLookupResult) -> Self:
        """Return a copy containing an external metadata lookup result.

        Args:
                result: Completed result from one external provider.

        Returns:
                A new track containing the result with later outputs cleared.
        """
        metadata = self.metadata.with_external_result(result)
        return replace(
            self,
            metadata=replace(metadata, resolved=None),
            artifacts=_without_published_outputs(self.artifacts),
        )

    def with_resolved_metadata(self, metadata: MetadataRecord) -> Self:
        """Return a copy containing the canonical resolved metadata.

        Args:
                metadata: Canonical record selected during reconciliation.

        Returns:
                A new track containing the record with later outputs cleared.

        Raises:
                ValueError: If the record violates resolved metadata invariants.
        """
        _validate_clean_metadata(metadata)
        return replace(
            self,
            metadata=replace(self.metadata, resolved=metadata),
            artifacts=_without_published_outputs(self.artifacts),
        )

    def with_downloaded_artifact(self, artifact: MediaArtifact) -> Self:
        """Return a copy containing the downloaded source artifact.

        Args:
                artifact: Media reference returned by the downloader.

        Returns:
                A new track containing the download with later outputs cleared.
        """
        return replace(
            self,
            artifacts=TrackArtifacts(downloaded=artifact),
        )

    def add_transformed_artifact(self, artifact: MediaArtifact) -> Self:
        """Return a copy with an additional transformed artifact.

        Args:
                artifact: Verified media reference produced by transformation.

        Returns:
                A new track with the artifact appended in production order.
        """
        return replace(
            self,
            artifacts=replace(
                self.artifacts,
                transformed=(*self.artifacts.transformed, artifact),
            ),
        )

    def add_stored_artifact(self, artifact: MediaArtifact) -> Self:
        """Return a copy with an additional stored artifact.

        Args:
                artifact: Final reference returned by durable storage.

        Returns:
                A new track with the artifact appended in storage order.
        """
        return replace(
            self,
            artifacts=replace(
                self.artifacts,
                stored=(*self.artifacts.stored, artifact),
            ),
        )
