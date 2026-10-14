# Gyomu Schema

US English | [JP 日本語](README.ja.md)

## Overview

The package provides canonical data schemas, models, and shared utilities for the Gyomu system. Its primary purpose is to define data contracts across Gyomu functions—such as Python analysis, structured documents, domain knowledge, and snapshots—while maintaining type safety and data consistency. 

By serving as a centralized source for types, error definitions, and protocols, the package keeps dependencies between individual Gyomu modules loosely coupled. It specializes in supporting Python AST and code structure analysis, structured document validation and translation, and domain-specific knowledge representation.

## Architecture

The package is organized around a core set of collaborating components that divide responsibilities by domain and schema type. Python analysis is structured through dedicated models representing AST expressions, statements, type structures, and code elements such as classes, functions, modules, and project configurations. 

Structured document processing is handled by schema components that define document hierarchies, content elements, validation rules, and translation strategies. Domain-specific requirements are further supported by robust error handling models—covering AI, configuration, database, and validation operations with associated resolution strategies—alongside knowledge management schemas that structure guidelines, roadmaps, and technical documentation.

Shared foundational operations, such as serialization, timing, results wrapping, and filesystem interactions, cut across these components to support the broader system architecture.

## Installation

Install using uv.

```bash
uv add gyomu-schema
```

## Dependencies

This package is designed for compatibility with Pydantic version 2.x, which is required alongside Pydantic schemas for data definition, validation, serialization, and deserialization. Additionally, the runtime relies on the returns package to provide explicit success and failure representations using Success, Failure, and Result.

## Development

To maintain strict package decoupling and consistent data contracts across Python Analysis, Concept, Document, Knowledge, and Snapshot features, all shared data structures must be defined as canonical Pydantic schemas. Contributors must ensure that any data crossing external boundaries—such as JSON serialization, persistence layers, and Model Context Protocol (MCP) interfaces—is fully modeled using Pydantic. Furthermore, to enhance runtime safety and maximize utility for AI-driven code generation, documentation, and knowledge extraction, all schema annotations must be explicitly provided and thoroughly documented rather than omitted. Implementation details reserved exclusively for internal processing should remain hidden and not exposed as public Pydantic schemas.

Type safety and domain clarity must be enforced by encapsulating values, identifiers, and paths into precise types to prevent data interchange errors. APIs should be designed to be strictly immutable and declarative, accompanied by domain-specific error handling models that adhere to a unified error structure for consistent cross-package error recovery. Shared utilities must remain completely decoupled from specific business logic, and protocols must be reserved strictly for cross-cutting interface contracts that do not belong to the responsibilities of any single downstream package. Because this package serves as the foundational shared infrastructure for the entire Gyomu ecosystem, contributors must strictly preserve its independence by preventing any dependencies on other Gyomu packages.

## Public API

- Python AST and Type Models - Defines schema models, union types, and kinds for representing Python AST expressions, statements, and type structures to support analysis.
- Python Code Structure Analysis - Provides data models and schemas for Python code structures, symbols, modules, files, project configuration, and dependencies.
- Structured Document Schemas - Defines data models, validation rules, translation strategies, and content elements for structured documents and sections.
- Error Handling Models - Provides core error handling models, domain-specific error classes, and resolution strategies for AI, configuration, database, and validation.
- Knowledge Management Schemas - Defines schemas for structuring knowledge domains including coding guidelines, technical documentation, operational knowledge, and roadmaps.

## License

MIT