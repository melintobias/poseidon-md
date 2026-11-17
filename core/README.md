# Poseidon-MD Core

The core package contains the media pipeline, its shared models and policies,
and the integration boundaries used by services. Start with the
[pipeline overview](src/poseidon_md_core/pipeline/README.md).

Provider and tool integrations belong in `adapters`; workflow decisions belong
in `pipeline`; shared integration contracts belong in `ports`.
