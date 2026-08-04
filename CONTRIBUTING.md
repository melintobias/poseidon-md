# Development

## Environment setup

### 1. Install Python dependencies

Poseidon-MD uses [uv](https://docs.astral.sh/uv/) for Python environment and
dependency management.

```sh
uv sync
```

### 2. Install Node.js dependencies

Poseidon-MD uses [pnpm](https://pnpm.io/) for Node.js-based development tools,
including Prettier.

```sh
pnpm install --frozen-lockfile
```

### 3. Install pre-commit hooks

Poseidon-MD uses [prek](https://prek.j178.dev/) alongside
[Ruff](https://github.com/astral-sh/ruff),
[Pyright](https://github.com/microsoft/pyright), and
[git-conventional-commits](https://github.com/qoomon/git-conventional-commits),
to manage Git hooks for code quality and commit message checks.

```sh
prek install --hook-type commit-msg --overwrite
```

> [!TIP]
> If the `prek` command is not found, a possible workaround is to install it
> manually from PyPI: <https://pypi.org/project/prek/> or using `uv`:
>
> ```sh
> uvx prek install --hook-type commit-msg --overwrite
> ```
