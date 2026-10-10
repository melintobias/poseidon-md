# Ports

Ports define the capabilities required by the core pipeline, such as source
inspection, media download, metadata lookup, media transformation, temporary
artifact handling, and durable storage. They keep workflow decisions
independent of vendors and tools.

`SourceAcquirer` combines source inspection and media download into one
operation because download tools resolve the media formats and request details
during extraction. It returns provider-neutral `SourceAcquisition` values so
orchestrators can replace the integration without changing pipeline logic.
