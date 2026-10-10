# Pipeline

The core pipeline package contains provider-independent validation and the
shared domain models used by application-level orchestration. Concrete source
providers belong in `adapters`; command-line presentation belongs in the CLI
package.

`validate_url` parses one source URL and returns `None` for invalid input. The
CLI intake stage uses this function before deduplicating accepted URLs.
