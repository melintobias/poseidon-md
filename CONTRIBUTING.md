# Contributing

## Project documentation

Start with the [documentation index](docs/README.md) for the pipeline and core
package architecture.

## Style guides

Posidon follows the [Google style guides](https://google.github.io/styleguide/).
Python code follows the
[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
Ruff enforces parts of it, such as Google-style docstrings and import ordering.

Treat the guides as sensible defaults rather than strict rules, and use your
own judgement when applying them. Departing from a guideline is fine when it
makes the code clearer or more consistent with the code around it.

## Environment setup

### 1. Install Python dependencies

Posidon uses [uv](https://docs.astral.sh/uv/) for Python environment and
dependency management.

```sh
uv sync --all-packages
```

The `--all-packages` option installs both the CLI and core workspace members,
including their declared dependencies.

### 2. Install Node.js dependencies

Posidon uses [pnpm](https://pnpm.io/) for Node.js-based development tools,
including Prettier.

```sh
pnpm install --frozen-lockfile
```

### 3. Install pre-commit hooks

Posidon uses [prek](https://prek.j178.dev/) alongside
[Ruff](https://github.com/astral-sh/ruff),
[Pyright](https://github.com/microsoft/pyright), and
[git-conventional-commits](https://github.com/qoomon/git-conventional-commits),
to manage Git hooks for code quality and commit message checks.

```sh
prek install --hook-type commit-msg --overwrite
```

> [!TIP]
> If the `prek` command is not found, a possible workaround is to install it
> manually from [PyPI](https://pypi.org/project/prek/) or using `uv`:
>
> ```sh
> uvx prek install --hook-type commit-msg --overwrite
> ```

## Running tests

Posidon uses [pytest](https://docs.pytest.org/) to test the CLI and core
workspace members. Each member keeps its tests in its own `tests` directory.

```sh
uv run pytest
```
