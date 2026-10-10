"""Stage-oriented orchestration for the media processing pipeline."""

from .extraction import ExtractionStage
from .intake import IntakeStage
from .types import PipelineStage

__all__ = [
    "ExtractionStage",
    "IntakeStage",
    "PipelineStage",
]
"""Names supported as the pipeline package's public interface."""
