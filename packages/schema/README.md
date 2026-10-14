# Gyomu Schema

US English | [JP 日本語](README.ja.md)

## Overview

This package provides canonical data models, structural schemas, and validation rules that serve as the shared foundation across the entire Gyomu ecosystem. Its primary purpose is to define data contracts for Python AST analysis, structured documents, project knowledge bases, and robust error-handling strategies. 

By establishing shared types, protocols, and utility definitions, the package ensures data consistency and type safety across all functional modules. It facilitates seamless communication between distinct features while maintaining loosely coupled dependencies throughout the architecture.

## Architecture

The package is organized around a core set of collaborating domain schemas and utility components that divide responsibilities by data structure and system concern. At its foundation, the architecture separates code analysis, document formatting, project knowledge, and robust error management into distinct, modular subsystems.

Code and structural analysis responsibilities are handled by specialized schema directories. The Python components model code structures such as classes, functions, modules, and symbols, while nested type directories define AST expressions, statements, and union types. Concurrently, document components manage structured content elements, sections, and validation rules, and knowledge components structure domain-specific data like coding guidelines, operational details, and technical references.

Cross-cutting operational concerns, such as fault-tolerance and error management, are centralized within dedicated error-handling schemas that define application error hierarchies, retry policies, and resolution strategies across operations. Together, these components collaborate to provide a unified framework for data modeling, validation, and serialization.

## Installation

Install using uv.

```bash
uv add gyomu-schema
```

## Dependencies

This package is designed for Pydantic version 2.x, which is used for schema definition, data validation, serialization, and deserialization. 

For runtime usage, the package relies on pydantic for its core data handling and returns to provide explicit success and failure representations using Success, Failure, and Result types.

## Development

Data contracts shared across multiple Gyomu packages must reside within this foundation. Contributors are required to define all data handled at external boundaries—such as JSON, persistence layers, and MCP interfaces—as Pydantic schemas, while internal implementation details that remain strictly within a single processing flow should not be exposed as Pydantic models. To prevent value misassignment and enforce strict boundaries, developers must represent identifiers, paths, and meaningful values through dedicated types whenever possible. Furthermore, Pydantic schema annotations must be comprehensively provided rather than omitted, ensuring they serve not only as runtime type information but also as essential context for AI-driven code generation, document generation, and knowledge generation.

Interfaces and shared abstractions must adhere to strict dependency and placement rules. Developers should define Protocols as interface contracts separated from their implementations, restricting this package to interfaces that multiple packages share and that do not belong to the specific responsibilities of any single package. Protocols tied to specific package responsibilities or use cases belong within those respective packages, with concrete implementations positioned according to the correct direction of dependency and responsibility. Error handling must follow a common error structure across all definitions to guarantee consistent error management throughout the ecosystem.

All utilities implemented in this package must remain strictly generic and free of business logic tied to any specific Gyomu package. Contributors must design APIs to be as immutable and declarative as possible to maintain robust data consistency and type safety. Finally, contributors must preserve the zero-dependency status of this package relative to other Gyomu packages, ensuring it perpetually functions as an isolated, stable shared foundation.

## Public API

- Python AST and Type Models - Models Python Abstract Syntax Tree (AST) expressions, statements, types, and code structure elements for analysis.
- Structured Document Models - Defines structured document models, elements, validation rules, and translation strategies.
- Project Knowledge Schemas - Provides domain-specific schemas for representing project knowledge, guidelines, operational details, and technical references.
- Error Handling and Recovery Schemas - Defines comprehensive application error hierarchies, retry policies, and resolution strategies across operations.
- Serialization and Utility Framework - Provides utility functions for serialization, format validation, timing, execution wrapping, and file system operations.

## License

MIT