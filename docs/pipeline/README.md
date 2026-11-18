# Pipeline

The core pipeline package contains provider-independent validation and the
shared domain models used by application-level orchestration. The CLI package
handles command-line presentation and currently uses yt-dlp directly in
`RetrievalStage`.

`validate_url` parses one source URL and returns `None` for invalid input. The
CLI intake stage uses this function before deduplicating accepted URLs.

The CLI's `--output-format` option controls audio conversion and tag writing.
It defaults to `mp3`, the only supported format. `RetrievalStage` produces
the audio, a metadata file, and a thumbnail. `TaggingStage` logs invalid
metadata and skips tagging that track. For valid metadata, it selects the
`TagWriter` for the output format and stores the metadata on the track after
the write succeeds. `MovingStage` then moves the media file into the output
directory and clears its temporary path.

The CLI's `--output-dir` (`-o`) option chooses the output directory. Without
it, the CLI uses the platform's music directory: `~/Music` on Windows and
macOS, and `$XDG_MUSIC_DIR` or `~/Music` on Linux and other POSIX platforms.
`get_music_directory` looks these up in a mapping keyed by `sys.platform`.
After URL validation, the intake stage checks that the directory exists. If
the chosen directory or the music directory is missing, it logs a warning
naming the `--output-dir` option and uses the current working directory
instead.
