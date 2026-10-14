# Gyomu Schema

## Repository Overview

The `gyomu-schema` package provides canonical data schemas, type definitions, error types, protocols, and generic utilities shared across the Gyomu system. Its primary responsibility is to define data contracts passed between Gyomu's functional domains—including Python Analysis, Concept, Document, Knowledge, and Snapshot—specializing in Python AST and code structure analysis, structured document validation and translation, and domain-specific knowledge representation. 

By establishing these centralized data contracts, the package maintains type safety and data consistency across system components while keeping package-level dependencies loosely coupled.

## Package Responsibilities

- Define canonical schemas and data models for Python code structures, AST analysis, and type representation.
- Provide validation rules, translation instructions, and structured models for documents and sections.
- Define domain-specific error handling and recovery strategy models.
- Offer shared utility functions for serialization, timing, results wrapping, and filesystem operations.

## Architecture

The package is structurally organized into distinct schema and error-handling areas under the `src/gyomu_schema` root:

*   **`src/gyomu_schema/schemas/python`**: Defines Python code structure analysis schemas, data models, and union types. It includes `src/gyomu_schema/schemas/python/type`, which focuses specifically on schema models and union types for Python AST expressions, statements, and type structures.
*   **`src/gyomu_schema/schemas/document`**: Defines schemas, data structures, validation rules, and translation strategies for structured documents, sections, and content elements.
*   **`src/gyomu_schema/schemas/knowledge`**: Defines schemas for structuring various knowledge domains, including coding guidelines, operational knowledge, package metadata, roadmaps, and technical references.
*   **`src/gyomu_schema/error`**: Defines core error-handling schemas, domain-specific error classes, and associated retry and resolution strategies.

## Design Principles

- Centralized Data Contracts: Define shared data contracts for multiple Gyomu packages within this package to unify data exchange, while keeping internal implementation details private and excluding specific business logic.
- Strict External Boundaries: Use Pydantic schemas for data handled at external boundaries to ensure consistent validation and serialization, mandating comprehensive annotations that serve AI code generation, documentation, and knowledge generation.
- Strong Type Safety: Represent semantic values such as IDs and paths as distinct types to prevent value misidentification.
- Decoupled Interfaces: Define protocols as implementation-agnostic contracts separated from concrete implementations, controlling dependency directions and preventing excessive concentration in common packages.
- Zero Internal Dependencies: Maintain this package as an independent foundational layer that depends solely on Pydantic, Returns, and the Python standard library, without relying on other Gyomu packages or infrastructure specifics.

## Important Constraints

- Do not depend on external libraries other than Pydantic, Returns, and the Python standard library.
- Do not depend on other packages under the `gyomu` namespace.
- Do not implement Gyomu-specific business logic.
- Do not place processing specific to particular applications or packages.
- Do not provide infrastructure-specific implementations.
- Do not implement AI model execution or LLM-specific processing.

## Editing Rules

- Explicitly type arguments and return values for public APIs and primary application logic.
- Maintain type-safe implementations that comply with strict mypy settings.
- Avoid Any and type-checking suppression, restricting their scope and justification when necessary.
- Define and validate structured data at system boundaries using explicit Pydantic schemas.
- Use dataclasses and appropriate data structures for internal state representation.
- Do not duplicate the same conceptual data structures or constraints across multiple places.
- Represent expected application failures explicitly using returns.Result, Success, and Failure.
- Do not use exceptions for expected failures, and handle exceptions appropriately at boundaries.
- Design package dependencies to flow from higher-level workflows to lower-level functions without circular dependencies.
- Depend only on public APIs of other packages rather than internal implementation details.
- Use Protocols and constructor injection to specify contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities and changes rather than speculative future abstractions.
- Implement side-effect-free logic as pure functions whenever possible.
- Separate I/O operations involving the filesystem, external services, or LLMs from business logic.
- Treat AI outputs as untrusted input and validate them with Pydantic models before use.
- Enclose AI-provider-specific APIs and types within adapters and infrastructure boundaries.
- Design AI interfaces to decouple execution control, routing, fallback, and retry logic from callers.
- Use structured data such as Concepts and analysis results as inputs for document generation.
- Treat document structure, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document instead of directly assembling Markdown strings.
- Treat auto-derived Concepts from source code and human-managed Knowledge as independent information sources.
- Update tests when observable behavior changes.
- Keep unit tests deterministic by isolating dependencies on LLMs and external services.
- Use actual temporary directories or fixtures for filesystem and project structure tests, mocking only external service dependencies.
- Base mock dependencies on actual public interfaces rather than internal implementation details.
- Consolidate shareable logic into existing packages without duplicating implementations.
- Evaluate standard libraries and existing dependencies before adding new dependency packages.
- Follow existing naming conventions, package structures, and code styles while minimizing change scopes.
- Maintain code that passes all repository checks and tests including ruff, mypy, and pytest.

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
