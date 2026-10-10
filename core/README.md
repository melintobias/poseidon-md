# Poseidon-MD Core

The core package contains the media pipeline, its shared models and policies,
and the integration boundaries used by services. Start with the
[pipeline overview](src/poseidon_md_core/pipeline/README.md).

Provider and tool integrations belong in `adapters`; workflow decisions belong
in `pipeline`; shared integration contracts belong in `ports`.

## Track model

`poseidon_md_core.Track` is the immutable state passed between pipeline stages.
It keeps the source, user options, metadata lifecycle, and media artifacts
together while retaining the pipeline distinctions needed for conflict
resolution.

Stages return an updated copy through the model's `with_*` and `add_*` methods.
Source acquisition returns source identity, extracted metadata, and a
downloaded artifact together. The coordinator applies those values to one
track copy before passing it to validation and external metadata stages.

```python
from poseidon_md_core import Track
from poseidon_md_core import TrackSource

track = Track(source=TrackSource(url="https://example.com/track"))
```
