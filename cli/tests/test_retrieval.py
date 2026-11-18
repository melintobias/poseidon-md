"""Tests for post-processing artifacts in the retrieval stage."""

# cspell:words IHDR xerror rawvideo

import re
import shutil
import subprocess  # noqa: S404
from typing import TYPE_CHECKING

from posidon_cli.options import CliOptions
from posidon_cli.options import ThumbnailFormat
from posidon_cli.pipeline.retrieval import RetrievalStage
from posidon_cli.pipeline.types import PipelineSharedStorage
from posidon_core.models import Track
from pydantic import AnyUrl
import pytest
from yt_dlp import YoutubeDL

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    ("thumbnail_format", "expected_header"),
    [
        (ThumbnailFormat.JPG, rb"\xff\xd8\xff"),
        (ThumbnailFormat.PNG, rb"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR"),
        (ThumbnailFormat.WEBP, rb"RIFF....WEBP"),
    ],
    ids=["jpeg", "png", "webp"],
)
def test_thumbnail_postprocessor_encodes_requested_format(
    tmp_path: Path, thumbnail_format: ThumbnailFormat, expected_header: bytes
) -> None:
    """Produce a decodable image with the requested format's binary header.

    Args:
        tmp_path: Per-test directory for input and converted thumbnails.
        thumbnail_format: Target encoding configured on the retrieval stage.
        expected_header: Byte pattern at the start of the encoded output.
    """
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        pytest.skip("FFmpeg is required for thumbnail conversion")

    # A 2 by 2 red image in binary PPM forces conversion for every target.
    source = tmp_path / "cover.ppm"
    source.write_bytes(b"P6\n2 2\n255\n" + b"\xff\x00\x00" * 4)
    track = Track(url=AnyUrl("https://example.com/track"))
    track.artifacts.tmp_directory = tmp_path
    storage = PipelineSharedStorage(
        options=CliOptions(thumbnail_format=thumbnail_format)
    )
    info = {
        # Thumbnail records available after download.
        "thumbnails": [
            {
                "url": source.as_uri(),  # Source URL for yt-dlp's reporting.
                "filepath": str(source),  # Local input to the postprocessor.
            }
        ]
    }
    options = RetrievalStage.get_ytdlp_options(storage, track)
    # yt-dlp's stubs narrow the option and info mappings used at runtime.
    with YoutubeDL(options) as ydl:  # pyright: ignore[reportArgumentType]
        processed_info, _ = ydl.pre_process(
            info,  # pyright: ignore[reportArgumentType]
            key="before_dl",
            files_to_move={str(source): str(source)},
        )
        output = RetrievalStage.get_thumbnail_path(ydl, processed_info)

    image = output.read_bytes()
    assert re.match(expected_header, image, re.DOTALL), image[:16].hex(" ")

    # Read from stdin so the decoder cannot infer the format from a filename.
    decoded = subprocess.run(  # noqa: S603
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-xerror",
            "-i",
            "pipe:0",
            "-frames:v",
            "1",
            "-pix_fmt",
            "rgb24",
            "-f",
            "rawvideo",
            "pipe:1",
        ],
        input=image,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert decoded.returncode == 0, decoded.stderr.decode(errors="replace")
    assert len(decoded.stdout) == 2 * 2 * 3
