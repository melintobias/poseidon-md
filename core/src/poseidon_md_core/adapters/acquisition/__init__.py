"""Source acquisition adapters backed by external download tools."""

from .yt_dlp import YtDlpSourceAcquirer

__all__ = ["YtDlpSourceAcquirer"]
"""Names supported as the acquisition adapter package's public interface."""
