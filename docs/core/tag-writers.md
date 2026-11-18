# Tag Writers

`TagWriter` is a format-agnostic [port](ports.md) for updating an existing media
file in place. Its `write` method accepts the media path, parsed `TrackMetadata`,
and a local artwork path. The writer applies populated metadata fields and
embeds the image as the front cover using the file format's tagging conventions.

Implementations live in the
[tagging adapters](../../core/src/poseidon_md_core/adapters/tagging), and the CLI
selects a writer for the requested output format. For `mp3`, the CLI uses
`Mp3TagWriter`, which manages Mutagen audio objects for each write and saves
the metadata and cover artwork together in one ID3 update.
