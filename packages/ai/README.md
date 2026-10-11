# Gyomu AI

US English | [JP 日本語](README.ja.md)

## Overview

Gyomu AI is a Python library that serves as the AI execution foundation for the Gyomu project, providing a unified, provider-agnostic abstraction layer over Pydantic AI. Its primary mission is to absorb differences across various AI providers and SDKs, ensuring that applications utilizing AI features do not depend directly on any single provider. 

The package achieves this by delivering a consistent framework for execution runtimes, parameters, policies, tool execution, model registries, and dynamic model routing. By centralizing operations such as AI execution, model routing, retries, fallbacks, and error handling, it streamlines the development of robust and adaptable AI applications.

## Architecture

Gyomu AI is organized around a set of collaborating components that divide responsibilities across provider integration, execution management, tool handling, model definition, and error management. 

The provider integration component serves as the bridge to Pydantic AI, handling model registries, agent creation, prompt building, and the mapping of native constructs to standard formats. The execution runtime component manages the execution environment, runtime parameters, configuration policies, observers, and token usage statistics for text, object, and streaming generation. 

Supporting these operational layers, the tool component houses the core domain logic and result structures for tool execution, while the model component defines foundational AI model representations and identification keys. Finally, the error handling component manages application-specific exceptions, including dedicated routing errors, ensuring standardized error reporting across operations.

## Installation

Install using uv.

```bash
uv add gyomu-ai
```

## Dependencies

This package is designed for Pydantic AI version 2.x compatibility. For runtime operations, it relies on pydantic ai for general LLM processing, returns for explicit success and failure representation using Success, Failure, and Result, gyomu-schema for schemas and common types, and gyomu-infra for general infrastructure processing such as I/O.

## Development

Contributors must strictly maintain the abstraction layer that decouples consumer packages from underlying AI provider SDKs. All AI interactions must flow exclusively through the defined Routing mechanisms rather than invoking provider-specific logic directly. Code additions must respect this boundary, ensuring that provider-specific result types are systematically mapped into standardized Gyomu results, and that underlying SDK changes remain internal to this execution infrastructure.

Resilience and observability are mandatory requirements for any extensions to the execution pipeline. Temporary failures during AI execution must be intercepted and handled according to defined Retry strategies, while Fallback mechanisms must be seamlessly engaged to route requests to alternative execution paths when available. Furthermore, all execution failures must be caught and re-raised as structured errors that encapsulate comprehensive diagnostic details, including execution phases and root causes, to ensure predictable behavior across all integrated AI operations.

## Public API

- AI Provider Integration - Integrates Pydantic AI models, registries, and agents with standardized error, result, and tool formats.
- Execution Runtime Management - Manages execution contexts, runtime parameters, tool loop policies, observers, and token usage statistics for AI operations.
- AI Tool Execution - Defines domain logic, configurations, and result structures for executing AI tools.
- Model Routing and Configuration - Configures and executes dynamic model routing rules and routing error handling.
- Core Domain Models - Defines core data structures for AI model representations and application-specific errors.

## License

MIT