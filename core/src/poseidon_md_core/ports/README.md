# Ports

Ports define the capabilities required by the core pipeline, such as source
inspection, media download, metadata lookup, media transformation, temporary
artifact handling, and durable storage. They keep workflow decisions
independent of vendors and tools.

`SourceAcquirer` combines source inspection and media download into one
operation because download tools resolve the media formats and request details
during extraction. It returns provider-neutral `SourceAcquisition` values so
orchestrators can replace the integration without changing pipeline logic.

`TagWriter.write` accepts an existing media path, parsed `TrackMetadata`, and a
local artwork path. It updates populated tags and embeds front cover artwork in
the media file. The CLI uses `Mp3TagWriter` to apply both in one ID3 save.
