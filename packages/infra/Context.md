# Gyomu Infra

## Repository Overview

Gyomu Infrastructure (`gyomu-infra`) is a core infrastructure package responsible for providing shared infrastructure capabilities across the Gyomu ecosystem. Its primary role is to centralize processing related to external environment connections, such as file operations, configuration loading, CSV processing, archiving, and database access via SQLAlchemy. 

By encapsulating external library and execution environment dependencies, the package prevents upper-level packages from directly depending on infrastructure implementation details. Additionally, it handles domain-specific infrastructure concerns, including business calendar calculations, market holiday repositories, and parameter translation services.

## Package Responsibilities

- Provide core infrastructure and utility components for data parsing, file handling, and stream processing.
- Implement persistence operations, database connections, and transaction management using SQLAlchemy.
- Support domain-specific calculations and translations including business calendars, holidays, and variable resolution.
- Provide system integration helpers such as logging, process execution, configuration loading, and hashing.

## Architecture

The package is structured around several modular infrastructure areas rooted under `src/gyomu_infra`:

*   **`src/gyomu_infra/csv`**: Handles CSV data parsing, serialization, and configuration. The CSV reader utilizes parsing, encoding, and IO options to map data into validated Pydantic models, while the writer serializes Pydantic records using CSV writing configurations.
*   **`src/gyomu_infra/filesystem`**: Provides file system utilities, including text and JSON file I/O operations, file enumeration using search filter conditions, and operation helpers for access checking and exclusive access handling.
*   **`src/gyomu_infra/stream`**: Manages stream processing and I/O utilities, featuring lazy single-use streams of `Result` values via `RecordStream` and byte stream file writing functions (`stream_to_file`).
*   **`src/gyomu_infra/gyomu/date`**: Implements date-related domain logic, where the `BusinessCalendarService` performs business calendar calculations and retrieves cached calendar instances from a market holiday repository.
*   **`src/gyomu_infra/db/repository`**: Defines database abstraction layers, providing repository protocols and their corresponding SQLAlchemy implementations, such as `SqlAlchemyMarketHolidayRepository` and `SqlAlchemyParameterMasterRepository`.

## Design Principles

- Centralize external I/O and side effects into common infrastructure features to prevent upper packages from directly depending on external execution details.
- Isolate specific external library APIs and persistence implementation details behind standardized interfaces to decouple consumers from implementation specifics.
- Strictly separate the responsibilities of distinct infrastructure domains—such as file systems, databases, configurations, and data transformations—to avoid duplicated code across packages.
- Validate external data at system boundaries using schemas before treating it as internal models to prevent invalid data from propagating inward.
- Translate errors into a unified error model that retains traceability information, ensuring consistent error handling regardless of underlying infrastructure implementations.
- Prohibit the inclusion of application-specific business logic or domain knowledge within the infrastructure layer to maintain strict architectural separation.

## Important Constraints

- Do not implement business logic.
- Do not depend on application-specific domain logic.
- Do not expose external library-specific types or APIs as part of the common interface without careful abstraction.
- Do not leak infrastructure implementation details into upper application layers.
- Do not handle external data as internal application models without validation.
- Do not implement business processes that depend on specific database products or external services.

## Editing Rules

- Explicitly specify parameter and return types for public APIs and primary application logic.
- Maintain type-safe implementations compatible with strict mypy settings.
- Avoid Any and suppression of type checkers, limiting their scope and justification when necessary.
- Define and validate structured data at external boundaries using Pydantic models.
- Use appropriate data structures such as dataclasses for internal state representation.
- Do not duplicate data structures or constraints representing the same concept in multiple places.
- Express expected application failures explicitly using returns.Result, Success, and Failure.
- Avoid relying heavily on exceptions for expected failures, and handle exceptions appropriately at boundaries.
- Design package dependencies to flow from higher-level workflows to lower-level functions without circular dependencies.
- Depend only on public APIs of other packages rather than internal implementation details.
- Use Protocols and constructor injection to declare contracts for external dependencies and interchangeable logic.
- Base designs on current responsibilities and changes rather than speculative future abstractions.
- Implement side-effect-free logic as pure functions whenever possible.
- Separate I/O operations involving the file system, external services, or LLMs from business logic.
- Validate AI outputs using Pydantic models before use.
- Encapsulate AI provider-specific APIs and types within adapters or infrastructure boundaries.
- Design interfaces that abstract AI execution, routing, fallback, and retry from the caller.
- Use structured data such as concepts and analysis results as inputs for document generation.
- Maintain independent responsibilities for document composition, content, translation, and rendering.
- Use structured intermediate representations such as Document models instead of assembling Markdown strings directly.
- Keep source-derived concepts and human-managed knowledge as independent information sources.
- Update or add corresponding tests when observable behavior changes.
- Keep unit tests deterministic by isolating dependencies on LLMs and external services.
- Use temporary directories and fixtures for file system tests while mocking only necessary external services.
- Align mock dependencies with public interfaces rather than internal implementation details.
- Consolidate shareable logic into existing packages without duplication.
- Evaluate standard libraries and existing dependencies before adding new packages.
- Follow existing naming conventions, package structures, and code styles while keeping change scopes minimal.
- Maintain code that passes established linters, type checkers, and test suites including ruff, mypy, and pytest.

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
