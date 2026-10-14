# Gyomu Workflow

## Repository Overview

The `gyomu-workflow` package serves as the core workflow orchestration engine for the Gyomu CLI. Its primary responsibility is to provide an orchestration foundation that manages snapshot execution, request validation, target resolution, and incremental processing through checkpoints. 

By separating workflow control from individual processing implementations, the package executes specialized pipeline actions—such as code analysis, concept generation, docstring updates, LLM context generation, package structuring, and documentation generation—as a consistent workflow. It governs execution order and monitors artifact states to enable process resumption, targeted execution of required steps, and step-by-step updates for reproducible and maintainable project processing.

## Package Responsibilities

- Manage snapshot workflow execution, targets, checkpoints, and action configurations.
- Validate and repair Python package structures and snapshot requests.
- Execute specific workflow actions such as directory generation, docstring updates, LLM context generation, package processing, and README generation.

## Architecture

The package is architecturally structured around the `src/gyomu_workflow` root and its `src/gyomu_workflow/snapshot` subdirectory. 

- **`src/gyomu_workflow`**: Serves as the top-level boundary managing core snapshot workflow execution, targets, checkpoints, action configurations, package structure validation and repair, and specialized pipeline actions.
- **`src/gyomu_workflow/snapshot`**: Acts as the lower-level component managing the core snapshot workflow execution, including checkpoints, request validation, target resolution, package structure verification, and specialized pipeline actions.

The workflow runner within the architecture coordinates snapshot execution, action execution, and checkpoint management between these areas.

## Design Principles

- Strict separation of concerns where workflows manage sequence, execution conditions, and error propagation without implementing domain logic or specific processing details.
- Decoupling execution history from artifact state by treating checkpoints strictly as historical records of successful completion rather than proxies for current output existence.
- Modularizing workflow steps into independent actions to maintain a clean boundary between individual task implementations and overall orchestration.
- Delegating specialized responsibilities such as snapshots, change detection, and domain-specific processing to dedicated external packages through well-defined interfaces.
- Ensuring environment independence so workflows remain reusable across different execution interfaces without direct dependencies on specific delivery mechanisms or AI providers.

## Important Constraints

- Do not implement domain logic for individual processes within the workflow.
- Do not implement Directory Concept, Package Concept, or README generation processes directly; delegate them to their respective responsible packages.
- Do not implement snapshot generation, persistence, or change detection logic.
- Do not treat checkpoints as the state of generated artifacts; treat them solely as execution completion histories.
- Do not depend on specific execution environments such as CLI, MCP, or Agents.
- Do not depend directly on AI providers or LLM implementations from the workflow.
- Do not depend on the internal implementation details of lower-level packages; coordinate processing exclusively through public interfaces.
- Do not share unnecessary state or implementation details between workflow steps.
- Do not execute subsequent steps when a step fails; explicitly return the failure result to the caller.

## Editing Rules

- Explicitly specify argument and return types for public APIs and primary application logic.
- Maintain type-safe implementations that comply with strict mypy settings.
- Avoid `Any` and type-checking suppressions, restricting their scope and justification when necessary.
- Define and validate structured data at external boundaries, JSON, YAML, and persistence layers using explicit schemas like Pydantic models.
- Represent internal state using appropriate data structures such as dataclasses.
- Do not define the same data structures or constraints redundantly in multiple places.
- Express expected failures explicitly using `returns.Result`, `Success`, and `Failure`.
- Handle expected failures via explicit result types rather than relying heavily on exceptions across boundaries.
- Design packages with clear responsibilities and direct dependencies from upper workflows to lower functions.
- Do not introduce circular dependencies between packages.
- Depend only on public APIs when integrating with other packages.
- Use Protocols and constructor injection to clarify contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities and changes rather than speculating on future abstractions.
- Implement side-effect-free logic as pure functions whenever possible.
- Separate input and output operations involving the filesystem, external services, and LLMs from business logic.
- Treat AI output as untrusted input and validate it with Pydantic models before use.
- Enclose dependencies on AI-provider-specific APIs and types within adapters and infrastructure boundaries.
- Design AI interfaces so that callers do not need to know implementation details of execution, routing, fallback, and retry logic.
- Use structured data such as Concepts and analysis results as inputs for document generation.
- Treat document structure, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like `Document` instead of assembling Markdown strings directly.
- Treat Concepts derived from source code and human-managed Knowledge as independent information sources.
- Update tests when observable behavior changes.
- Keep unit tests deterministic and isolate dependencies on LLMs and external services.
- Use actual temporary directories and fixtures for filesystem and project structure tests, mocking only external service dependencies.
- Mock dependencies based on actual public interfaces rather than internal call counts or implementation details.
- Consolidate shareable logic into existing packages without duplicating implementations.
- Evaluate standard libraries and existing dependencies before adding new dependency packages.
- Follow existing naming conventions, package structures, and code styles while keeping changes minimal.
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
