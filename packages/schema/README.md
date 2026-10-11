# Gyomu Schema

US English | [JP 日本語](README.ja.md)

## Overview

This package provides the foundational data contracts, canonical models, and structural schemas shared across the Gyomu project. Its primary purpose is to define the standard types, protocols, error models, and validation rules for Python AST analysis, structured documents, project knowledge bases, and snapshots. 

By establishing explicit data contracts between functional components, the package maintains strict type safety and data consistency throughout the system. It enables packages to interact seamlessly while remaining fully decoupled, ensuring a robust and maintainable architecture for project-wide data exchange.

## Architecture

The package is organized around a core set of specialized schema domains and utility frameworks that divide responsibilities by data structure and system concern. Code analysis and structural representation are handled by dedicated Python modules that define models for AST expressions, statements, classes, functions, modules, and type systems. 

Complementing the code analysis capabilities, structured document schemas manage content elements like sections, paragraphs, lists, and tables, while project knowledge schemas capture domain-specific information such as coding guidelines, roadmaps, and technical references. Robust cross-cutting operations are supported by a dedicated error-handling component that provides comprehensive error hierarchies, domain-specific fault definitions, and retry resolution strategies. 

Finally, a serialization and utility framework collaborates across these domains to offer format validation, data conversion, timing, execution monitoring, and file system operations, tying the structural models and error strategies together into a cohesive architecture.

## Installation

Install using uv.

```bash
uv add gyomu-schema
```

## Dependencies

This package requires Pydantic version 2.x, as it is designed around Pydantic Version 2 for schema definition, data validation, serialization, and deserialization. 

For runtime usage, it relies on the `returns` package to handle explicit success and failure expressions using Success, Failure, and Result types.

## Development

Contributors must maintain this package as a foundational, zero-dependency layer for the Gyomu ecosystem. All data contracts shared across multiple packages must reside here, utilizing Pydantic schemas for external boundaries such as JSON, persistence, and MCP layers, while keeping internal implementation details unexposed. To prevent value swapping and ensure strict type safety, contributors should represent distinct concepts like IDs and paths as explicit types, avoiding primitive obsession. Furthermore, annotations on Pydantic schemas must never be omitted, as they serve a dual purpose: enforcing runtime type integrity and driving AI-assisted code, documentation, and knowledge generation.

Protocol definitions and error handling require careful boundary management. Protocols should be defined here only when they represent shared interface contracts that do not belong to the responsibility of a single package; package-specific use cases must keep their protocols local. Implementations must follow proper dependency directions. All error types must adhere to a common structure to guarantee consistent error handling across packages, while utilities must remain strictly generic and free of business logic. Finally, contributors are required to design all APIs to be immutable and declarative, ensuring that data consistency and loose coupling are preserved as the architecture evolves.

## Public API

- Python AST and Type Models - Models Python Abstract Syntax Tree (AST) expressions, statements, types, and code structure elements for analysis.
- Structured Document Models - Defines structured document models, elements, validation rules, and translation strategies.
- Project Knowledge Schemas - Provides domain-specific schemas for representing project knowledge, guidelines, operational details, and technical references.
- Error Handling and Recovery Schemas - Defines comprehensive application error hierarchies, retry policies, and resolution strategies across operations.
- Serialization and Utility Framework - Provides utility functions for serialization, format validation, timing, execution wrapping, and file system operations.

## License

MIT