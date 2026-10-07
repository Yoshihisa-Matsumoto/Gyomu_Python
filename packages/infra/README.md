# Gyomu Infra

US English | [JP 日本語](README.ja.md)

## Overview

The gyomu-infra package serves as the foundational infrastructure layer for the Gyomu ecosystem. Its primary mission is to centralize external environment interactions and concrete processing tasks—such as file handling, configuration loading, archiving, and database access—into a single shared module. 

By consolidating operations that rely on external libraries and execution environments, this package prevents upper-level packages from depending directly on implementation details. It delivers robust core utilities, including Pydantic-integrated CSV parsing, advanced filesystem and stream operations, SQLAlchemy-backed database persistence with transaction management, and specialized domain services like business calendars and parameter resolution.

## Architecture

The package is organized into a set of specialized collaborating components that divide core infrastructure and domain responsibilities. Data processing capabilities are handled by dedicated modules for CSV parsing and serialization, which integrate with Pydantic models, alongside stream processing utilities that manage lazy single-use streams and byte stream file operations.

Persistent data access is structured around database management components, utilizing SQLAlchemy repositories and transaction controls to implement data management and querying protocols. Additionally, specialized domain services execute business calendar calculations, holiday services, and variable translation. 

Finally, a robust set of filesystem and system utilities supports file I/O operations, enumeration, searching, access management, process execution, hashing, and archiving. These components collaborate to deliver a unified infrastructure layer supporting the system's storage, parsing, and domain logic.

## Installation

Install using uv.

```bash
uv add gyomu-infra
```

## Dependencies

This package is designed for Pydantic version 2.x compatibility. \n\nFor runtime operations, it relies on Pydantic for schema definition, data validation, serialization, and deserialization. Additionally, it uses the returns library for explicit success and failure expressions via Success, Failure, and Result, and SQLAlchemy for database access.

## Development

Contributors must strictly isolate all input-output operations, side effects, and external library interactions within this package to prevent upper-level layers from depending directly on infrastructure implementation details. Specific external APIs must be encapsulated behind common interfaces and shared utilities, ensuring a clear separation of concerns across file systems, databases, configurations, and data conversion tools. When handling external data, implementations should leverage schema validation, while database access must maintain a strict separation of responsibilities through repositories and mappers that hide persistence mechanisms from the consuming code.

All error handling must convert native exceptions into a common error model capable of tracking the origin and context of operations. Contributors are strictly prohibited from introducing specific application business logic or domain knowledge into this infrastructure layer. Any evolution of the package must preserve the design constraint that upper-level packages remain completely decoupled from specific external libraries and execution environments.

## Public API

- CSV Data Processing - Read, parse, serialize, and configure CSV data handling integrated with Pydantic data models.
- Filesystem Utilities - Provide robust filesystem utilities for file I/O, searching, enumeration, and access management.
- Database Management - Manage database connections, SQLAlchemy repository patterns, transactions, and error handling.
- Gyomu Domain Services - Perform business calendar calculations, holiday services, parameter access, and variable translation.
- Core System Utilities - Support general-purpose utilities including lazy stream processing, process execution, hashing, and archiving.

## License

MIT