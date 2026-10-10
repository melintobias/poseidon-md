# Pipeline

This directory contains the CLI-level stages that coordinate media
processing. Stage modules own their part of workflow orchestration while core
providers remain behind ports and adapters.

The intake stage validates supplied URLs with the core validation helper and
keeps the first occurrence of each valid URL. It reports accepted, duplicate,
and rejected values through the CLI logger. Terminal output should reuse
`poseidon_md_cli.styles` and the shared console and logger in
`poseidon_md_cli.logger`. The intake module keeps URL validation independent
of its terminal presentation. Pipeline stages receive the application logger
through shared storage. Normal events are logged at the info level, skipped
inputs at the warning level, and per-input diagnostic events are enabled with
the CLI's `--debug` option.
