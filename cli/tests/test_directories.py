"""Tests for locating the music directory of each platform."""

from typing import TYPE_CHECKING

from posidon_cli.directories import get_music_directory
import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the home directory at a temporary path and clear XDG overrides.

    `Path.home` reads `USERPROFILE` on Windows and `HOME` elsewhere, so both
    variables are replaced to keep the tests independent of the host.

    Args:
        tmp_path: Per-test temporary directory used as the home directory.
        monkeypatch: Fixture restoring the environment after the test.

    Returns:
        The temporary home directory.
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.delenv("XDG_MUSIC_DIR", raising=False)
    return tmp_path


@pytest.mark.parametrize("platform", ["win32", "darwin", "linux", "freebsd14"])
def test_music_directory_defaults_to_home_music(
    platform: str, home: Path
) -> None:
    """Use the home directory's `Music` folder without an XDG override."""
    assert get_music_directory(platform) == home / "Music"


@pytest.mark.parametrize("platform", ["linux", "freebsd14"])
def test_xdg_platforms_honor_music_directory_variable(
    platform: str, home: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Prefer `XDG_MUSIC_DIR` on Linux and unlisted POSIX platforms."""
    monkeypatch.setenv("XDG_MUSIC_DIR", str(home / "Tunes"))

    assert get_music_directory(platform) == home / "Tunes"


@pytest.mark.parametrize("platform", ["win32", "darwin"])
def test_non_xdg_platforms_ignore_music_directory_variable(
    platform: str, home: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Keep the `Music` folder on platforms that don't use XDG directories."""
    monkeypatch.setenv("XDG_MUSIC_DIR", str(home / "Tunes"))

    assert get_music_directory(platform) == home / "Music"


def test_blank_music_directory_variable_is_ignored(
    home: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fall back to the `Music` folder when `XDG_MUSIC_DIR` is blank."""
    monkeypatch.setenv("XDG_MUSIC_DIR", "  ")

    assert get_music_directory("linux") == home / "Music"
