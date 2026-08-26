# Package Architecture

## 1. Purpose

Gyomu-Python is managed as a monorepo containing multiple Python packages.

This document defines the rules for:

- Package structure and responsibilities
- Package dependencies
- Dependency direction
- Version management
- `pyproject.toml` responsibilities
- Common development tooling

The purpose is to keep the package architecture consistent as the number of packages grows.

---

# 2. Monorepo Structure

Packages are placed under the `packages/` directory.

```text
packages/
├── schema/
├── infra/
├── ai/
├── python-analysis/
└── ...
```

Each package is an independently buildable and publishable Python package.

Each package uses the `src` layout:

```text
<package>/
├── pyproject.toml
├── src/
│   └── <package_module>/
└── tests/
```

Tests are maintained separately from the `src` directory.

---

# 3. Package Responsibilities

## 3.1 schema

`schema` is the foundational package of Gyomu-Python.

It provides functionality that is shared across packages and does not depend on external I/O.

Responsibilities include:

- Pydantic schemas
- Common types
- Pure functions
- Common errors
- Result-related helper functions
- Other reusable logic that does not require external I/O

`schema` should avoid dependencies on higher-level packages.

As a general rule, other Gyomu packages may depend on `schema`.

```text
schema
  ↑
  ├── infra
  ├── ai
  ├── python-analysis
  └── ...
```

---

## 3.2 infra

`infra` provides infrastructure and I/O functionality.

Responsibilities include:

- File system operations
- CSV I/O
- Archive handling
- Database access
- Configuration access
- Logging infrastructure
- Other external I/O

`infra` may depend on `schema`.

Packages that require infrastructure or I/O functionality may depend on `infra`.

However, dependency on `infra` should only be introduced when the functionality is actually required.

---

## 3.3 ai

`ai` provides abstractions for interacting with LLMs.

The package is responsible for infrastructure surrounding LLM usage rather than application-specific AI use cases.

Responsibilities include:

- LLM abstraction
- Provider abstraction
- Retry handling
- Routing
- AI-related error handling
- Configuration required for AI execution

The initial implementation uses PydanticAI to abstract provider-specific behavior.

Application-specific AI use cases should not be implemented in this package.

`ai` may depend on `schema` and, where necessary, `infra`.

`ai` must not depend on `python-analysis`.

---

## 3.4 python-analysis

`python-analysis` provides static analysis functionality for Python source code.

Responsibilities include:

- Python source parsing
- AST analysis
- Module analysis
- Class and function analysis
- Import/dependency analysis
- Source-code metadata extraction
- Other deterministic source-code analysis

This package does not call LLMs.

Therefore, `python-analysis` must not depend on `ai`.

It may depend on:

- `schema`
- `infra`

when shared types or file/configuration I/O are required.

AI-based interpretation of analysis results belongs to a higher-level package.

---

## 3.5 Docstring-related packages

Docstring generation is implemented as a separate package.

The docstring package may depend on both:

- `python-analysis`
- `ai`

Its responsibility is to combine deterministic source-code analysis with LLM-based generation.

Conceptually:

```text
Python Source
      │
      ▼
python-analysis
      │
      │ Analysis Result
      ▼
docstring package
      ▲
      │
      │ LLM
      │
     ai
```

The `python-analysis` package itself must remain independent of AI.

---

# 4. Dependency Direction

Package dependencies must always be one-directional.

Circular dependencies are prohibited.

For example:

```text
schema
  ↑
infra
  ↑
ai
```

is valid.

The following is prohibited:

```text
schema → infra
infra → schema
```

Likewise, `ai` and `python-analysis` are sibling packages and should not depend on each other.

The intended architecture is approximately:

```text
                         schema
                       ▲   ▲   ▲
                       │   │   │
                       │   │   │
                     infra ai python-analysis
                       ▲   ▲       ▲
                       │   │       │
                       └───┴───────┘
                           │
                    docstring package
```

The exact dependency graph may grow as new packages are introduced, but dependency direction must remain acyclic.

---

# 5. Package Versioning

All Gyomu-Python packages use the same version number.

For example:

```text
gyomu-schema           0.2.0
gyomu-infra            0.2.0
gyomu-ai               0.2.0
gyomu-python-analysis  0.2.0
```

A version represents a compatible Gyomu-Python package set.

The purpose of unified versioning is:

1. To avoid requiring users to determine which individual packages need upgrading.
2. To make compatibility between Gyomu packages explicit.
3. To treat a Gyomu release as a consistent set of packages.

