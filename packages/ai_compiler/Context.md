# Gyomu AI Compiler

## Repository Overview

The `gyomu-ai-compiler` package functions as an AI processing compilation and execution infrastructure for the Gyomu project. Its primary responsibility is to transform AI processing definitions and contexts received from upper-level packages into structured components such as routes, prompts, execution strategies, and validation schemas, executing them consistently via `gyomu-ai`. 

The package operates through a modular pipeline architecture that encompasses context modeling, prompt rendering, execution engines, and deterministic schema definitions to support code intelligence operations.

## Package Responsibilities

- Define data structures and schemas for deterministic docstring update plans, actions, and values.
- Build LLM conversation messages from document context for various sections including architecture, design principles, editing rules, important constraints, and overview.
- Model declaration contexts and file contexts for updating docstrings within the docstring update pipeline.
- Execute document content translation with retry support and temporary state tracking.

## Architecture

The package is organized into modular pipelines under `src/gyomu_ai_compiler/pipelines/`, separating document updates, context generation, documentation rendering, and translation execution.

* **Docstring Updates (`src/gyomu_ai_compiler/pipelines/docstring_update/`)**: Divided into `schema` for defining data structures and plans for deterministic update actions, and `context` for modeling declaration and file contexts during docstring generation.
* **Context Rendering (`src/gyomu_ai_compiler/pipelines/llm_context/renderer`)**: Builds LLM conversation messages and structures from document contexts across sections such as architecture, design principles, editing rules, and overviews.
* **README Generation (`src/gyomu_ai_compiler/pipelines/readme/renderer`)**: Renders conversation messages and structures user data via section modules mapped to prompt builders for generating README sections like architecture, dependencies, development, and overviews.
* **Translation (`src/gyomu_ai_compiler/pipelines/translation/executor`)**: Implements the execution engine for document content translation, handling prompt construction, validation formatting, state management, retry support, and AI routing integration.

## Design Principles

- Decouple AI processing definitions from provider implementations by routing all execution through internal mechanisms, preventing upstream dependencies on specific AI vendors or SDKs.
- Isolate task semantics from model configurations using routes to ensure that modifications to underlying models do not impact core processing logic.
- Consolidate context construction and prompt compilation to maintain consistent instruction management while preventing application-specific business logic from leaking into routing layers.
- Enforce strict schema validation on all AI outputs prior to downstream consumption to mitigate uncertainties inherent in generative data.
- Handle execution failures through structured errors retaining diagnostic context and govern retries using centralized strategies rather than fragmented implementations.

## Important Constraints

- Do not call AI models or providers directly; always use `gyomu-ai`.
- Do not expose provider-specific SDKs or implementation details in the public API.
- Do not pass AI outputs to subsequent processing without validation.
- Do not introduce application-specific business logic into route or prompt construction logic.
- Do not persist AI execution results into compiler-specific persistence formats.
- Do not create architectures that expose AI provider or SDK details to upper-level packages.

## Editing Rules

- Explicitly define parameter and return types for public APIs and primary application logic.
- Maintain type-safe implementations compatible with strict mypy settings.
- Avoid Any and type-checking suppression, limiting scope and rationale when necessary.
- Use Pydantic models to define and validate structured data at external boundaries.
- Use dataclasses for internal state representations based on requirements.
- Do not duplicate concept data structures or constraints across multiple places.
- Represent expected failures explicitly using returns.Result, Success, and Failure.
- Handle exceptions at boundaries rather than using them for expected failures.
- Design dependencies to flow from higher-level workflows to lower-level features.
- Do not introduce circular dependencies between packages.
- Interact with other packages exclusively through public APIs.
- Use Protocol and constructor injection to specify contracts for external dependencies.
- Design based on current responsibilities and changes rather than speculative abstractions.
- Implement side-effect-free logic as pure functions wherever possible.
- Separate file system, external service, and LLM input/output from business logic.
- Validate AI outputs with Pydantic models before use.
- Confine AI provider-specific APIs and types to adapters and infrastructure boundaries.
- Design AI interfaces that isolate execution, routing, fallback, and retry logic from callers.
- Use structured data such as concepts and analysis results as inputs for documentation generation.
- Treat document composition, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document instead of directly assembling Markdown strings.
- Treat code-derived concepts and human-managed knowledge as independent information sources.
- Update tests when observable behavior changes.
- Keep unit tests deterministic by isolating dependencies on LLMs and external services.
- Use temporary directories and fixtures for file system and project structure tests.
- Base mock implementations on public interfaces rather than internal implementation details.
- Consolidate shareable logic into existing packages without duplication.
- Evaluate standard libraries and existing dependencies before adding new packages.
- Follow existing naming conventions, package structures, and code styles.
- Maintain a state that passes ruff, mypy, and pytest checks.

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
