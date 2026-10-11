# Gyomu Schema

## Repository Overview

`gyomu-schema` serves as the foundational core for the Gyomu project by providing canonical data models, structural schemas, type definitions, error types, protocols, and generic utilities. Its primary responsibility is to define data contracts that are shared across functional packages—such as Python Analysis, Concept, Document, Knowledge, and Snapshot. By establishing these shared data contracts, the package maintains type safety and data consistency across the system while keeping inter-package dependencies loosely coupled.

## Package Responsibilities

- Define canonical data schemas and type models for Python code analysis, structured documentation, and project knowledge.
- Provide standardized error definitions, fault-tolerance options, and retry resolution strategies.
- Offer helper utilities and validation routines for data serialization, format conversion, and execution monitoring.

## Architecture

The package is organized into two primary architectural areas rooted under `src/gyomu_schema/`: schema definitions (`src/gyomu_schema/schemas/`) and core error handling (`src/gyomu_schema/error`).

The schema area is further divided into specialized subdirectories:
- **`src/gyomu_schema/schemas/python`**: Defines data models for Python code structure analysis, covering modules, symbols, classes, functions, methods, parameters, dependencies, and documentation strings.
- **`src/gyomu_schema/schemas/python/type`**: Extends the Python analysis structure by defining schema models and union types for representing Python AST expressions, statements, and type structures.
- **`src/gyomu_schema/schemas/document`**: Houses data structures, validation rules, and translation configurations for structured documents, sections, and content elements such as paragraphs, bullet lists, code blocks, and tables.
- **`src/gyomu_schema/schemas/knowledge`**: Provides schemas for structuring various knowledge domains, including coding guidelines, operational knowledge, package usage, project roadmaps, and technical integration references.

The **`src/gyomu_schema/error`** component operates alongside the schemas, defining base error types, domain-specific error classes across AI, configuration, database, I/O, validation, and timeouts, alongside their associated retry and resolution strategies.

## Design Principles

- Centralized Data Contracts: Define shared data contracts for multiple packages exclusively within this package to ensure uniform data exchanges across boundaries.
- Strict Architectural Boundaries: Prevent dependencies on other Gyomu packages, infrastructure specifics, business logic, and external libraries beyond Pydantic, Returns, and the Python standard library.
- Type-Driven Safety and Documentation: Represent semantic values like IDs and paths distinctively through types, and exhaustively provide Pydantic schema annotations to aid runtime validation, AI code generation, and documentation.
- Separation of Protocols and Implementations: Define interfaces as Protocols separate from concrete implementations, aligning placement with dependency directions to control coupling and prevent over-aggregation.
- Immutable and Declarative APIs: Design APIs to be immutable and declarative while keeping utilities domain-agnostic and free of specific business logic.

## Important Constraints

- Do not depend on external libraries other than Pydantic, Returns, and the Python standard library.
- Do not depend on other packages under `gyomu`.
- Do not implement Gyomu-specific business logic.
- Do not place processing specific to particular applications or packages.
- Do not provide infrastructure-specific implementations.
- Do not implement AI model execution or LLM-specific processing.
- Preserve the existing public export structure.

## Editing Rules

- Explicitly specify argument and return types for public APIs and primary application logic.
- Maintain type-safe implementations compatible with strict mypy settings.
- Avoid Any and suppress type checking sparingly, restricting scope and rationale when necessary.
- Define and validate structured data at system boundaries using Pydantic models.
- Use dataclasses and appropriate data structures for internal state representation.
- Do not duplicate conceptual data structures or constraints across multiple locations.
- Express expected application failures explicitly using returns.Result, Success, and Failure.
- Handle exceptions at boundaries rather than using them to communicate expected failures.
- Design package dependencies to flow from higher-level workflows to lower-level features.
- Do not introduce circular dependencies between packages.
- Interact with other packages strictly through their public APIs rather than internal implementation details.
- Use Protocols and constructor injection to define contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities and changes rather than speculative future abstractions.
- Implement operations without side effects as pure functions wherever possible.
- Isolate I/O operations involving file systems, external services, and LLMs from business logic.
- Validate AI outputs using Pydantic models before using them.
- Confine AI provider-specific APIs and types to adapters and infrastructure boundaries.
- Design AI execution interfaces that separate execution control, routing, fallback, and retry from callers.
- Use structured data like concepts and analysis results as inputs for document generation.
- Treat document structure, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations such as Document instead of assembling Markdown strings directly.
- Treat code-derived concepts and human-managed knowledge as independent information sources.
- Update or add corresponding tests when observable behavior changes.
- Keep unit tests deterministic by isolating LLM and external service dependencies.
- Use temporary directories and fixtures for file system tests, mocking only external service dependencies.
- Match mocks to actual public interfaces without over-relying on internal call counts and details.
- Consolidate shared logic into existing packages without duplicating implementations.
- Evaluate standard libraries and existing dependencies before adding new packages.
- Maintain consistency with existing naming conventions, package structures, and code styles.
- Ensure all code passes ruff, mypy, and pytest checks.

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
