# Gyomu Concept

## Repository Overview

`gyomu-concept` is a Python package responsible for building structured project models known as *Concepts*, which integrate source code analysis with human-managed knowledge to serve as a shared knowledge representation for humans and AIs. 

Its primary responsibility is constructing Directory and Package Concepts and utilizing them, along with underlying knowledge, to generate structured project documentation such as README files and LLM contexts through modular document definitions and section builders.

## Package Responsibilities

- Orchestrate the generation and translation of structured project documentation like READMEs and LLM contexts.
- Define and configure document sections, output renderers, and file path resolvers.
- Process, analyze, and manage hierarchical package and directory concepts.

## Architecture

The package is organized into several architectural areas under `src/gyomu_concept`:

- **`src/gyomu_concept/document`**: Manages overall document generation, context initialization, data models, rendering, translation, and building operations. Its sub-directory `src/gyomu_concept/document/builder` provides asynchronous builder components and functions for generating document sections and bullet lists, coordinating with translation and enablement definitions.
- **`src/gyomu_concept/llm_context/builder/section`**: Provides section builder configurations and instances for composing specific document sections, such as architecture, design principles, editing rules, constraints, navigation, overview, and responsibilities.
- **`src/gyomu_concept/directory/internal`**: Handles internal functionality for building, loading, processing, saving, and managing directory concepts and file summary records.
- **`src/gyomu_concept/package/internal`**: Provides internal utilities and mechanisms for handling package concepts, including dependency collection, path resolution, loading, saving, and processing operations.

## Design Principles

- Maintain Concepts as structured knowledge models that combine source code analysis with human-managed knowledge, functioning as an independent intermediate representation to enable reuse across multiple output formats.
- Strictly decouple Concept generation, source code analysis, and document rendering into independent responsibilities to prevent tight coupling between internal models and output-specific formats like Markdown.
- Isolate all AI execution through a dedicated compiler interface to eliminate direct dependencies on specific AI providers, models, or vendor-specific SDKs.
- Manage Concepts across different granularities, such as packages and directories, according to their respective responsibilities.
- Express document-specific definitions, such as content translation methods, within the Concept layer while avoiding the introduction of output constraints into the core Concept models.

## Important Constraints

- Do not tightly couple concept generation and Markdown rendering.
- Do not expose public APIs that directly depend on specific AI models or providers.
- Do not depend on editor- or IDE-specific features.
- Do not mix source code analysis logic into document generation processing.
- Do not introduce constraints imposed by output formats (such as Markdown) into the Concept models themselves.
- Do not introduce AI provider-specific SDKs or implementation details.

## Editing Rules

- Explicitly specify argument and return types for public APIs and primary application logic.
- Maintain type-safe implementations that comply with strict mypy settings.
- Avoid Any and suppress type checking only when necessary with limited scope and clear rationale.
- Define and validate structured data at boundaries using Pydantic models.
- Use dataclasses or appropriate data structures for internal state representation.
- Do not duplicate the same concept or constraints across multiple definitions.
- Represent expected failures explicitly using returns.Result, Success, and Failure.
- Do not use exceptions for expected failures and handle them properly at boundaries.
- Design packages with clear responsibilities and direct dependencies from upper workflows to lower functions.
- Do not introduce circular dependencies between packages.
- Depend only on public APIs of other packages rather than internal implementation details.
- Use Protocol and constructor injection to define contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities rather than speculative future abstractions.
- Implement operations without side effects as pure functions where possible.
- Separate input and output operations involving the file system, external services, and LLMs from business logic.
- Validate AI outputs using Pydantic models before use.
- Encapsulate AI provider-specific APIs and types within adapters or infrastructure boundaries.
- Separate AI execution, routing, fallback, and retry responsibilities from calling interfaces.
- Use structured data like Concepts and analysis results as inputs for document generation.
- Keep document composition, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document rather than assembling raw Markdown strings directly.
- Treat Concepts derived from source code and human-managed Knowledge as independent information sources.
- Update or add tests when observable behavior changes.
- Keep unit tests deterministic by isolating dependencies on LLMs and external services.
- Use actual temporary directories or fixtures for file system tests, and mock only uncontrollable external services.
- Align mocks with actual public interfaces without depending excessively on internal implementation details.
- Consolidate shared logic into existing packages without duplicating implementations.
- Evaluate standard libraries and existing dependencies before adding new packages.
- Follow existing naming conventions, package structures, and code styles while minimizing change scopes.
- Maintain code that passes ruff, mypy, and pytest checks.

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
