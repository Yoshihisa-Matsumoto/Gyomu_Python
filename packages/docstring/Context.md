# Gyomu Docstring

## Repository Overview

Gyomu-docstring is a core package that provides a docstring management infrastructure for Python source code within Gyomu. Its primary responsibility is to parse docstrings into structured document information, express updates as structured Update Plans, and safely apply verified changes back to the source code. 

By separating docstring analysis, update planning, and change application, the package achieves reproducible and maintainable code document management. It automates generation, updating, merging, and validation by building code contexts, planning symbol updates with retry support, rendering structured docstring components, and validating resulting code through external formatters and linters.

## Package Responsibilities

- Manage and execute docstring updates and merges for Python files.
- Build structured contexts and plans for declarations requiring documentation.
- Render and format docstring sections, lines, and tags.
- Validate updated code sources and handle update-specific errors.

## Architecture

The `src/gyomu_docstring` package is organized into several structural areas that manage docstring updates, rendering, validation, and error handling.

- **`src/gyomu_docstring`**: Serves as the core package root, coordinating file updates, merges, rendering, validation, and error handling.
- **`src/gyomu_docstring/update`**: Manages the creation, execution, rendering, and validation of file updates and merges. Its planning processes depend on building update and merge plans, rendering docstrings, and validating sources.
- **`src/gyomu_docstring/update/docstring`**: Manages docstring updates by providing data structures and plans for modeling lines, sections, merging, and rendering symbol docstrings.
- **`src/gyomu_docstring/update/internal`**: Contains internal utilities responsible for building file and declaration contexts, constructing and overriding update and merge plans with retry support, rendering docstring elements, and validating plans and signatures.
- **`src/gyomu_docstring/error`**: Provides specialized error handling and exception definitions, specifically defining `UpdateError` for failures occurring during the docstring update process.

## Design Principles

- Manage docstrings as structured artifacts aligned with source code to ensure safe reuse across downstream processes.
- Enforce a strict separation of concerns between docstring analysis, AI generation, and file application processes, preventing tight coupling of generation logic and file updates.
- Require an explicit update plan to be generated and verified before applying any docstring modifications, prohibiting unconditional overrides and unverified changes.
- Standardize file operations around normalized path models to guarantee consistent document updates across monorepo and complex project structures without depending on specific directory layouts or build methods.
- Maintain architectural independence from specific AI providers and models to ensure long-term flexibility and maintainability.

## Important Constraints

- Do not execute docstring updates without analyzing source code.
- Do not overwrite existing docstrings unconditionally.
- Do not apply docstring changes without going through an Update Plan.
- Do not couple document generation logic with file update processing.
- Do not depend on specific directory structures or build systems.
- Do not depend directly on specific AI providers or models.

## Editing Rules

- Explicitly specify argument and return types for public APIs and primary application logic.
- Maintain type-safe implementations compatible with strict mypy settings.
- Avoid Any and type-checking suppression, limiting their scope and justification when necessary.
- Define and validate JSON, YAML, persisted data, and boundary-crossing structured data using explicit Pydantic schemas.
- Use appropriate data structures like dataclasses for internal state representation.
- Avoid defining the same data structures or constraints redundantly in multiple places.
- Express expected application failures explicitly using returns.Result, Success, and Failure.
- Avoid using exceptions for ordinary expected failures, and handle exceptions appropriately at boundaries.
- Design packages with clear responsibilities and unidirectional dependencies from workflows to lower-level features.
- Do not introduce circular dependencies between packages.
- Interact with other packages strictly through their public APIs rather than internal implementation details.
- Utilize Protocol and constructor injection to specify contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities and changes rather than speculative future abstractions.
- Implement side-effect-free logic as pure functions wherever possible.
- Separate input/output operations involving the file system, external services, or LLMs from business logic.
- Treat AI outputs as untrusted data and validate them with Pydantic models before use.
- Confine AI provider-specific APIs and types to appropriate adapters and infrastructure boundaries.
- Design interfaces that isolate AI execution, routing, fallback, and retry from the calling code.
- Use structured data such as concepts and analysis results as inputs for documentation generation.
- Treat document structure, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document instead of directly assembling Markdown strings.
- Treat source-code-derived concepts and human-managed knowledge as independent information sources.
- Update tests when observable behavior changes.
- Keep unit tests deterministic and isolate dependencies on LLMs and external services.
- Use actual temporary directories or fixtures for file system and project structure tests, mocking only necessary external dependencies.
- Align mock dependencies with actual public interfaces rather than over-relying on internal implementation details or call counts.
- Consolidate shared logic into existing appropriate packages instead of duplicating it.
- Evaluate standard libraries and existing dependencies before adding new dependency packages.
- Follow existing naming conventions, package structures, and code styles while keeping change scopes minimal.
- Maintain a state that passes repository-defined checks and tests such as ruff, mypy, and pytest.
- Do not depend directly on internal implementations of other packages.
- Do not mix the responsibilities of analysis, concept generation, document generation, and rendering unnecessarily.
- Do not introduce unnecessary abstractions or commonalities based solely on future possibilities.

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
