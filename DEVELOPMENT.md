# Development

## Environment setup

### 1. Install dependencies

Poseidon-MD uses [uv](https://docs.astral.sh/uv/) for Python environment and
dependency management.

```bash
uv sync
```

### 2. Install pre-commit hooks

Poseidon-MD adheres to the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
specification for commit messages. We use [prek](https://prek.j178.dev/)
alongside [git-conventional-commits](https://github.com/qoomon/git-conventional-commits)
and [Ruff](https://github.com/astral-sh/ruff) to manage Git hooks for code
squality and commit message checks.

```bash
prek install --hook-type commit-msg --overwrite
```

> [!TIP]
> If the `prek` command is not found, a possible workaround is to install it
> manually from PyPI: <https://pypi.org/project/prek/> or using `uv`:
>
> ```bash
> uvx prek install --hook-type commit-msg --overwrite
> ```
