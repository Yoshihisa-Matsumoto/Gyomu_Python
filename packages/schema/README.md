# Gyomu Schema

US English | [JP 日本語](README.ja.md)

## Overview

The package defines canonical schema models and data structures for the Gyomu system, providing robust Pydantic-based models for Python AST and code analysis, package structure analysis, conceptual modeling, error handling, and configuration management. 

Its primary purpose is to establish shared schemas, type definitions, error types, protocols, and general-purpose utilities across the entire project. By defining the data contracts exchanged between features such as Python Analysis, Concept, Document, Knowledge, and Snapshot, the package maintains type safety and data consistency while keeping inter-package dependencies loosely coupled.

## Architecture

The `gyomu-schema` package is organized into dedicated components that divide responsibilities across schema modeling, error management, configuration, and system utilities. Pydantic-based data structures are structured to handle distinct domains of the Gyomu system. 

Core code and abstract syntax tree analysis are handled by specialized schema components. The Python analysis components define models for expressions, statements, symbols, classes, functions, modules, and dependencies, with dedicated structures for type processing. Complementing these code-level models, the concept and package modeling components define structures for package dependency analysis, directory facts, pyproject analysis, and architectural capabilities.

Operational concerns are isolated into dedicated modules. The error handling component defines base application errors, domain-specific failure classes across AI, configuration, database, I/O, validation, and timeouts, alongside operational phases and automated retry strategies. Concurrently, the configuration component manages parameters for system processes, code analysis, LLM execution, and loaders. Finally, utility modules support these components by providing file system operations, project snapshots, object serialization, and execution helpers.

## Installation

Install using uv.

```bash
uv add gyomu-schema
```

## Dependencies

This package requires Python and is designed for Pydantic version 2.x, which is used for schema definition, data validation, and serialization. It also relies on the `returns` library to manage explicit success and failure states using Result types. Ensure your environment meets these requirements before installation.

## Development

The primary purpose of this package is to serve as the shared foundation for the entire Gyomu project by providing canonical schemas, type definitions, error types, protocols, and general-purpose utilities. By acting as the central source for data contracts passed between features such as Python Analysis, Concept, Document, Knowledge, and Snapshot, it maintains type safety and data consistency while keeping inter-package dependencies loosely coupled. 

Contributors must adhere to strict architectural policies to preserve this foundation. All data contracts shared across multiple Gyomu packages must reside here, with data crossing external boundaries—such as JSON, persistence, and MCP—defined strictly as Pydantic schemas. To ensure these schemas serve AI code generation, documentation, and knowledge generation effectively, annotations must never be omitted. Furthermore, value types should represent distinct meanings to prevent misuse, protocols must define shared interfaces without concrete implementations, and error types must follow a common structure for consistent handling across packages.

To maintain its role as an independent core infrastructure, this package must never depend on other Gyomu packages and must contain only generic utilities devoid of specific business logic. APIs should be designed to be as immutable and declarative as possible, while implementation details used solely for internal processing should remain hidden rather than exposed as public Pydantic schemas.

## Public API

- Python AST and Code Analysis Schemas - Defines schema models representing Python AST expressions, statements, types, and code structures for analysis.
- Package and Concept Modeling - Provides comprehensive schema definitions for package analysis, dependency tracking, directory facts, and capability and package concepts.
- Error Handling and Retry Strategies - Defines application-level error handling classes, operational phases, domain-specific errors, and retry strategies.
- Configuration and Process Options - Defines configuration options and parameters for system processes, code analysis, LLM execution, and loaders.
- System Utilities and File Management - Provides utilities for file system management, project and file snapshots, serialization, execution timing, and asynchronous/synchronous execution wrapping.

## License

MIT