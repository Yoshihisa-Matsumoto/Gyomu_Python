# Gyomu Infra

## Repository Overview

Gyomu Infrastructure (`gyomu-infra`) is a core infrastructure package that provides shared utilities and services for application interaction with external environments, including file and stream I/O, filesystem manipulation, structured CSV processing, archiving, and database persistence via SQLAlchemy. Its primary responsibility is to centralize processing dependent on external libraries and execution environments.

By encapsulating domain-specific infrastructure concerns—such as business calendar calculations, market holiday repositories, and parameter translation services—the package ensures that upper-level packages remain decoupled from infrastructure implementation details.

## Package Responsibilities

- Provide core infrastructure and utility components for data parsing, file handling, and stream processing.
- Implement persistence operations, database connections, and transaction management using SQLAlchemy.
- Support domain-specific calculations and translations including business calendars, holidays, and variable resolution.
- Provide system integration helpers such as logging, process execution, configuration loading, and hashing.

## Architecture

The package is organized into two primary architectural areas: infrastructure utilities under `src/gyomu_infra/` and domain logic under `src/gyomu_infra/gyomu/`.

The infrastructure layer is divided into three components:
- `src/gyomu_infra/csv`: Handles CSV parsing, serialization, and configuration using Pydantic models. The reader parses data into validated models, while the writer serializes model records.
- `src/gyomu_infra/filesystem`: Provides file I/O operations for text and JSON, file enumeration and search functionality via `FileSearch`, and file access helpers via `FileOperation`.
- `src/gyomu_infra/stream`: Manages stream processing and I/O, supporting lazy single-use streams of `Result` values via `RecordStream` and writing byte streams to files.

The domain logic layer (`src/gyomu_infra/gyomu/`) contains:
- `src/gyomu_infra/gyomu/variable`: Translates and resolves date and parameter placeholders utilizing defined variable types, date parameter keywords, and `VariableTranslatorImpl`.
- `src/gyomu_infra/gyomu/date`: Manages business calendar calculations and holiday services, where `BusinessCalendarService` retrieves cached calendar instances from a market holiday repository.

## Design Principles

- Centralize external input-output and side effects into common infrastructure features to prevent upstream packages from depending directly on external library and execution environment details.
- Encapsulate specific external library APIs behind internal interfaces to ensure implementations remain decoupled from consumers.
- Strictly separate responsibilities for file systems, databases, configurations, and data transformations while preventing domain logic or application-specific knowledge from entering the infrastructure layer.
- Combine data handling with schema validation at system boundaries to prevent unverified data from entering internal application models.
- Separate persistence details using patterns like repositories and mappers, and standardize error handling through a unified error model that preserves traceability.

## Important Constraints

- Do not implement business logic.
- Do not depend on specific application domain logic.
- Do not expose external library-specific types or APIs as part of the common interface.
- Do not leak infrastructure implementation details to upper application layers.
- Do not treat external data as internal application models without validation.
- Do not implement business processes that depend on specific database products or external services.

## Editing Rules

- Explicitly specify input and output types for all public APIs and core application logic.
- Maintain type-safe implementations that comply with strict mypy settings.
- Avoid Any and type-checking suppression, limiting their scope and justification when necessary.
- Define and validate structured data at external boundaries, persistent storage, and serialization points using Pydantic models.
- Use appropriate data structures such as dataclasses to represent internal state.
- Avoid duplicating data structures or constraints for the same concept across multiple locations.
- Express expected failures explicitly using returns.Result, Success, and Failure.
- Handle expected errors at appropriate boundaries rather than relying heavily on implicit exceptions.
- Design packages with clear responsibilities and direct dependencies from upper workflows to lower functions.
- Do not introduce circular dependencies between packages.
- Depend only on public APIs of other packages rather than their internal implementation details.
- Use Protocols and constructor injection to declare contracts for external dependencies and interchangeable logic.
- Design for current responsibilities and actual changes rather than speculative future abstractions.
- Implement stateless and side-effect-free logic as pure functions wherever possible.
- Separate input and output operations involving the file system, external services, and LLMs from business logic.
- Validate AI outputs using Pydantic models before use.
- Isolate AI provider-specific APIs and types behind adapters and infrastructure boundaries.
- Separate AI execution, routing, fallback, and retry concerns behind clean interfaces.
- Use structured data like concepts and analysis results as inputs for document generation.
- Treat document composition, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document models instead of directly assembling Markdown strings.
- Treat concepts derived from source code and human-managed knowledge as independent information sources.
- Reference appropriate single sources of truth instead of duplicating design knowledge across multiple locations.
- Update tests when observable behavior changes.
- Keep unit tests deterministic and isolate dependencies on LLMs and external services.
- Use actual temporary directories or fixtures for file system tests, mocking only necessary external services.
- Base mocks on actual public interfaces rather than excessive reliance on internal call counts and details.
- Consolidate shareable logic into existing packages without duplicating implementations.
- Evaluate standard libraries and existing dependencies before adding new packages.
- Follow existing naming conventions, package structures, and code styles while keeping changes minimal.
- Keep codebases passing all repository checks and tests including ruff, mypy, and pytest.

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
