"""Stage-oriented orchestration for the media processing pipeline."""

from .intake import IntakeStage
from .types import PipelineStage

__all__ = [
    "IntakeStage",
    "PipelineStage",
]
"""Names supported by the currently implemented pipeline stages."""
