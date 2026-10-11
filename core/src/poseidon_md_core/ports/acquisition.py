"""Contracts for extracting source metadata while downloading media."""

from dataclasses import dataclass
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from poseidon_md_core.models import MediaArtifact
    from poseidon_md_core.models import MetadataCandidate
    from poseidon_md_core.models import TrackSource


class SourceAcquisitionError(RuntimeError):
    """A source provider failed to produce a usable downloaded track."""


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceAcquisition:
    """Provider-neutral output from one source acquisition operation.

    Attributes:
        source: Resolved identity of the downloaded source.
        metadata: Metadata extracted from the source during acquisition.
        artifact: Local media artifact downloaded from the source.
    """

    source: TrackSource
    metadata: MetadataCandidate
    artifact: MediaArtifact


class SourceAcquirer(Protocol):
    """Extract source metadata and download media in one provider operation."""

    def acquire(self, url: str) -> SourceAcquisition:
        """Acquire one source URL.

        Args:
            url: Validated source URL to inspect and download.

        Returns:
            Extracted source identity and metadata plus the downloaded artifact.

        Raises:
            SourceAcquisitionError: If extraction or download does not produce a
                usable result.
        """
        ...
