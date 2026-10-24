# Repository instructions

## Begin with the project documentation

- Before planning or changing code, read the root `README.md`,
  `CONTRIBUTING.md`, and every README or design document governing the area
  being changed. Follow relevant links from those documents before making
  architectural or workflow decisions.
- Use the repository documentation and configuration as the source of truth for
  tool selection. In particular, consult `pyproject.toml` and `uv.lock` for
  Python work, `package.json` and `pnpm-lock.yaml` for Node.js work, and
  `prek.toml` for repository checks. Do not substitute a different package
  manager, formatter, linter, type checker, or test runner without an explicit
  request.
- Read the nearest subtree `README.md` before adding a file or choosing its
  location. Preserve the documented boundaries between packages, pipeline
  stages, adapters, observability, models, ports, and tests.
- If documentation, configuration, and implementation disagree, call out the
  mismatch. Reconcile it as part of the change when that is clearly in scope;
  otherwise, ask before making a decision that changes project behavior.
- Update the affected documentation in the same change whenever commands,
  behavior, public interfaces, or architectural boundaries change.

## Document every code element

- Give every module, package, class, protocol, enum, exception, function,
  method, property, callback, fixture, and nested definition a meaningful
  docstring. This requirement applies to public and private code, tests, and
  short helpers; visibility and brevity are not exemptions.
- Document every constant, type alias, enum member, dataclass or model field,
  protocol attribute, and structured mapping key. Do not rely on the name or
  type annotation alone to explain its meaning.
- In Python, give each element a Google-style docstring, consistent with the
  Ruff configuration. Describe purpose and semantics, then include `Args:`,
  `Returns:`, `Yields:`, and `Raises:` sections whenever they convey useful
  contract information.
- For module and class constants, place an explanatory string immediately
  after the assignment so documentation tools can treat it as an attribute
  docstring.
- For dataclasses and similar models, document every field in the class
  docstring's `Attributes:` section. For `TypedDict` and other dictionary
  schemas, document every permitted key in an `Attributes:` section. For a
  significant untyped mapping literal, add an adjacent comment for every key.
- For type aliases, place an explanatory string immediately after the alias.
  State the concept represented by the type and any constraints that are not
  expressible in its annotation.
- Keep each docstring accurate when code changes. Explain intent, units,
  invariants, side effects, ownership, and edge cases where applicable.
- Do not edit the root `README.md` unless explicitly told to.

## Verify changes

- Use the checks and commands documented by the repository and the nearest
  relevant README.
- Run the narrowest relevant checks while iterating, then the broader
  repository-configured checks appropriate to the files changed.
- Report checks that were run and any checks that could not be run.
- Refuse to merge changes that fail checks or introduce new warnings, unless the
  change is explicitly intended to do so.
