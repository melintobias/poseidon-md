# Adapters

Adapters connect ports to concrete URL providers, metadata services,
downloaders, media processors, and storage backends. Organize implementations
by capability first and provider second.

The `acquisition` capability contains `YtDlpSourceAcquirer`. It uses one
`extract_info(..., download=True)` call per URL, prefers an audio-only source,
and maps the completed result to core source, metadata, and artifact models.
