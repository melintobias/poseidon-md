"""Tests for selecting the pipeline's audio and thumbnail formats."""

from posidon_cli.main import app
from posidon_cli.options import OutputFormat
from posidon_cli.options import ThumbnailFormat
from posidon_cli.pipeline.types import StageOrchestrator
import pytest
from typer.testing import CliRunner


@pytest.mark.parametrize("args", [[], ["--output-format", "mp3"]])
def test_cli_configures_mp3_output(
    args: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pass an MP3 format to the pipeline by default and on explicit input."""
    formats: list[OutputFormat] = []

    def capture_format(orchestrator: StageOrchestrator) -> None:
        """Record the format passed by the CLI without running the stages."""
        formats.append(orchestrator.storage.options.output_format)

    monkeypatch.setattr(StageOrchestrator, "run", capture_format)

    result = CliRunner().invoke(app, args)

    assert result.exit_code == 0, result.output
    assert len(formats) == 1
    assert formats[0] is OutputFormat.MP3


def test_cli_rejects_unsupported_output_format() -> None:
    """Reject unsupported format values during command-line parsing."""
    result = CliRunner().invoke(app, ["--output-format", "wav", "--no-prompt"])

    assert result.exit_code != 0
    assert "Invalid value" in result.output
    assert "wav" in result.output
    assert "mp3" in result.output


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        ([], ThumbnailFormat.ORIGINAL),
        (["--thumbnail-format", "jpg"], ThumbnailFormat.JPG),
        (["--thumbnail-format", "png"], ThumbnailFormat.PNG),
        (["--thumbnail-format", "webp"], ThumbnailFormat.WEBP),
    ],
)
def test_cli_configures_thumbnail_format(
    args: list[str], expected: ThumbnailFormat, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pass the default or selected thumbnail format to the pipeline.

    Args:
        args: Command-line options for this run.
        expected: Enum member the pipeline should receive.
        monkeypatch: Fixture for intercepting the pipeline before retrieval.
    """
    formats: list[ThumbnailFormat] = []

    def capture_format(orchestrator: StageOrchestrator) -> None:
        """Record the format passed by the CLI without downloading a track.

        Args:
            orchestrator: Pipeline configured by the command.
        """
        formats.append(orchestrator.storage.options.thumbnail_format)

    monkeypatch.setattr(StageOrchestrator, "run", capture_format)

    result = CliRunner().invoke(app, args)

    assert result.exit_code == 0, result.output
    (actual,) = formats
    assert actual is expected


def test_cli_rejects_unsupported_thumbnail_format() -> None:
    """Reject an unsupported image format during command-line parsing."""
    result = CliRunner().invoke(
        app, ["--thumbnail-format", "bmp", "--no-prompt"]
    )

    assert result.exit_code != 0
    assert "Invalid value" in result.output
    assert "--thumbnail-format" in result.output
    assert "bmp" in result.output
