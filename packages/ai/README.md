# Gyomu AI

US English | [JP 日本語](README.ja.md)

## Overview

The package serves as a robust AI execution framework for the Gyomu project, designed to provide a unified infrastructure for artificial intelligence integration. Its primary purpose is to absorb differences between various AI providers and SDKs, decoupling consuming packages from specific third-party implementations.

Built primarily around Pydantic AI, the framework establishes a standardized approach for runtime execution, model routing, and error management. By seamlessly mapping provider-specific constructs to consistent generation, streaming, and embedding results, it ensures reliable and consistent AI operations across the entire system.

## Architecture

The package is structured into collaborating components that divide responsibilities across provider integration, execution management, tool handling, error management, and model representation. 

The provider integration layer maps Pydantic AI models, agents, tools, prompts, and results into standard internal formats. It collaborates closely with the model representation component, which defines core data structures and identification keys for AI models used across the application.

An execution environment manages runtime contexts, parameters, configuration policies, observers, and result structures for operations like text generation, streaming, object generation, and embeddings. Execution parameter configurations and contexts support model invocation and tracking, while execution results capture outputs, metadata, and token usage.

Domain logic for AI tool execution, configurations, and results is encapsulated separately, working alongside dedicated error handling modules. Application-specific error types and exceptions manage routing operations and public tool error handling to ensure robust execution across the framework.

## Installation

Install using uv.

```bash
uv add gyomu-ai
```

## Dependencies

This project requires Pydantic AI version 2.x, as it is designed around Pydantic AI Version 2. 

For runtime dependencies, the package utilizes Pydantic AI for LLM processing, `returns` for explicit success and failure handling using Success, Failure, and Result types, `gyomu-schema` for schemas and common types, and `gyomu-infra` for general infrastructure processing such as I/O.

## Development

Contributors must strictly enforce the abstraction of AI provider-specific SDKs, ensuring that consuming packages interact exclusively through Gyomu's unified interfaces rather than depending directly on external providers. All AI request executions must route exclusively through the defined Routing mechanisms to maintain centralized control over model selection and execution paths. Architecture changes must preserve the mandatory application of defined Retry strategies for handling transient execution failures, as well as the seamless utilization of Fallback mechanisms to divert traffic to alternative execution routes whenever available.

Error handling design requires that all AI execution failures are treated as structured errors capable of retaining critical diagnostic information, including failure causes and execution phases. Contributors are strictly required to transform any provider-specific outputs into standard, unified result structures native to Gyomu. Any code additions must uphold these boundaries to guarantee that model registries, agent execution, context management, and tool configurations remain decoupled from underlying SDK specifics.

## Public API

- Pydantic AI Integration - Integration layer mapping Pydantic AI models, agents, tools, prompts, and results to standard internal formats.
- Execution Environment - Management of execution context, runtime parameters, configuration policies, observers, and result structures for AI operations.
- AI Tool Execution - Core domain logic and definitions for AI tool execution, configurations, and public error handling.
- Error Handling and Routing - Application-specific error types and exception handling for routing operations.
- Model Representation - Core data structures and identification keys for AI models across the application.

## License

MIT