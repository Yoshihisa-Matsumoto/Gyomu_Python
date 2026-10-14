# Gyomu Schema

## Repository Overview

The `gyomu-schema` package provides canonical data schemas, type definitions, error types, protocols, and general-purpose utilities shared across the Gyomu system. Its primary responsibility is to define data contracts passed between Gyomu's functional domains—including Python analysis, concepts, documents, knowledge, and snapshots. By establishing these shared data contracts, the package maintains type safety and data consistency while keeping inter-package dependencies loosely coupled.

## Package Responsibilities

- Define canonical schemas and data models for Python code structures, AST analysis, and type representation.
- Provide validation rules, translation instructions, and structured models for documents and sections.
- Define domain-specific error handling and recovery strategy models.
- Offer shared utility functions for serialization, timing, results wrapping, and filesystem operations.

## Architecture

The package is organized into two primary architectural areas located under `src/gyomu_schema/`: domain-specific schemas (`src/gyomu_schema/schemas/`) and core error handling (`src/gyomu_schema/error`).

The `src/gyomu_schema/schemas/` directory branches into three structural domains:
- **`src/gyomu_schema/schemas/python`**: Defines data models and analysis schemas for Python code structures, symbols, modules, files, and project configuration. Within this area, `src/gyomu_schema/schemas/python/type` defines schema models and union types specifically for representing Python AST expressions, statements, and type structures to support AST and type analysis.
- **`src/gyomu_schema/schemas/document`**: Contains schemas, data structures, validation rules, and translation strategies for structured documents, sections, and content elements such as paragraphs, lists, code blocks, and tables.
- **`src/gyomu_schema/schemas/knowledge`**: Defines schemas for structuring and representing knowledge domains, including coding guidelines, operational knowledge, package usage, roadmaps, and technical integration references.

The `src/gyomu_schema/error` directory operates independently as the core error-handling layer, defining base errors, domain-specific error classes for AI, configuration, database, I/O, validation, and timeouts, along with retry and resolution strategies.

## Design Principles

- Centralized Data Contracts: Define shared data contracts for multiple packages exclusively within this package, using Pydantic schemas for external boundaries (JSON, persistence, MCP) to ensure consistent validation, serialization, and metadata richness for code and knowledge generation.
- Strong Typing for Value Semantics: Represent identifiers, paths, and meaningful values as distinct types wherever possible to prevent parameter mix-ups and enforce domain constraints statically.
- Strict Separation of Protocols and Implementations: Define interfaces as Protocols separated from concrete implementations to control dependency directions and avoid coupling to specific implementations or business logic.
- Strict Independence and Architectural Boundaries: Maintain a reusable shared foundation by depending solely on Pydantic, Returns, and the Python standard library, strictly prohibiting dependencies on other Gyomu packages, infrastructure-specific code, or LLM logic.

## Important Constraints

- Do not depend on external libraries other than Pydantic, Returns, and the Python standard library.
- Do not depend on other packages under `gyomu`.
- Do not implement Gyomu-specific business logic.
- Do not place processing specific to particular applications or packages.
- Do not provide infrastructure-specific implementations.
- Do not implement AI model execution or LLM-specific processing.

## Editing Rules

- Explicitly specify argument and return types for public APIs and primary application logic.
- Maintain type-safe implementations compatible with strict mypy settings.
- Avoid Any and type-checking suppression; limit their scope and reason when necessary.
- Define and validate structured data at external boundaries, JSON, YAML, and persistent storage using Pydantic models.
- Use dataclasses or appropriate data structures for internal state representation.
- Do not duplicate the same data structures or constraints in multiple locations.
- Represent expected application failures explicitly using returns.Result, Success, and Failure.
- Handle expected failures via return types rather than relying heavily on exceptions, and process exceptions at boundaries.
- Design packages with clear responsibilities and direct dependencies from upper workflows to lower functions.
- Do not introduce circular dependencies between packages.
- Depend only on public APIs of other packages rather than internal implementation details.
- Use Protocols and constructor injection to define contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities and changes rather than speculative future abstractions.
- Implement side-effect-free logic as pure functions wherever possible.
- Separate input/output operations involving the filesystem, external services, and LLMs from business logic.
- Validate AI outputs using Pydantic models before use.
- Encapsulate AI-provider-specific APIs and types within adapters and infrastructure boundaries.
- Separate AI execution, routing, fallback, and retry responsibilities behind clean interfaces.
- Use structured data such as concepts and analysis results as inputs for documentation generation.
- Treat document structure, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document instead of assembling Markdown strings directly.
- Treat derived code concepts and human-managed knowledge as independent information sources.
- Update tests when observable behavior changes.
- Keep unit tests deterministic by isolating dependencies on LLMs and external services.
- Use actual temporary directories or fixtures for filesystem tests, mocking only external service dependencies.
- Mock dependencies based on public interfaces rather than internal implementation details or call counts.
- Consolidate shared logic into existing packages without duplication.
- Evaluate standard libraries and existing dependencies before adding new dependency packages.
- Follow existing naming conventions, package structure, and code style.
- Pass all repository linters and type checkers including ruff, mypy, and pytest.

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