When the Gyomu version changes, all published Gyomu packages use the same version.

---

# 6. `pyproject.toml` Responsibilities

## 6.1 Root `pyproject.toml`

The root `pyproject.toml` contains monorepo-wide development configuration.

Examples include:

- uv workspace configuration
- pytest configuration
- Ruff configuration
- mypy configuration
- coverage configuration
- Common development dependencies

Development tools should generally be managed at the repository root rather than duplicated in individual packages.

For example:

```toml
[dependency-groups]
dev = [
    "mypy>=2.3.1",
    "pytest>=9,<10",
    "ruff>=0.16.3",
]
```

Package-specific development dependencies should only be introduced when they are genuinely specific to that package.

---

## 6.2 Package `pyproject.toml`

Each package has its own `pyproject.toml`.

It contains information required to build and publish the package and information relevant to package users.

This includes:

- Package name
- Version
- Description
- Supported Python versions
- Runtime dependencies
- Build system configuration

For example:

```toml
[project]
name = "gyomu-schema"
version = "0.1.0"
description = "Gyomu canonical schemas"
requires-python = ">=3.14"
dependencies = [
    "pydantic>=2,<3",
    "returns>=0.29.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Package-specific uv configuration may also be defined here.

For example:

```toml
[tool.uv.sources]
gyomu-schema = { workspace = true }
```

or:

```toml
[tool.uv.scripts]
schema-gen = "python scripts/schema_gen.py"
```

---

# 7. Development Tooling

Python type safety is treated as an important part of the Gyomu-Python architecture.

Gyomu-Python aims to provide type safety comparable to the TypeScript implementation.

## 7.1 mypy

`mypy` is used with strict mode.

```toml
[tool.mypy]
python_version = "3.14"
strict = true
plugins = ["returns.contrib.mypy.returns_plugin"]
```

The following principles apply:

- Public APIs must be fully typed.
- Function arguments and return values should be explicitly typed.
- `Any` should be avoided.
- `cast()` should be used only when necessary.
- `# type: ignore` should be avoided and justified when required.
- Generic types and `Protocol` should be used where appropriate.

Static typing and runtime validation have separate responsibilities.

- `mypy`: static type safety
- `Pydantic`: runtime data validation

---

## 7.2 Ruff

Ruff is used for linting and formatting.

The root configuration is the common configuration for all packages.

Package-specific exclusions should be minimized.

Generated code and other exceptional paths may be excluded where necessary.

---

## 7.3 Testing

Tests are maintained under each package's `tests/` directory.

Unit and integration tests are separated:

```text
tests/
├── unit/
├── integration/
└── resources/
```

This structure is used consistently across packages.

---

# 8. Package Dependencies

Runtime dependencies are declared in each package's `pyproject.toml`.

For example:

```toml
[project]
dependencies = [
    "gyomu-schema>=...",
]
```

When developing inside the monorepo, workspace dependencies are declared using uv workspace sources:

```toml
[tool.uv.sources]
gyomu-schema = { workspace = true }
```

Package development tools such as pytest, mypy, and Ruff are managed centrally at the repository root unless a package has a specific requirement.

---

# 9. Build Artifacts

Build artifacts are generated during the build process and are not committed to Git.

Typical artifacts include:

```text
dist/
├── *.whl
└── *.tar.gz
```

These artifacts are generated locally or by CI and are published to PyPI as part of the release process.

---

# 10. Legacy Packaging Configuration

The project uses `pyproject.toml` as the primary packaging configuration.

Legacy configuration files such as the following should not be used:

- `setup.py`
- `setup.cfg`
- `requirements.txt`
- `.pylintrc`

Runtime dependencies are managed through package `pyproject.toml` files and the uv lock file.

Development tools are managed through the root `pyproject.toml`.

Ruff replaces Pylint as the project's linting tool.

---

# 11. Design Principles

The following principles should be maintained as the project grows.

1. **Dependencies are one-directional.**
2. **Circular package dependencies are prohibited.**
3. **`schema` remains independent of external I/O.**
4. **AI-specific functionality belongs in `ai`.**
5. **Deterministic Python source analysis belongs in `python-analysis`.**
6. **Python source analysis must not depend on AI.**
7. **AI-based use cases are implemented in higher-level packages.**
8. **All Gyomu packages share the same version.**
9. **Common development tooling is managed at the monorepo root.**
10. **Package-specific build and runtime information is managed by each package.**
11. **Python type safety is treated as a first-class design concern.**
12. **Public APIs should be explicitly typed and intentionally exposed.**
