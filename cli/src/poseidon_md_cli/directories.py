"""Locate the platform directories used by the command-line interface."""

import os
from pathlib import Path
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def _home_music_directory() -> Path:
    """Return the `Music` folder in the user's home directory.

    Windows and macOS create this folder for every user by default.

    Returns:
        Path to `Music` in the home directory, whether or not it exists.

    Raises:
        RuntimeError: If the home directory cannot be determined.
    """
    return Path.home() / "Music"


def _xdg_music_directory() -> Path:
    """Return the XDG music directory used by Linux and other POSIX desktops.

    A non-blank `XDG_MUSIC_DIR` environment variable takes precedence over the
    `Music` folder in the user's home directory.

    Returns:
        Path to the music directory, whether or not it exists.

    Raises:
        RuntimeError: If `XDG_MUSIC_DIR` is unset or blank and the home
            directory cannot be determined.
    """
    configured = os.environ.get("XDG_MUSIC_DIR", "").strip()
    return Path(configured) if configured else _home_music_directory()


_MUSIC_DIRECTORIES: dict[str, Callable[[], Path]] = {
    # Windows keeps the Music known folder in the user profile by default.
    "win32": _home_music_directory,
    # macOS keeps the Music folder in each user's home directory.
    "darwin": _home_music_directory,
    # Linux desktops follow the XDG user directory conventions.
    "linux": _xdg_music_directory,
}
"""Music directory resolvers keyed by `sys.platform` identifier."""


def get_music_directory(platform: str = sys.platform) -> Path:
    """Return the conventional music directory of a platform.

    Platforms without an entry in `_MUSIC_DIRECTORIES` use the XDG music
    directory. This covers the BSDs, whose identifiers include a version
    number, such as `freebsd14`.

    Args:
        platform: `sys.platform` identifier of the platform to look up.
            Defaults to the running platform.

    Returns:
        Path to the platform's music directory, which may not exist.

    Raises:
        RuntimeError: If the directory depends on a home directory that
            cannot be determined.
    """
    return _MUSIC_DIRECTORIES.get(platform, _xdg_music_directory)()
