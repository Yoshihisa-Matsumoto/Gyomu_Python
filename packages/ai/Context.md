# Gyomu AI

## Repository Overview

The `gyomu-ai` package serves as the AI execution infrastructure for the Gyomu project, built on top of Pydantic AI. Its primary responsibility is to abstract AI providers and SDKs, providing a unified mechanism for AI execution, model routing, execution policies, tool integration, and result and error mapping. 

By centralizing these operations, the package ensures that dependent packages remain decoupled from specific AI providers and SDKs, while delivering standardized text, object, and embedding generation capabilities.

## Package Responsibilities

- Implement provider-agnostic execution logic and models for AI text, object, and embedding generation.
- Integrate with Pydantic AI to handle agent creation, tool mapping, prompt building, and stream processing.
- Manage model registries, routing configurations, and execution policies.
- Provide standardized error handling, mapping, and result formatting across AI operations.

## Architecture

The package is structurally organized around several core directories within `src/gyomu_ai/`:

- **`src/gyomu_ai/execution`**: Manages the execution environment, runtime parameters, configuration policies, observers, and result structures for AI operations, supporting model invocation and execution tracking.
- **`src/gyomu_ai/provider/pydantic_ai`**: Implements the Pydantic AI provider integration for model execution, routing, prompt building, agent creation, tool mapping, and result/error mapping. This component interacts with Google API configuration to create models, embeddings, and model registries.
- **`src/gyomu_ai/tool`**: Houses core domain logic and definitions for AI tool execution, including configurations, results, and public error handling.
- **`src/gyomu_ai/model`**: Provides foundational definitions, including type aliases (`BucketId`) and enumeration keys (`AiModelKey`) for identifying AI models and buckets.
- **`src/gyomu_ai/error`**: Defines application-specific error types and exception handling, including routing errors.

## Design Principles

- Enforce strict abstraction of AI providers and SDKs by mediating all interactions through internal interfaces, preventing provider-specific details from leaking to consumers.
- Centralize execution routing, retry strategies, and fallback mechanisms to handle transient failures and alternative pathways uniformly without consumer duplication.
- Normalize provider-specific outputs into standard result types to conceal underlying differences from upper layers.
- Represent execution failures as structured errors containing diagnostic context such as causes and execution phases rather than relying on raw exceptions or strings.
- Strictly bound the package scope to AI execution orchestration, excluding any application-specific business logic.

## Important Constraints

- Do not expose APIs that depend on specific AI providers or SDKs to consumers.
- Do not expose provider-specific implementation details to consumers.
- Do not implement application-specific business logic outside of AI execution.
- Represent AI execution failures as structured errors rather than raw exceptions or strings.
- Do not require consumers to implement duplicate execution control for retries and fallbacks.
- Depend only on permitted runtime packages (`gyomu-schema`, `gyomu-infra`, `returns`, `pydantic-ai`, `pydantic-ai-slim`).
- Preserve the existing public export structure of 68 symbols.

## Editing Rules

- Specify explicit argument and return types for public APIs and core application logic.
- Maintain type-safe implementations conforming to strict mypy settings.
- Avoid Any and type-checking suppression, restricting their scope and justification when necessary.
- Define and validate JSON, YAML, persisted data, and external boundary structures using explicit Pydantic schemas.
- Use dataclasses or appropriate data structures for internal state representation.
- Do not duplicate identical concept data structures or constraints across multiple locations.
- Express expected application failures explicitly using returns.Result, Success, and Failure.
- Handle exceptions at boundaries rather than using them to communicate expected failures.
- Design packages with clear responsibilities and direct dependencies from upper workflows to lower functions.
- Do not introduce circular dependencies between packages.
- Depend only on public APIs when integrating with other packages.
- Use Protocols and constructor injection to specify contracts for external dependencies and interchangeable processing.
- Design based on current responsibilities and changes rather than speculative future abstractions.
- Implement side-effect-free processing as pure functions whenever possible.
- Separate I/O operations involving the filesystem, external services, or LLMs from business logic.
- Treat AI outputs as untrusted data and validate them with Pydantic models before use.
- Encapsulate AI-provider-specific APIs and types within adapters or infrastructure boundaries.
- Design interfaces that separate AI execution, routing, fallback, and retry from caller implementation details.
- Use structured data such as concepts and analysis results as inputs for documentation generation.
- Treat document composition, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document instead of assembling Markdown strings directly.
- Treat code-derived concepts and human-managed knowledge as independent information sources.
- Update or add corresponding tests when observable behavior changes.
- Keep unit tests deterministic and isolate dependencies on LLMs or external services.
- Use actual temporary directories or fixtures for filesystem and project structure tests, mocking only external service dependencies.
- Align mock dependencies with actual public interfaces without relying excessively on internal call counts or implementation details.
- Consolidate shared processing into existing appropriate packages without duplicating logic.
- Evaluate standard libraries and existing dependencies before adding new dependency packages.
- Follow existing naming conventions, package structures, and code styles, keeping change scopes minimal.
- Maintain a state that passes repository checks and tests including ruff, mypy, and pytest.

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
