# Pipeline

The core pipeline package contains provider-independent validation and the
shared domain models used by application-level orchestration. The CLI package
handles command-line presentation and currently uses yt-dlp directly in
`RetrievalStage`.

`validate_url` parses one source URL and returns `None` for invalid input. The
CLI intake stage uses this function before deduplicating accepted URLs.

The CLI's `--output-format` option controls audio conversion and selects the
[tag writer](../core/tag-writers.md). The CLI currently supports `mp3` and uses
it by default. `RetrievalStage` produces the audio, a metadata file, and a
thumbnail. `TaggingStage` logs invalid metadata and skips tagging that track.
For valid metadata, it applies tags and artwork with the selected writer and
stores the metadata on the track after the write succeeds. `MovingStage` then
moves the media file into the output directory and clears its temporary path.

The CLI's `--thumbnail-format` option chooses the image encoding for the
embedded front cover. It accepts `original` (the default), `jpg`, `png`, and
`webp`. For example, `uv run posidon --thumbnail-format jpg "<source-url>"`
uses yt-dlp and FFmpeg to convert the downloaded thumbnail to JPEG before
tagging. The option only controls the image encoding. Spotify Local Files
may also need smaller artwork.

The CLI's `--output-dir` (`-o`) option chooses the output directory. Without
it, the CLI uses the platform's music directory: `~/Music` on Windows and
macOS, and `$XDG_MUSIC_DIR` or `~/Music` on Linux and other POSIX platforms.
`get_music_directory` looks these up in a mapping keyed by `sys.platform`.
After URL validation, the intake stage checks that the directory exists. If
the chosen directory or the music directory is missing, it logs a warning
naming the `--output-dir` option and uses the current working directory
instead.
