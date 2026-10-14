"""Shared blackboard state and orchestration contracts for CLI stages."""

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING

from poseidon_md_cli.logger import LOGGER
from poseidon_md_cli.options import CliOptions

if TYPE_CHECKING:
    from logging import Logger

    from poseidon_md_core.models import Track
    from pydantic import AnyUrl


@dataclass
class PipelineSharedStorage:
    """Shared state and services available to every pipeline stage.

    Attributes:
        options: Command settings and source URLs available to stages.
        logger: Application logger used to report pipeline events.
        urls: URLs accepted by the intake stage.
        tracks: Successfully acquired tracks available to later stages.
    """

    options: CliOptions = field(default_factory=CliOptions)
    logger: Logger = field(default=LOGGER)

    urls: tuple[AnyUrl, ...] = field(default_factory=tuple)
    tracks: tuple[Track, ...] = field(default_factory=tuple)


class PipelineStage(ABC):
    """Abstract base class for a pipeline stage."""

    @abstractmethod
    def run(self, storage: PipelineSharedStorage) -> None:
        """Run the pipeline stage.

        Args:
            storage: Shared storage for the pipeline stages.

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
        storage: PipelineSharedStorage | None = None,
    ) -> None:
        """Initialize a pipeline stage sequence.

        The stage list is shallow-copied, so later edits to the caller's list do
        not change this orchestrator's sequence.

        Args:
            stages: Stage classes to instantiate in execution order.
            storage: Existing shared storage, or `None` to create it.
        """
        self.stages = list(stages)
        self.storage = storage or PipelineSharedStorage()

    def run(self) -> None:
        """Run every configured stage in order."""
        for stage in self.stages:
            stage().run(self.storage)
