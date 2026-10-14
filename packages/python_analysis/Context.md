# Gyomu Python Analysis

## Repository Overview

`gyomu-python-analysis` serves as the Python source code analysis foundation for Gyomu. Its primary responsibility is to analyze Python projects and workspaces, extracting source code structures, declarations, and dependencies into a structured analysis model. 

The package manages analysis targets and configurations consistently through Project Context and Workspace Context. By treating analysis results and project states as reusable formats, it establishes a common analysis infrastructure utilized by upper layers such as Concept, Facts, and Docstring.

## Package Responsibilities

- Analyze Python source code structures, metadata, and dependencies.
- Manage project workspaces, configuration, and module discovery.
- Generate and compare project snapshots to track code evolution.
- Provide AST-based parsing utilities for statements, expressions, and symbols.

## Architecture

The package is structured hierarchically around two primary architectural areas located under `src/gyomu_python_analysis/`: `analysis` and `snapshot`.

The `src/gyomu_python_analysis/snapshot` directory manages project-level state, handling project snapshots, file enumeration, difference computation, change analysis, validation, and workspace management.

The `src/gyomu_python_analysis/analysis` directory provides core project initialization, workspace discovery, configuration parsing, module loading, caching, and metadata registration. It contains the `analyzers` component (`src/gyomu_python_analysis/analysis/analyzers`), which extracts structure and metadata from Python code elements—such as classes, functions, variables, types, decorators, imports, docstrings, and dependencies—while maintaining symbol context and dependency resolution.

Within `analyzers`, specialized sub-components handle specific granular constructs:
- `src/gyomu_python_analysis/analysis/analyzers/ast` provides AST-based code analysis, statement and expression evaluation, and builds symbol, class, and function indexes.
- `src/gyomu_python_analysis/analysis/analyzers/expression` delegates and processes various Python expressions (including constants, subscripts, dictionaries, arrays, literals, type expressions, tuples, sets, and expression names) and parses literal values.

## Design Principles

- Derive analysis results deterministically from source code and project settings using unified path resolution rules and centralized Python analysis logic to prevent upper layers from depending directly on external parsing implementation details.
- Separate project and source file analyses into independent responsibilities managed consistently through Project Context and Workspace Context while maintaining clear project boundaries and source roots.
- Provide analysis results exclusively as read-only structured models and persist project states as immutable snapshots, strictly separating analysis from upper-layer processing such as document updates, code modifications, and AI-driven reasoning.

## Important Constraints

- Do not rewrite source code.
- Do not generate, update, or apply documentation such as READMEs, design documents, or docstrings.
- Do not implement AI-based inference or semantic analysis.
- Do not introduce project-specific analysis logic into the common analysis infrastructure.
- Do not expose implementation details of Python analysis libraries as part of the upper layer's public API.
- Do not implement application-specific decision logic using analysis results.
- Do not couple analysis processing with documentation update processing.

## Editing Rules

- Explicitly specify argument and return types for public APIs and primary application logic.
- Maintain type-safe implementations compatible with strict mypy settings.
- Avoid Any or suppressing type checkers, limiting their scope and justification when necessary.
- Define and validate JSON, YAML, persisted data, and boundary-crossing structured data using explicit Pydantic models.
- Use dataclasses or appropriate data structures for internal state representation.
- Do not duplicate data structures or constraints representing the same concept in multiple places.
- Express expected application failures explicitly using returns.Result, Success, and Failure.
- Avoid using exceptions for expected failures, and handle exceptions appropriately at boundaries.
- Design package dependencies to flow from higher-level workflows to lower-level features without circular dependencies.
- Depend only on public APIs of other packages rather than internal implementation details.
- Use Protocols and constructor injection to specify contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities and changes rather than speculative future abstractions.
- Implement stateless logic as pure functions whenever possible.
- Separate I/O operations involving the file system, external services, or LLMs from business logic.
- Validate AI outputs with Pydantic models before using them as untrusted inputs.
- Encapsulate AI provider-specific APIs and types within adapters or infrastructure boundaries.
- Design AI interfaces to isolate execution, routing, fallback, and retry responsibilities from callers.
- Use structured data like Concepts and analysis results as inputs for document generation.
- Treat document composition, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document instead of directly assembling Markdown strings.
- Treat code-derived Concepts and human-managed Knowledge as independent information sources.
- Update tests when observable behavior changes.
- Keep unit tests deterministic by isolating dependencies on LLMs and external services.
- Use actual temporary directories or fixtures for file system tests, mocking only external service dependencies.
- Base mocks on public interfaces rather than internal implementation details or call counts.
- Consolidate shared logic into existing packages without duplicating implementations.
- Evaluate standard libraries and existing dependencies before adding new dependency packages.
- Follow existing naming conventions, package structures, and code styles while minimizing change scopes.
- Maintain code that passes all project-defined checks and tests such as ruff, mypy, and pytest.

## Navigation

This document provides a high-level overview of the package concept, responsibilities, and design decisions.

For more detailed information, refer to the following documents:



- **Architecture Documentation**
  Describes the internal architecture, major components, dependencies, and design decisions of this package.

- **API Reference**
  Describes public APIs, exported modules, and usage patterns.

- **Technical Documentation**
  Describes technical details, configuration, dependencies, and implementation-specific information.

- **Development Guide**
  Describes development workflows, coding conventions, testing strategies, and contribution guidelines.

- **Project Knowledge**
  Contains additional knowledge maintained by developers, including constraints, rationale, terminology, and operational guidelines.


When modifying this package, review the relevant documentation before making changes to preserve the intended responsibilities and architectural boundaries.
