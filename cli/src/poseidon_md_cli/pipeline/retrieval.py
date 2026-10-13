"""Retrieve and process downloaded media and metadata."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import logging
from pathlib import Path
from typing import cast, TYPE_CHECKING

from rich import progress
from yt_dlp import YoutubeDL

from poseidon_md_cli.logger import CONSOLE
from poseidon_md_cli.logger import log_stage_completion
from poseidon_md_cli.models.yt_dlp import DownloadArtifact
from poseidon_md_cli.pipeline.types import PipelineStage

if TYPE_CHECKING:
    from poseidon_md_core.models import Track
    from pydantic import AnyUrl

    from poseidon_md_cli.pipeline.types import PipelineSharedStorage


class RetrievalStage(PipelineStage):
    """Retrieve and process downloaded media and metadata."""

    @classmethod
    def run(cls, storage: PipelineSharedStorage) -> None:
        """Run all retrieval steps against shared pipeline storage.

        Args:
            storage: Existing pipeline storage.
        """
        logger = storage.logger
        tracks = storage.tracks

        tracked_tracks = progress.track(
            tracks, description="Track retrieval", console=CONSOLE
        )

        for index, track in enumerate(tracked_tracks, start=1):
            logger.info(
                "Retrieving track %d/%d: %s", index, len(tracks), track.url
            )

            options = cls.get_ytdlp_options(track)
            with YoutubeDL(options) as ydl:
                download_artifact = cls.download_track(ydl, track.url)
                track.apply_download_artifact(download_artifact)

                logger.debug(
                    "Downloaded media to %s, metadata to %s, "
                    "and thumbnail to %s",
                    download_artifact.media_path,
                    download_artifact.metadata_path,
                    download_artifact.thumbnail_path,
                )

        log_stage_completion(logger, logging.INFO, "Track retrieval completed")

    @staticmethod
    def download_track(ydl: YoutubeDL, url: AnyUrl) -> DownloadArtifact:
        """Download one URL and collect its media, metadata, and thumbnail.

        Args:
            ydl: Configured yt-dlp downloader used for this track.
            url: Source URL to download.

        Returns:
            Artifact containing the downloaded media, metadata, and thumbnail
            paths.

        Raises:
            TypeError: If yt-dlp does not return an information mapping.
        """
        info = ydl.extract_info(str(url), download=True)
        if not isinstance(info, Mapping):
            msg = f"yt-dlp returned no item information for {url}"
            raise TypeError(msg)

        return DownloadArtifact(
            metadata_path=RetrievalStage.get_metadata_path(ydl, info),
            thumbnail_path=RetrievalStage.get_thumbnail_path(ydl, info),
            media_path=RetrievalStage.get_media_path(info),
        )

    @staticmethod
    def get_metadata_path(ydl: YoutubeDL, info: Mapping[str, object]) -> Path:
        """Return the metadata JSON path.

        Raises:
            ValueError: If yt-dlp provides no metadata path.
        """
        filepath = info.get("infojson_filename") or ydl.prepare_filename(
            info, "infojson"
        )
        if not isinstance(filepath, str) or not filepath:
            raise ValueError("yt-dlp returned no metadata filepath")
        return Path(filepath)

    @staticmethod
    def get_thumbnail_path(ydl: YoutubeDL, info: Mapping[str, object]) -> Path:
        """Return the downloaded thumbnail path, resolving yt-dlp's file move.

        Args:
            ydl: Configured downloader, used to resolve a moved thumbnail.
            info: yt-dlp result for the downloaded item.

        Raises:
            TypeError: If yt-dlp provides no thumbnail filepath.
        """
        thumbnails = cast(
            "Sequence[Mapping[str, object]]", info.get("thumbnails", ())
        )
        path = next(
            filter(None, (item.get("filepath") for item in thumbnails)), None
        )
        if not isinstance(path, str):
            raise TypeError("yt-dlp returned no downloaded thumbnail filepath")
        path = Path(path)
        if path.exists():
            return path
        return Path(ydl.prepare_filename(info, "thumbnail")).with_suffix(
            path.suffix
        )

    @staticmethod
    def get_media_path(info: Mapping[str, object]) -> Path:
        """Return the post-processed media path, falling back to the download.

        Raises:
            ValueError: If no media path is available.
        """
        requested = cast(
            "Sequence[Mapping[str, object]]",
            info.get("requested_downloads") or (),
        )
        filepath = info.get("filepath") or next(
            filter(None, (item.get("filepath") for item in requested)), None
        )
        filepath = filepath or info.get("_filename")
        if not isinstance(filepath, str) or not filepath:
            raise ValueError("yt-dlp returned no downloaded media filepath")
        return Path(filepath)

    @staticmethod
    def get_ytdlp_options(track: Track) -> dict[str, object]:
        """Build yt-dlp options for MP3 audio and per-track sidecars.

        Returns:
            Python API options for the requested outputs.
        """
        return {
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",  # Extract audio.
                    "preferredcodec": "mp3",  # Convert output to MP3.
                }
            ],  # Extract audio as MP3.
            "writeinfojson": True,  # Write metadata JSON.
            "writethumbnail": True,  # Download thumbnail.
            "format": "bestaudio/best",  # Prefer audio, allow combined media.
            "outtmpl": "%(title)s.%(ext)s",  # Template for media filename.
            "noplaylist": True,  # Treat one URL as one track.
            "quiet": True,  # Suppress routine output.
            "no_warnings": True,  # Suppress warning output.
            "paths": {"home": str(track.tmp_directory)},  # Track output dir.
        }
