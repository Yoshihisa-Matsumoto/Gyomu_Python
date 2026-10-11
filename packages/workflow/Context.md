# Gyomu Workflow

## Repository Overview

`gyomu-workflow` serves as the core workflow engine for the Gyomu CLI, providing an orchestration foundation for executing code analysis, concept generation, and documentation processing as a cohesive pipeline. Its primary responsibility is to manage execution order, track checkpoints, and monitor artifact states to enable process resumption and incremental updates. 

Architecturally, the package separates individual processing implementations from overall workflow control, driving the snapshot pipeline through request translation, validation, checkpoint tracking, target resolution, and specialized project actions to ensure reproducible and maintainable project processing.

## Package Responsibilities

- Manage the execution of the snapshot workflow pipeline from initial request translation to final action execution.
- Validate request parameters and Python package structures.
- Track pipeline state and step completion via persistent checkpoints and input fingerprinting.
- Resolve and filter target source files for snapshot generation.

## Architecture

The package is structurally organized around a central root directory (`src/gyomu_workflow`) that houses the core workflow execution logic, with a specialized sub-component located at `src/gyomu_workflow/snapshot`. 

- **`src/gyomu_workflow`**: Acts as the primary container for the workflow package, managing the overall snapshot workflow pipeline responsibilities.
- **`src/gyomu_workflow/snapshot`**: Implements the concrete snapshot workflow pipeline. It houses the execution runner which directly coordinates request translation and validation, checkpoint tracking and loading, target resolution, and the execution of specific pipeline actions such as docstrings, directories, LLM contexts, packages, and READMEs.

## Design Principles

- Strict separation of concerns by delegating domain logic, snapshots, and change detection to specialized external packages through defined interfaces.
- Decoupling execution flow orchestration from individual step implementations by treating steps as independent, reusable Actions.
- Isolating Checkpoints as historical records of successful execution rather than proxies for current artifact states, triggering re-execution when artifacts are absent.
- Environment-agnostic architecture ensuring workflows remain independent of specific execution interfaces like CLI, MCP, or LLM providers.
- Explicit error handling that halts subsequent step execution upon failure and returns clear failure results to callers.

## Important Constraints

- Do not implement domain logic for individual tasks; delegate processing to responsible packages (Directory Concept, Package Concept, README generation, etc.).
- Do not implement snapshot generation, persistence, or change detection logic.
- Treat checkpoints as processing completion history, not as the state of the generated artifacts themselves.
- Do not depend on specific execution environments such as CLI, MCP, or Agents.
- Do not depend directly on AI providers or LLM implementations from the workflow.
- Do not depend on the internal implementation details of lower-level packages; coordinate processing strictly through public interfaces.
- Do not share unnecessary state or implementation details between workflow steps.
- Do not execute subsequent steps when a step fails; explicitly return the failure result to the caller.
- Restrict runtime dependencies to `gyomu-schema`, `gyomu-infra`, `returns`, `gyomu-python-analysis`, `gyomu-docstring`, and `gyomu-concept`.

## Editing Rules

- Explicitly specify input and output types for all public APIs and core application logic.
- Maintain type-safe implementations that comply with strict mypy settings.
- Avoid Any and type-checking suppression, limiting their scope and justification when strictly necessary.
- Define and validate structured data for JSON, YAML, persisted data, and external boundaries using explicit schemas like Pydantic models.
- Use appropriate data structures such as dataclasses for internal state representation.
- Do not duplicate data structures or constraints for the same concept across multiple places.
- Express expected application failures explicitly using returns.Result, Success, and Failure.
- Avoid using exceptions for expected failures, and handle exceptions appropriately at system boundaries.
- Design packages with clear responsibilities and direct dependencies from upper workflows to lower functions.
- Do not introduce circular dependencies between packages.
- Depend only on public APIs of other packages rather than internal implementation details.
- Use Protocol and constructor injection to declare contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities and changes rather than speculative future abstractions.
- Implement logic as pure functions whenever side effects are absent.
- Separate I/O operations involving the file system, external services, or LLMs from business logic.
- Treat AI outputs as untrusted data and validate them with Pydantic models before use.
- Encapsulate AI provider-specific APIs and types within adapters and infrastructure boundaries.
- Separate AI execution, routing, fallback, and retry responsibilities into clean interfaces for callers.
- Use structured data such as concepts and analysis results as inputs for documentation generation.
- Treat document composition, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document instead of building Markdown strings directly.
- Treat derived concepts from source code and human-managed knowledge as independent information sources.
- Do not duplicate design knowledge across multiple management locations.
- Update or add tests when observable behavior changes.
- Keep unit tests deterministic by isolating dependencies on LLMs and external services.
- Use actual temporary directories or fixtures for file system and project structure tests, mocking only external services.
- Base mocks on actual public interfaces without over-relying on internal call counts or implementation details.
- Consolidate shareable logic into existing packages without duplicating implementations.
- Evaluate standard libraries and existing dependencies before adding new dependency packages.
- Follow existing naming conventions, package structures, and code styles while keeping change scopes minimal.
- Maintain code passing all repository linters, type checkers, and tests including ruff, mypy, and pytest.

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
