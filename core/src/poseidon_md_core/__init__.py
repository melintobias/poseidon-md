"""Public interface for the Poseidon-MD core package."""

from .models import MediaArtifact
from .models import MetadataCandidate
from .models import MetadataLookupResult
from .models import MetadataLookupStatus
from .models import MetadataProvenance
from .models import MetadataRecord
from .models import Track
from .models import TrackArtifacts
from .models import TrackMetadata
from .models import TrackOptions
from .models import TrackSource

__all__ = [
    "MediaArtifact",
    "MetadataCandidate",
    "MetadataLookupResult",
    "MetadataLookupStatus",
    "MetadataProvenance",
    "MetadataRecord",
    "Track",
    "TrackArtifacts",
    "TrackMetadata",
    "TrackOptions",
    "TrackSource",
]
"""Names supported as the core package's public interface."""
