# Gyomu Concept

## Repository Overview

`gyomu-concept` is a core Python package responsible for analyzing project structures, managing directory and package concepts, and generating structured documentation. Its primary role is to construct structured project models—termed Concepts—by combining insights from source code analysis with human-managed knowledge. 

Serving as a shared knowledge representation for both humans and AI systems, the package provides a modular framework for document building, translation, section assembly, and markdown rendering. It handles the creation of Directory and Package Concepts and utilizes this underlying knowledge model to generate structured documentation such as project README files and LLM contexts, supported by domain-specific error handling.

## Package Responsibilities

- Coordinate the generation, translation, and rendering of project documentation like READMEs and LLM contexts.
- Manage directory and package concepts through building, processing, dependency collection, and persistence operations.
- Provide domain-specific error management and phase classifications for robust application error handling.

## Architecture

The package is structured into core functional areas under `src/gyomu_concept/`:

*   **`src/gyomu_concept/document`**: Serves as the central component for documentation processes. It initializes base contexts, defines models, renderers, and output configurations, and coordinates building, translation, and rendering. It relies on the nested `src/gyomu_concept/document/builder` directory, which asynchronously builds document sections and bullet lists utilizing translation and enablement definitions.
*   **`src/gyomu_concept/directory/internal`**: Manages internal operations for directory concepts and file summary records, handling building, loading, processing, saving, and path management.
*   **`src/gyomu_concept/package/internal`**: Handles internal package concept mechanisms through collaborative loading, saving, processing, path resolution, and dependency collection.
*   **`src/gyomu_concept/error`**: Provides domain-specific exception handling, defining error classes that relate to concept phases for classifying execution errors.

## Design Principles

- Treat concepts as structured knowledge models that combine source code analysis with human-managed knowledge, independent of specific document formats or output languages to enable multi-purpose reuse.
- Maintain strict separation of concerns among source code analysis, concept construction, and document generation to prevent logic coupling and support varied granularities like packages and directories.
- Isolate AI execution by routing all interactions through gyomu-ai-compiler, prohibiting direct dependencies on AI providers, provider-specific SDKs, or models while defining document-specific execution rules within concepts.
- Enforce architectural boundaries that prevent output-format constraints, such as Markdown rendering specifics, from leaking into the core concept models.

## Important Constraints

- Do not tightly couple Concept generation with Markdown rendering.
- Do not expose APIs that depend directly on specific AI models or providers.
- Do not depend on editor- or IDE-specific features.
- Do not mix source code analysis logic into document generation processing.
- Do not introduce constraints specific to output formats (such as Markdown) into Concepts themselves.
- Do not introduce AI provider-specific SDKs or implementation details.

## Editing Rules

- Explicitly specify argument and return types for public APIs and primary application logic.
- Maintain type-safe implementations compatible with strict mypy settings.
- Limit the use of Any and type-checking suppression, restricting their scope and rationale when necessary.
- Define and validate structured data for JSON, YAML, persisted data, and external boundaries using explicit schemas such as Pydantic models.
- Use appropriate data structures like dataclasses for representing internal state.
- Avoid duplicating data structures or constraints of the same concept across multiple places.
- Express expected application failures explicitly using returns.Result, Success, and Failure.
- Handle exceptions at boundaries rather than using them to implicitly communicate expected operational failures.
- Design packages with clear responsibilities and direct dependencies from upper workflows to lower functions.
- Do not introduce circular dependencies between packages.
- Interact with other packages exclusively through their public APIs rather than internal implementation details.
- Use Protocols and constructor injection to specify contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities and changes rather than speculating on future usage.
- Implement side-effect-free logic as pure functions whenever possible.
- Separate input and output operations involving the file system, external services, or LLMs from business logic.
- Treat AI outputs as untrusted input and validate them with Pydantic models before use.
- Confine dependencies on AI-provider-specific APIs and types to appropriate adapters and infrastructure boundaries.
- Design interfaces that separate AI execution, routing, fallback, and retry from the caller's implementation details.
- Use structured data such as concepts and analysis results as inputs for documentation generation.
- Treat document composition, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document rather than building Markdown strings directly.
- Treat code-derived concepts and human-managed knowledge as independent information sources.
- Avoid duplicating design knowledge across multiple management locations and reference the appropriate information source.
- Update or add corresponding tests when observable behavior changes.
- Keep unit tests deterministic and isolate dependencies on LLMs and external services.
- Use actual temporary directories or fixtures for file system and project structure tests, mocking only controlled dependencies like external services.
- Align mock dependencies with actual public interfaces without over-relying on internal call counts or implementation details.
- Consolidate shareable logic into existing packages without duplicating implementations.
- Evaluate standard libraries and existing dependencies before adding new dependency packages.
- Follow existing naming conventions, package structures, and code styles while keeping change scopes minimal.
- Maintain passing states for quality checks and tests including ruff, mypy, and pytest.

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
