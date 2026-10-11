# Gyomu Infra

US English | [JP 日本語](README.ja.md)

## Overview

Gyomu Infrastructure is a core package designed to provide robust shared infrastructure utilities and services for the Gyomu ecosystem. Its primary purpose is to standardize and handle operations involving external environment connections, such as file and stream I/O, structured CSV processing, filesystem manipulation, and database persistence via SQLAlchemy. The package encapsulates domain-specific infrastructure concerns, including business calendar calculations, market holiday repositories, and parameter translation services. By centralizing operations that depend on external libraries and execution environments, it prevents upper-level packages from directly depending on infrastructure implementation details and ensures a clean architecture.

## Architecture

The package is organized into a set of specialized, collaborating infrastructure components that divide responsibilities across data handling, filesystem operations, and domain-specific services. Core utilities manage structured data parsing, file input/output, and stream processing, while dedicated persistence layers handle relational database connections and transactions via SQLAlchemy. 

Responsibilities are cleanly separated into modular directories. The CSV component handles reading, writing, and model validation, and the filesystem module provides robust file enumeration, search, and exclusive access handling. Stream processing components manage lazy data pipelines and byte stream I/O. 

Domain-specific concerns are encapsulated to support dynamic execution contexts. The variable translation component resolves date and parameter placeholders, and the date component performs business calendar calculations using cached market holiday repositories. Together, these components collaborate to supply reliable infrastructure services for application workflows.

## Installation

Install using uv.

```bash
uv add gyomu-infra
```

## Dependencies

This package is designed for Pydantic version 2.x compatibility. 

For runtime execution, it relies on Pydantic for schema definition, data validation, and serialization and deserialization. It also uses returns to provide explicit success and failure handling through Success, Failure, and Result, and utilizes SQLAlchemy for database access.

## Development

Contributors must strictly encapsulate external library APIs and side-effect-heavy I/O operations behind common infrastructure interfaces to prevent upper layers from depending directly on implementation details. File systems, databases, configuration loading, and data conversion must maintain strict separation of concerns, with incoming external data consistently validated through schemas. Persistence logic requires a clear separation between repositories and mappers to shield users from database specifics, while all errors must map into a unified error model that preserves context for tracing operations and failure locations. 

To maintain architectural integrity, contributors must keep this package entirely free of domain-specific business logic or application-specific rules, ensuring it remains a reusable foundation for the Gyomu ecosystem. Any integration of external libraries or execution environments must be wrapped inside standardized interfaces, allowing the broader system to interact with external systems without coupling to concrete implementations.

## Public API

- CSV Data Processing - Read, write, and parse structured CSV data and configuration models using Pydantic validation.
- Filesystem Operations - Provide robust file system operations including file I/O, searching, enumeration, and exclusive access handling.
- Stream Processing - Support lazy stream processing and byte stream I/O utilities for handling pipeline data.
- Variable and Parameter Resolution - Resolve and translate date and parameter placeholders to support dynamic execution context.
- Business Calendar Services - Perform business calendar calculations and market holiday services using cached repository instances.
- Database Infrastructure - Manage relational database connections, transactions, and SQLAlchemy-backed repository models.

## License

MIT