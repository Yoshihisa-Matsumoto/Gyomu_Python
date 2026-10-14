# Gyomu AI

US English | [JP 日本語](README.ja.md)

## Overview

The package serves as the AI execution foundation for the Gyomu project, delivering a robust framework for managing and executing AI operations built on Pydantic AI. Its primary purpose is to absorb differences between AI providers and SDKs, offering a unified mechanism for model routing, execution policies, and error handling. 

By providing standardized text, object, and embedding generation capabilities, the framework ensures that consuming packages remain decoupled from specific provider implementations. This design creates a cohesive environment where AI features can be integrated seamlessly without direct dependencies on underlying vendor interfaces.

## Architecture

The `gyomu-ai` package is organized into a set of collaborating components that divide responsibilities across model referencing, execution management, tool integration, and error handling. 

Foundational model definitions and enumerations reside in the core model module, supplying identifiers for AI models and buckets. The execution component manages runtime parameters, execution contexts, policies, and streaming events, while capturing metadata, results, and token usage statistics for text, object, and embedding generations.

The package delegates provider-agnostic execution logic and model routing to the Pydantic AI provider integration. This component interfaces with Pydantic AI to handle agent creation, prompt building, stream processing, and tool mapping. Concurrently, the tool module provides core domain logic, configurations, and result handling for AI tool executions. Finally, dedicated error and routing modules define application-specific exception types and standardized mapping across all operations.

## Installation

Install using uv.

```bash
uv add gyomu-ai
```

## Dependencies

This package is designed for Pydantic AI Version 2. 

The runtime dependencies include pydantic ai for general LLM processing, returns for explicit success and failure expression using Success, Failure, and Result, gyomu-schema as a repository for schemas and common types, and gyomu-infra for general infrastructure processing such as I/O.

## Development

Contributors must enforce strict abstraction boundaries by ensuring that AI provider-specific SDKs are never exposed directly to consumers, mandating that all interactions occur solely through Gyomu's defined abstraction layers. Architectural decisions must rely on centralized model registries and execution policies, routing every AI request exclusively through configured routing mechanisms rather than hardcoded endpoints. To maintain system resilience, contributors are required to implement structured error handling that captures diagnostic information such as the execution phase and underlying cause, while systematically mapping provider-specific outputs into standard result formats.

Execution logic must incorporate defined retry strategies to handle transient failures, alongside fallback mechanisms that seamlessly redirect operations to alternative execution paths when available. When integrating Pydantic AI for agent creation, tool mapping, prompt building, and stream processing, contributors must preserve these unified execution workflows for text, object, and embedding generation. Code contributions that bypass the standardized routing, retry policies, or error-mapping structures will violate the core architecture of the execution platform and will not be accepted.

## Public API

- Pydantic AI Integration - Integrates with Pydantic AI for model execution, prompt construction, agent creation, and streaming capabilities.
- Execution Management - Manages execution contexts, runtime policies, streaming events, token usage statistics, and result structures for AI interactions.
- AI Tool Execution - Provides core domain logic, definitions, configurations, and result handling for AI tool execution.
- Model Routing and Registry - Offers model registries, routing tables, and initialization routines for configuring AI model interactions.
- Error Handling and Mapping - Defines application-specific error types, exception mapping, and robust error handling for AI operations.

## License

MIT