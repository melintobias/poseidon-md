"""Shared blackboard state and orchestration contracts for CLI stages."""

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING

from poseidon_md_cli.logger import LOGGER

if TYPE_CHECKING:
    from logging import Logger

    from poseidon_md_core import Track
    from poseidon_md_core.ports import SourceAcquirer
    from pydantic import AnyUrl


@dataclass
class PipelineSharedStorage:
    """Shared state and services available to every pipeline stage.

    Attributes:
        input_urls: Raw URL strings supplied through the command line.
        no_prompt: Whether to exit when no URLs are provided, instead of
            prompting for input.
        logger: Application logger used to report pipeline events.
        urls: URLs accepted by the intake stage.
        source_acquirer: Optional provider-neutral source acquisition service.
        tracks: Successfully acquired tracks available to later stages.
    """

    input_urls: list[str] = field(default_factory=list)
    no_prompt: bool = field(default=False)

    logger: Logger = field(default=LOGGER)

    urls: tuple[AnyUrl, ...] = field(default_factory=tuple)
    source_acquirer: SourceAcquirer | None = None
    tracks: tuple[Track, ...] = field(default_factory=tuple)


class PipelineStage(ABC):
    """Abstract base class for a pipeline stage."""

    @abstractmethod
    def run(self, shared_storage: PipelineSharedStorage) -> None:
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
        stages: Stage classes in their execution order.
        storage: State and services shared by the stages.
    """

    def __init__(
        self,
        stages: list[type[PipelineStage]],
        shared_storage: PipelineSharedStorage | None = None,
    ) -> None:
        """Initialize a pipeline stage sequence.

        The stage list is shallow-copied, so later edits to the caller's list do
        not change this orchestrator's sequence.

        Args:
            stages: Stage classes to instantiate in execution order.
            shared_storage: Existing shared storage, or `None` to create it.
        """
        self.stages = list(stages)
        self.storage = shared_storage or PipelineSharedStorage()

    def run(self) -> None:
        """Run every configured stage in order."""
        for stage in self.stages:
            stage().run(self.storage)
