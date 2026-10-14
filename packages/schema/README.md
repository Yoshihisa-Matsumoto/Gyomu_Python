# Gyomu Schema

US English | [JP 日本語](README.ja.md)

## Overview

This package provides canonical data schemas, type definitions, error types, protocols, and general utilities shared across the entire Gyomu ecosystem. Its primary purpose is to define data contracts passed between system components—including Python analysis, concepts, documents, knowledge, and snapshots. 

By establishing these centralized definitions, the package maintains type safety and data consistency while keeping inter-package dependencies loosely coupled. It specializes in Python AST and code structure analysis, structured document validation and translation, and domain-specific knowledge representation.

## Architecture

The package is organized around collaborating schema and data model components that divide responsibilities across distinct domain boundaries within the Gyomu system. 

Core code analysis is handled by specialized Python components. The Python code structure components define models for symbols, modules, files, configuration, and structural elements like classes, functions, and docstrings. Working alongside them, the AST and type components supply schema models, union types, and kinds for representing expressions, statements, and type structures.

Document processing and domain knowledge are supported by dedicated structuring components. The document components provide validation rules, translation strategies, and data models for structured documents, sections, and content elements. Meanwhile, the knowledge management components structure diverse domains such as coding guidelines, operational knowledge, project roadmaps, and technical integration references. 

Finally, cross-cutting concerns are addressed by a centralized error handling component that defines base errors, domain-specific error classes for AI, configuration, database, and validation operations, alongside recovery and resolution strategies.

## Installation

Install using uv.

```bash
uv add gyomu-schema
```

## Dependencies

This package is compatible with Pydantic version 2.x, which it is designed to use. 

For its runtime dependencies, the package relies on Pydantic for schema definition, data validation, serialization, and deserialization. It also uses the returns library to provide explicit success and failure expressions through Success, Failure, and Result types.

## Development

To maintain strict type safety and data consistency across all Gyomu features—such as Python Analysis, Concept, Document, Knowledge, and Snapshot—contributors must define all shared data contracts strictly within this foundational package. Because this package serves as an independent shared base that must not depend on any other Gyomu packages, all data structures traversing external boundaries like JSON, persistence layers, and MCP must be modeled as Pydantic schemas. Contributors should omit implementation-specific details that are restricted solely to internal processing from these public schemas. Furthermore, to prevent value mix-ups, identifiers, paths, and meaningful values must be encapsulated as distinct types to encode domain semantics directly into the type system.

Annotations on Pydantic schemas are mandatory rather than optional because they supply critical metadata for AI code generation, documentation generation, and knowledge creation, in addition to runtime type checking. When defining contracts, developers must keep APIs immutable and declarative, ensuring that utilities remain strictly generic and free of specific Gyomu business logic. Protocols must be reserved strictly for cross-package interface contracts that do not belong to the responsibilities of any single package; domain-specific protocols and concrete implementations must remain within their respective packages. Finally, contributors are required to implement error handling using domain-specific error models that adhere to a uniform structure, guaranteeing consistent error handling across all interacting packages.

## Public API

- Python AST and Type Models - Defines schema models, union types, and kinds for representing Python AST expressions, statements, and type structures to support analysis.
- Python Code Structure Analysis - Provides data models and schemas for Python code structures, symbols, modules, files, project configuration, and dependencies.
- Structured Document Schemas - Defines data models, validation rules, translation strategies, and content elements for structured documents and sections.
- Error Handling Models - Provides core error handling models, domain-specific error classes, and resolution strategies for AI, configuration, database, and validation.
- Knowledge Management Schemas - Defines schemas for structuring knowledge domains including coding guidelines, technical documentation, operational knowledge, and roadmaps.

## License

MIT