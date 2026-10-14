# Gyomu AI

US English | [JP 日本語](README.ja.md)

## Overview

The package provides a robust execution framework for AI operations within the Gyomu project, built on top of Pydantic AI. Its primary purpose is to absorb differences across various AI providers and SDKs, delivering standardized text, object, and embedding generation. 

By unifying model routing, execution policies, tool integration, and error handling under a single mechanism, the framework ensures that consuming packages remain decoupled from specific underlying providers.

## Architecture

The `gyomu-ai` package is organized into a set of collaborating components that divide responsibilities across model referencing, execution management, tool integration, error handling, and provider-specific logic. 

Foundational model definitions and enumerations reside in the core model module, while application-specific exceptions and routing errors are managed by a dedicated error module. The execution component governs runtime parameters, context management, streaming events, and token usage statistics for text, object, and embedding generations. The tool component supplies domain logic, configurations, and result structures for AI tool execution.

These capabilities are unified through the Pydantic AI provider integration. This provider component handles model registries, routing configurations, agent creation, prompt building, and stream processing. It directly interacts with execution policies and maps provider-specific results and errors into standardized application formats.

## Installation

Install using uv.

```bash
uv add gyomu-ai
```

## Dependencies

This package is designed for Pydantic AI version 2.x compatibility. For runtime dependencies, it utilizes Pydantic AI for general LLM processing, returns for explicit success and failure expressions using Success, Failure, and Result, gyomu-schema for schemas and common types, and gyomu-infra for general infrastructure processing such as I/O.

## Development

Contributors must strictly enforce provider-agnostic execution across all AI text, object, and embedding operations, ensuring that provider-specific SDKs are never exposed directly to consumers. Instead, all interactions must flow through Gyomu's internal abstraction layers, utilizing Pydantic AI for agent creation, tool mapping, prompt building, and stream processing. When implementing changes, maintain the model registry and routing configurations as the mandatory gateway for every AI request, preventing bypass of the defined execution paths.

All execution logic must integrate robust operational policies directly into the call lifecycle. Temporary failures during AI execution require strict adherence to the defined retry strategies, while persistent or qualifying failures must leverage fallback mechanisms to seamlessly switch to alternative execution routes. Furthermore, contributors must standardize all error handling by converting provider-specific outcomes into uniform, structured errors that preserve critical diagnostic information such as the underlying cause and the execution phase.

## Public API

- Pydantic AI Integration - Integrates with Pydantic AI for model execution, prompt construction, agent creation, and streaming capabilities.
- Execution Management - Manages execution contexts, runtime policies, streaming events, token usage statistics, and result structures for AI interactions.
- AI Tool Execution - Provides core domain logic, definitions, configurations, and result handling for AI tool execution.
- Model Routing and Registry - Offers model registries, routing tables, and initialization routines for configuring AI model interactions.
- Error Handling and Mapping - Defines application-specific error types, exception mapping, and robust error handling for AI operations.

## License

MIT