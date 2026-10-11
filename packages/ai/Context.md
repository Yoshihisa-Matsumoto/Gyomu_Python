# Gyomu AI

## Repository Overview

Gyomu AI is a Python library that functions as a unified, provider-agnostic abstraction layer over Pydantic AI for building AI applications within the Gyomu project. Its primary responsibility is to absorb differences between AI providers and SDKs, decoupling consuming packages from direct dependencies on specific external implementations. 

The library manages execution runtimes, parameters, policies, tool execution, model registries, and dynamic model routing. Through this centralized infrastructure, it delivers consistent execution, model routing, retries, fallbacks, and error handling.

## Package Responsibilities

- Provide a unified interface for AI generation, streaming, object generation, and embedding operations.
- Integrate and manage Pydantic AI provider capabilities including model registries, agent creation, and prompt construction.
- Define execution policies, parameters, and observers for monitoring and controlling AI interactions and tool loops.
- Handle tool execution, configuration, and result mapping across AI interactions.
- Support dynamic model routing and configuration initialization within the application.

## Architecture

The package architecture is organized around five primary structural areas within `src/gyomu_ai`:

- **`src/gyomu_ai/execution`**: Manages the execution environment, runtime parameters, configuration policies, observers, and result structures. It supports model invocation, execution tracking, and captures outputs, metadata, and token usage from generation operations.
- **`src/gyomu_ai/provider/pydantic_ai`**: Implements the Pydantic AI integration. It handles model registries, agent creation, prompt building, model execution, routing, and maps Pydantic AI components (errors, results, finish reasons, and tools) to standard formats, alongside Google API integration and model settings.
- **`src/gyomu_ai/tool`**: Houses the core domain logic, classes, configurations, and results for AI tool execution, alongside public error handling structures.
- **`src/gyomu_ai/model`**: Defines the core data structures, keys, and identification representations for AI models used across the application.
- **`src/gyomu_ai/error`**: Defines application-specific exception handling and custom error types, such as routing errors.

Execution parameter configurations and execution contexts explicitly support AI model invocation and tracking across these structural boundaries, while execution results capture outputs from generation operations.

## Design Principles

- Abstract AI providers and hide SDK implementation details behind the Gyomu layer to prevent consumer dependency on specific platforms.
- Centralize AI execution routing, retry strategies, and fallback mechanisms to eliminate duplicated control logic in consuming applications.
- Normalize provider-specific outputs into standard results to conceal underlying provider differences.
- Represent execution failures as structured errors containing diagnostic metadata like execution phases rather than raw exceptions or strings.
- Strictly restrict the package scope to AI execution management without incorporating unrelated application business logic.

## Important Constraints

- Do not expose APIs that depend on specific AI providers or SDKs to the consuming side.
- Do not expose provider-specific implementation details to the consuming side.
- Do not implement application-specific business logic unrelated to AI execution.
- Represent AI execution failures as structured errors rather than raw exceptions or plain strings.
- Encapsulate retry and fallback execution control to prevent duplicate implementation by the consumer.

## Editing Rules

- Explicitly specify types for arguments and return values in public APIs and core application logic.
- Maintain type-safe implementations that comply with strict mypy settings.
- Avoid Any or suppressing type checks, and restrict their scope and rationale when necessary.
- Define and validate structured data for JSON, YAML, persisted data, and external boundaries using explicit Pydantic models.
- Use dataclasses or appropriate data structures for internal state representation according to their use case.
- Do not duplicate the same conceptual data structures or constraints across multiple locations.
- Express expected failures explicitly using returns.Result, Success, and Failure.
- Handle exceptions appropriately at boundaries rather than using them widely for expected failures.
- Design packages with clear responsibilities, directing dependencies from upper workflows to lower functions.
- Do not introduce circular dependencies between packages.
- Interact with other packages exclusively through their public APIs rather than internal implementation details.
- Use Protocol and constructor injection to specify contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities and changes rather than speculating future usage patterns.
- Implement operations without side effects as pure functions where possible.
- Separate I/O with the file system, external services, and LLMs from business logic.
- Treat AI outputs as untrusted data and validate them with Pydantic models before use.
- Confine dependencies on AI provider-specific APIs and types to appropriate adapters and infrastructure boundaries.
- Separate AI execution, routing, fallback, and retry responsibilities into interfaces that hide implementation details.
- Use structured data such as Concepts and analysis results as inputs for documentation generation.
- Treat document structure, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document instead of directly assembling Markdown strings.
- Treat Concepts derived from source code and human-managed Knowledge as independent information sources.
- Do not define identical design knowledge in multiple management locations; reference appropriate information sources instead.
- Update or add corresponding tests when observable behavior changes.
- Keep unit tests deterministic and isolate dependencies on LLMs or external services.
- Use actual temporary directories or fixtures for file system and project structure tests, mocking only controllable external dependencies.
- Base mock implementations on actual public interfaces without over-relying on internal call counts or details.
- Consolidate shareable logic into existing packages without duplicating implementations.
- Evaluate standard libraries and existing dependencies before adding new dependency packages.
- Follow existing naming conventions, package structures, and code styles while keeping changes minimal.
- Maintain a state that passes repository inspections and tests including ruff, mypy, and pytest.

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
