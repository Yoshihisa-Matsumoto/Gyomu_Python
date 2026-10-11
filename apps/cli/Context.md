# Gyomu CLI

## Repository Overview

The `gyomu-cli` package serves as the primary command-line interface entry point for the Gyomu suite. Its architectural role is to accept user commands, arguments, and options, construct the necessary input data, and invoke underlying application features such as workflows. 

By separating command-line-specific input handling from core application logic, the package ensures that Gyomu's functionality is accessible through a consistent interface. It coordinates interactions across internal domain packages, including schema, infrastructure, AI, compilers, and workflows.

## Package Responsibilities

- Serve as the primary user-facing entry point for the gyomu application suite.
- Wire together CLI commands with underlying domain logic, AI configuration, and workflow services.

## Architecture

The package is structured around a single core entry point located in the `src/gyomu_cli` directory. 

- **`src/gyomu_cli`**: Serves as the primary architectural boundary for the command-line interface application. It houses the main Typer app instance and is responsible for registering and executing CLI commands, including user greeting, Google routing configuration, AI settings, and code snapshot generation.

## Design Principles

- Strict Separation of Concerns: The CLI layer exclusively manages command-line input interpretation and presentation, delegating all domain logic, workflow orchestration, and AI execution details to lower-level packages via public interfaces.
- Input Boundary Validation: User inputs are strictly validated and transformed into type-safe execution requests at the CLI boundary, preventing command-line specific concerns from propagating downward.
- Explicit Dependency Management: All dependencies are wired through a Composition Root pattern and passed via constructor injection to maintain clear boundaries and component isolation.
- Predictable Execution and Error Handling: Commands operate with explicit configurations, and outcomes are clearly distinguished through appropriate exit statuses and outputs to support automation and scripting.

## Important Constraints

- Do not implement domain logic, Python source code analysis, snapshot generation or comparison, concept/README/LLM context generation, or docstring parsing/generation/update/application logic within the CLI package.
- Do not duplicate workflow control logic such as execution order, checkpoints, or resumption conditions.
- Do not directly call AI provider or LLM APIs from the CLI, and do not depend on internal implementations of AI execution, routing, fallback, or retry.
- Invoke lower-level package processing exclusively through public interfaces rather than internal implementations.
- Do not delegate CLI-specific argument parsing or display formatting responsibilities to lower-level packages.
- Do not manage CLI execution state with a custom persistence mechanism unless the necessity is strictly justified.
- Avoid unnecessary dependencies on specific shells, terminals, or IDE execution environments.
- Ensure command execution results and errors are distinctly handled so success and failure can be reliably determined by callers.

## Editing Rules

- Specify argument and return types for all public APIs and core application logic.
- Maintain type-safe implementations conforming to strict mypy settings.
- Avoid Any and type-checking suppression, restricting their use and scope when necessary.
- Use Pydantic models to define and validate structured data at external boundaries and persistence layers.
- Use dataclasses for internal state representation.
- Do not duplicate data structures or constraints across multiple locations.
- Represent expected application failures using returns.Result, Success, and Failure.
- Handle exceptions at architectural boundaries rather than using them for expected failures.
- Depend on public APIs rather than internal implementation details of other packages.
- Do not introduce circular dependencies between packages.
- Use Protocols and constructor injection to define contracts for external dependencies and interchangeable logic.
- Implement side-effect-free logic as pure functions.
- Separate I/O operations involving the file system, external services, and LLMs from business logic.
- Validate AI outputs with Pydantic models before use.
- Encapsulate AI-provider-specific APIs and types behind adapters and infrastructure boundaries.
- Design interfaces that separate AI execution control, routing, fallback, and retry logic from business operations.
- Use structured data like Concepts and analysis results as inputs for document generation.
- Use structured intermediate representations like Document instead of building Markdown strings directly.
- Treat source-code-derived Concepts and human-managed Knowledge as independent information sources.
- Update tests when observable behavior changes.
- Keep unit tests deterministic by isolating LLM and external service dependencies.
- Use actual temporary directories or fixtures for file system tests, mocking only uncontrollable external dependencies.
- Mock dependencies based on public interfaces rather than internal implementation details.
- Consolidate shared logic into existing packages without duplicating implementations.
- Evaluate standard libraries and existing dependencies before adding new packages.
- Maintain code style, naming conventions, and package structure consistent with the existing codebase.
- Ensure code passes ruff, mypy, and pytest checks.

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
