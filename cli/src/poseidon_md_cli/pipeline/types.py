"""Shared blackboard state and orchestration contracts for CLI stages."""

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from logging import Logger
from typing import Any

from poseidon_md_core import Track
from poseidon_md_core.ports import SourceAcquirer
from pydantic import AnyUrl

from ..logger import LOGGER


@dataclass
class PipelineSharedStorage:
    """Shared state and services available to every pipeline stage.

    Attributes:
        input_urls: Raw URL strings supplied through the command line.
        welcome_on_no_urls: Whether intake should greet and prompt when empty.
        logger: Application logger used to report pipeline events.
        urls: URLs accepted by the intake stage.
        source_acquirer: Optional provider-neutral source acquisition service.
        tracks: Successfully acquired tracks available to later stages.
    """

    input_urls: list[str] = field(default_factory=list)
    welcome_on_no_urls: bool = field(default=True)

    logger: Logger = field(default=LOGGER)

    urls: tuple[AnyUrl, ...] = field(default_factory=tuple)
    source_acquirer: SourceAcquirer | None = None
    tracks: tuple[Track, ...] = field(default_factory=tuple)


class PipelineStage(ABC):
    """Abstract base class for a pipeline stage."""

    @abstractmethod
    def run(self, shared_storage: PipelineSharedStorage) -> Any | None:
        """Run the pipeline stage.

        Args:
            shared_storage: Shared storage for the pipeline stages.

        Returns:
            The result of the stage execution.
        """

        raise NotImplementedError("Subclasses must implement this method.")


class StageOrchestrator:
    """Run an ordered collection of stages against shared storage.

    Attributes:
        stages: Instantiated stages in their execution order.
        storage: State and services shared by the stages.
    """

    def __init__(
        self,
        stages: list[type[PipelineStage]],
        shared_storage: PipelineSharedStorage | None = None,
    ) -> None:
        """Initialize a pipeline stage sequence.

        Args:
            stages: Stage types to instantiate in execution order.
            shared_storage: Existing shared storage, or `None` to create it.
        """

        self.stages: list[PipelineStage] = [stage() for stage in stages]
        self.storage = shared_storage or PipelineSharedStorage()

    def run(self) -> None:
        """Run every configured stage in order."""

        for stage in self.stages:
            stage.run(self.storage)
