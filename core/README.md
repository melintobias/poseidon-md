# Poseidon-MD Core

The core package contains the media pipeline, its shared models and policies,
and the integration boundaries used by services. Start with the
[pipeline overview](src/poseidon_md_core/pipeline/README.md).

Provider and tool integrations belong in `adapters`; workflow decisions belong
in `pipeline`; shared integration contracts belong in `ports`.

The MP3 tag writer lives in `adapters/tagging` and implements the
[`TagWriter` port](src/poseidon_md_core/ports/README.md). It owns the Mutagen
audio objects for each write. `Track` carries the metadata and artifact paths
between stages.
