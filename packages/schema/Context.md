# Gyomu Schema

## Repository Overview

The `gyomu-schema` package acts as the foundational layer providing canonical data models, structural schemas, validation rules, protocols, error types, and generic utilities shared across the Gyomu project. Its primary responsibility is to define data contracts—covering Python AST analysis, concepts, documents, knowledge bases, and snapshots—passed between various Gyomu features. By establishing these shared data contracts, the package maintains type safety and data consistency while keeping inter-package dependencies loosely coupled.

## Package Responsibilities

- Define canonical data schemas and type models for Python code analysis, structured documentation, and project knowledge.
- Provide standardized error definitions, fault-tolerance options, and retry resolution strategies.
- Offer helper utilities and validation routines for data serialization, format conversion, and execution monitoring.

## Architecture

The package is structurally organized under `src/gyomu_schema` into distinct schema and error-handling areas:

*   **`src/gyomu_schema/schemas/python`**: Defines data models for Python code structure analysis, covering classes, functions, modules, symbols, and parameters. Within this area, `src/gyomu_schema/schemas/python/type` provides lower-level schema models, union types, and kinds specifically for representing Python AST expressions, statements, and type structures.
*   **`src/gyomu_schema/schemas/document`**: Defines data structures, validation rules, and translation configurations for structured documents, sections, and content elements.
*   **`src/gyomu_schema/schemas/knowledge`**: Defines schemas for structuring various knowledge domains, including coding guidelines, operational knowledge, package metadata, roadmaps, and technical integration references.
*   **`src/gyomu_schema/error`**: Defines core error handling schemas, domain-specific error classes, and associated retry and resolution strategies across application operations.

## Design Principles

- Centralized Data Contracts: Define shared data contracts for multiple packages exclusively within this package to ensure uniform data exchange.
- Strict Architectural Independence: Prohibit dependencies on other internal packages, specific business logic, and infrastructure details to maintain the package as a universal shared foundation.
- External Boundary Validation: Model data exchanged across external boundaries as Pydantic schemas using comprehensive annotations to support runtime validation, code generation, and documentation.
- Strong Typing for Semantic Values: Encode distinct meanings such as identifiers and paths into types to prevent value misplacement and enforce compile-time safety.
- Decoupled Interfaces: Separate interface contracts via Protocols from concrete implementations to control dependency directions and minimize coupling.

## Important Constraints

- Do not depend on external libraries other than Pydantic, Returns, and the Python standard library.
- Do not depend on other packages under the `gyomu` namespace.
- Do not implement Gyomu-specific business logic.
- Do not place processing specific to particular applications or packages within this package.
- Do not provide infrastructure-specific implementations.
- Do not implement AI model execution or LLM-specific processing.

## Editing Rules

- Explicitly type arguments and return values for all public APIs and core application logic.
- Maintain type-safe implementations that comply with strict mypy settings.
- Avoid `Any` and type-checking suppression, limiting their scope and justification when necessary.
- Define and validate JSON, YAML, persisted data, and structured data at system boundaries using Pydantic models.
- Use appropriate data structures such as dataclasses for internal state representation.
- Do not duplicate data structures or constraints for the same concept across multiple places.
- Express expected application failures explicitly using `returns.Result`, `Success`, and `Failure`.
- Handle expected failures at system boundaries rather than relying heavily on implicit exceptions.
- Design packages with clear responsibilities and direct dependencies from upper workflows to lower functions.
- Do not introduce circular dependencies between packages.
- Interact with other packages strictly through their public APIs rather than implementation details.
- Use Protocols and constructor injection to declare contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities and required changes rather than speculative future abstractions.
- Implement stateless and side-effect-free logic as pure functions where possible.
- Isolate I/O operations involving the file system, external services, and LLMs from business logic.
- Treat AI outputs as untrusted input and validate them with Pydantic models before use.
- Confine AI provider-specific APIs and types to adapters and infrastructure boundaries.
- Separate AI execution, routing, fallback, and retry responsibilities behind clean interfaces.
- Use structured data like concepts and analysis results as inputs for documentation generation.
- Treat document structure, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like `Document` instead of directly assembling Markdown strings.
- Treat source-code-derived concepts and human-managed knowledge as independent information sources.
- Add or update corresponding tests whenever observable behavior changes.
- Keep unit tests deterministic and isolate dependencies on LLMs and external services.
- Use actual temporary directories or fixtures for file system and project structure tests while mocking controlled dependencies.
- Mock dependencies based on actual public interfaces without over-relying on call counts or internal implementation details.
- Consolidate shareable logic into existing packages without duplicating implementations.
- Evaluate standard libraries and existing dependencies before adding new packages.
- Follow existing naming conventions, package structures, and code styles while keeping changes minimal.
- Keep the codebase passing all repository checks and tests including ruff, mypy, and pytest.

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
