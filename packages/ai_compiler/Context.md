# Gyomu AI Compiler

## Repository Overview

The `gyomu-ai-compiler` package serves as the compilation and execution infrastructure for AI processing within the Gyomu project. Its primary responsibility is to transform AI processing definitions and contexts provided by upper-level packages into structured components—such as routes, prompts, execution strategies, and validation mechanisms—and execute them consistently via `gyomu-ai`. 

The package organizes these workflows into modular components, which include schemas, context models, renderers, and execution logic, to automate developer documentation tasks such as docstring generation, README creation, document translation, and architectural concept compilation.

## Package Responsibilities

- Provide pipeline execution logic and prompt rendering for AI-driven code documentation and compilation tasks.
- Define structured data schemas, actions, and context models for documentation and translation workflows.
- Manage execution state, retries, and validation handling during content generation processes.

## Architecture

The package is structurally organized around distinct pipelines under `src/gyomu_ai_compiler/pipelines/`, separating concerns into specific functional domains:

*   **Docstring Update Pipeline**: 
    *   `src/gyomu_ai_compiler/pipelines/docstring_update/schema` defines data structures and schemas for deterministic update plans, actions, reasoning, and risks.
    *   `src/gyomu_ai_compiler/pipelines/docstring_update/context` models declaration and file contexts for generating and updating Python declarations.
*   **LLM Context Pipeline**: 
    *   `src/gyomu_ai_compiler/pipelines/llm_context/renderer` builds LLM conversation messages and structures from document contexts across sections such as architecture, design principles, editing rules, constraints, and overviews.
*   **README Pipeline**: 
    *   `src/gyomu_ai_compiler/pipelines/readme/renderer` builds conversation messages and structures user data for generating README sections, mapping identifiers to architecture, dependencies, development, and overview prompt builders.
*   **Translation Pipeline**: 
    *   `src/gyomu_ai_compiler/pipelines/translation/executor` provides execution logic, retry support, temporary state management, prompt construction, and validation handling for translating document content.

## Design Principles

- Decouple AI processing definitions from underlying providers by utilizing the execution mechanism of `gyomu-ai` and prohibiting direct provider calls or exposure of provider-specific SDKs, preventing upper-layer dependencies on specific implementations.
- Separate AI tasks from model configurations using Routes to minimize the impact of model changes on AI processing implementations, while maintaining domain-agnostic route and prompt construction logic.
- Centralize input transformation, context assembly, and prompt construction within the compiler to ensure consistent management of instructions while preventing provider-specific logic leaks.
- Enforce rigorous output validation through defined schemas and validators to prevent unverified, uncertain AI-generated data from propagating into downstream processing.
- Standardize error handling, retry execution, and pipeline modularity through structured diagnostics, defined retry strategies, and reusable components to ensure reliable and extensible execution control.

## Important Constraints

- Do not invoke AI models or providers directly; always use `gyomu-ai`.
- Do not expose provider-specific SDKs or implementation details in the public API.
- Do not pass unvalidated AI outputs to downstream processing.
- Do not introduce application-specific business logic into Route or Prompt construction processes.
- Do not save AI execution results into compiler-specific persistence formats.
- Do not create architectural structures that allow upper packages to be aware of AI Provider or SDK details.

## Editing Rules

- Explicitly specify argument and return types for public APIs and primary application logic.
- Maintain type-safe implementations that comply with strict mypy settings.
- Avoid Any or suppressing type checks, limiting their scope and justification when necessary.
- Define and validate structured data at external boundaries, such as JSON, YAML, and persisted data, using explicit Pydantic schemas.
- Use appropriate data structures, such as dataclasses, for expressing internal state.
- Do not define the same data structures or constraints redundantly in multiple places.
- Express expected application failures explicitly using returns.Result, Success, and Failure.
- Handle exceptions at boundaries rather than using them to communicate expected failures.
- Design packages with clear responsibilities and direct dependencies from upper workflows to lower functions.
- Do not introduce circular dependencies between packages.
- Depend only on public APIs of other packages rather than their implementation details.
- Use Protocols and constructor injection to declare contracts for external dependencies and interchangeable processing.
- Design based on current responsibilities and changes rather than adding abstractions for hypothetical future use.
- Implement operations without side effects as pure functions whenever possible.
- Separate I/O operations involving the file system, external services, and LLMs from business logic.
- Treat AI outputs as untrusted input and validate them with Pydantic models before use.
- Isolate dependencies on AI provider-specific APIs and types within appropriate adapters or infrastructure boundaries.
- Design interfaces that decouple AI execution, routing, fallback, and retry responsibilities from callers.
- Use structured data like concepts and analysis results as inputs for document generation.
- Treat document composition, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations, such as Document objects, instead of assembling Markdown strings directly.
- Treat concepts derived from source code and human-managed knowledge as independent sources of information.
- Avoid defining the same design knowledge in multiple management locations by referencing appropriate sources.
- Update tests when observable behavior changes.
- Keep unit tests deterministic and isolate dependencies on LLMs and external services.
- Use actual temporary directories or fixtures for file system and project structure tests, mocking only necessary external dependencies.
- Align mock dependencies with actual public interfaces without relying excessively on internal call counts or implementation details.
- Consolidate shareable processing into existing packages without duplicating logic across multiple packages.
- Evaluate standard libraries and existing dependencies before adding new dependency packages.
- Follow existing naming conventions, package structures, and code styles while keeping change scopes minimal.
- Maintain code that passes repository-defined checks and tests such as ruff, mypy, and pytest.

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
