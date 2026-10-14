# Gyomu CLI

## Repository Overview

The `gyomu-cli` package serves as the primary command-line interface for the application, built using Typer. It acts as an execution interface that receives user commands, arguments, and options, constructs the necessary input data for core workflows, and invokes underlying application functions. 

By separating command-line input processing from application business logic, the package orchestrates user commands, coordinates code snapshot execution, and integrates configuration settings for AI and routing services by leveraging core domain and infrastructure packages, thereby providing a consistent interface to the application's capabilities.

## Package Responsibilities

- Provide the main user-facing command-line interface and application entry point.
- Coordinate code snapshot requests and execution flow.
- Initialize and register AI configurations and routing mechanisms.

## Architecture

The package is structured around a single core directory, `src/gyomu_cli`, which acts as the primary architectural boundary for the application. 

- **`src/gyomu_cli`**: Serves as the core command-line interface package. It houses the main application entry point and encapsulates all application logic related to user command handling, code snapshot execution, and the registration of Google routing and AI configuration.

## Design Principles

- Separates command-line interface concerns from application logic to prevent interface-specific changes from propagating to lower-level packages and to enable alternative execution interfaces such as MCP to reuse existing processing logic.
- Enforces strict input boundary validation, transforming command-line arguments and options into type-safe execution requests through consistent naming and predictable, explicit behavior.
- Delegates all workflow control, execution sequencing, error recovery, and AI model interactions exclusively to downstream packages through defined public interfaces rather than implementing them within the CLI.
- Establishes dependencies centrally using a Composition Root pattern, passing required dependencies explicitly via constructor injection to maintain clear component boundaries.
- Distinguishes cleanly between processing results and errors, returning appropriate exit statuses to support both interactive usage and automated scripting.

## Important Constraints

- Do not implement domain logic for individual features within the CLI.
- Do not implement Python source code parsing, snapshot generation/comparison, or generation logic for concepts, READMEs, or LLM context.
- Do not implement docstring parsing, generation, updating, or application logic.
- Do not duplicate workflow processing order, checkpoint, or resumption control logic.
- Do not call AI providers or LLM APIs directly from the CLI.
- Do not depend on internal implementations of AI execution, routing, fallback, or retry mechanisms.
- Invoke downstream processing exclusively through public interfaces rather than internal implementations.
- Do not delegate CLI-specific argument parsing or display formatting to downstream packages.
- Do not manage CLI execution state with a custom persistence mechanism without clear necessity.
- Do not introduce unnecessary dependencies on specific shells, terminals, or IDE execution environments.
- Ensure command execution results and errors are explicitly handled so success and failure can be distinguished by the caller.

## Editing Rules

- Explicitly specify argument and return types for public APIs and primary application logic.
- Maintain type-safe implementations compatible with strict mypy settings.
- Avoid Any and type-checking suppression, limiting scope and rationale when necessary.
- Define and validate structured data at external boundaries, persistent storage, and serialization using Pydantic models or equivalent schemas.
- Use dataclasses or appropriate data structures for internal state representation.
- Do not duplicate data structures or constraints for the same concept across multiple locations.
- Express expected application failures explicitly using returns.Result, Success, and Failure.
- Do not rely on implicit exceptions for expected failures, and handle exceptions at boundaries.
- Design packages with clear responsibilities and unidirectional dependencies from upper workflows to lower functions.
- Do not introduce circular dependencies between packages.
- Interact with other packages strictly through their public APIs rather than implementation details.
- Leverage Protocol and constructor injection to declare contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities and changes rather than speculative future abstractions.
- Implement side-effect-free logic as pure functions whenever possible.
- Isolate I/O operations with the file system, external services, and LLMs from business logic.
- Treat AI outputs as untrusted input and validate them with Pydantic models before use.
- Confine AI-provider-specific APIs and types within adapters or infrastructure boundaries.
- Separate AI execution, routing, fallback, and retry responsibilities behind clean interfaces.
- Use structured data such as concepts and analysis results as inputs for document generation.
- Treat document composition, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document rather than building Markdown strings directly.
- Treat source-code-derived concepts and human-managed knowledge as independent information sources.
- Update tests when observable behavior changes.
- Keep unit tests deterministic and isolate dependencies on LLMs and external services.
- Use temporary directories or fixtures for file system tests while mocking only uncontrollable external dependencies.
- Mock dependencies based on public interfaces rather than internal implementation details or call counts.
- Consolidate shareable logic into existing packages without duplication.
- Evaluate standard libraries and existing dependencies before adding new packages.
- Maintain existing naming conventions, package structures, and minimal change scopes.
- Pass all repository checks and tests including ruff, mypy, and pytest.

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
