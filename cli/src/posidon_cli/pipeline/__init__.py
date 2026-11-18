"""Stage-oriented orchestration for the media processing pipeline."""

from .intake import IntakeStage
from .moving import MovingStage
from .retrieval import RetrievalStage
from .tagging import TaggingStage
from .types import PipelineStage

__all__ = [
    "IntakeStage",
    "MovingStage",
    "PipelineStage",
    "RetrievalStage",
    "TaggingStage",
]
"""Names supported as the pipeline package's public interface."""
