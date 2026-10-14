# Gyomu Infra

US English | [JP 日本語](README.ja.md)

## Overview

This core infrastructure package provides robust utilities and services designed for the Gyomu ecosystem. Its primary purpose is to standardize and handle interactions with external environments, including file and stream I/O, structured CSV processing, filesystem manipulation, and database persistence via SQLAlchemy. 

The package encapsulates essential domain-specific infrastructure concerns such as business calendar calculations, market holiday repositories, and parameter translation services. By centralizing operations that depend on external libraries and execution environments, it ensures that upper-level packages remain decoupled from low-level implementation details.

## Architecture

The gyomu-infra package is organized into a set of specialized modules that divide core infrastructure responsibilities across data processing, storage, and domain logic. The package structure separates low-level system utilities from domain-specific services, enabling structured collaboration between file handling, database persistence, and business calculations.

Data handling and file operations are managed through dedicated components for structured CSV parsing with Pydantic validation, filesystem manipulation, and lazy stream processing. These I/O and stream utilities supply foundational data pipelines that feed into the broader application.

Persistence and domain-specific operations are encapsulated within database repository implementations and specialized calculation services. Relational database interactions are handled via SQLAlchemy-backed repositories, while domain logic leverages cached market holiday repositories to execute business calendar calculations and dynamic parameter translations. Together, these collaborating components deliver a cohesive infrastructure layer for system integration and data management.

## Installation

Install using uv.

```bash
uv add gyomu-infra
```

## Dependencies

This package requires Pydantic version 2.x, as it is designed specifically for Pydantic Version 2. 

For runtime dependencies, the package utilizes Pydantic for schema definition, data validation, serialization, and deserialization. It also uses returns for explicit success and failure representation via Success, Failure, and Result, and SQLAlchemy for database access.

## Development

Contributors must strictly enforce the separation of concerns by isolating all input-output operations, side effects, and external library APIs within this package. Implementation details of the file system, databases, configuration loading, and data conversion must remain entirely encapsulated to prevent upper packages from forming direct dependencies on external environments or specific third-party libraries. Furthermore, domain-specific business logic must never bleed into this infrastructure layer; all implementations should remain generic utility components rather than housing application-specific rules.

To maintain architectural integrity, persistence operations must decouple database access details from the consuming code by utilizing strict boundaries such as repositories and mappers. Data acquired from external sources requires validation through schemas, while any raw exceptions thrown by external drivers must be caught and translated into a unified error model that preserves context regarding the operation and failure location. Contributions that introduce hidden tight coupling, expose raw external APIs to upper layers, or mix domain knowledge into these utility components will be rejected to preserve the decoupled nature of the Gyomu ecosystem.

## Public API

- CSV Data Processing - Read, write, and parse structured CSV data and configuration models using Pydantic validation.
- Filesystem Operations - Provide robust file system operations including file I/O, searching, enumeration, and exclusive access handling.
- Stream Processing - Support lazy stream processing and byte stream I/O utilities for handling pipeline data.
- Variable and Parameter Resolution - Resolve and translate date and parameter placeholders to support dynamic execution context.
- Business Calendar Services - Perform business calendar calculations and market holiday services using cached repository instances.
- Database Infrastructure - Manage relational database connections, transactions, and SQLAlchemy-backed repository models.

## License

MIT