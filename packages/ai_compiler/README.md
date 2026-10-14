# Gyomu AI Compiler

US English | [JP 日本語](README.ja.md)

## Overview

This package provides an AI processing compilation and execution infrastructure designed for the Gyomu project. Its mission is to transform AI processing definitions and contexts into structured components such as routes, prompts, execution strategies, and validation rules, executing them consistently through gyomu-ai. 

Serving as a specialized AI orchestration and compilation toolkit, the package automates documentation, docstring updates, package analysis, and document translation. It establishes a modular pipeline architecture that encompasses context modeling, prompt rendering, execution engines, and deterministic schema definitions tailored for code intelligence operations.

## Architecture

The `gyomu-ai-compiler` package is organized around a modular pipeline architecture that divides responsibilities into distinct functional components for AI-driven orchestration, documentation generation, and translation operations. 

Core capabilities are structured into specialized pipelines. The docstring update pipeline collaborates with dedicated schema components to define deterministic update plans, actions, and values, while context modules model file states and code declarations. Concurrently, rendering components construct LLM conversation messages, prompts, and user data structures to generate documentation sections such as architectural overviews, design principles, and README contents. 

Execution responsibilities are handled by specialized engines, such as the translation execution component, which manages document content translation alongside retry mechanisms, temporary state tracking, and validation formatting. Together, these collaborating components separate context modeling, prompt rendering, execution, and schema definition to support automated code intelligence and documentation workflows.

## Installation

Install using uv.

```bash
uv add gyomu-ai-compiler
```

## Dependencies

This package relies on several runtime dependencies to function. It uses the `returns` package for explicit success and failure expression using Success, Failure, and Result. Additionally, it integrates `gyomu-schema` for schemas and common types, `gyomu-infra` for general infrastructure processing such as I/O, and `gyomu-ai` for LLM processing.

## Development

Contributors must ensure that all AI processing relies strictly on the execution mechanisms of `gyomu-ai` rather than accessing AI models or providers directly. This separation of concerns requires that AI tasks be identified exclusively through explicit Routes, effectively decoupling the underlying model configuration from the actual content of the AI processing. Furthermore, every interaction with the AI must be assembled as an explicit Prompt that clearly structures the necessary execution context. To guarantee reliability, all AI outputs must pass through defined Schemas and Validators before use, and any execution failures must be handled as structured Errors that retain diagnostic details such as the failure cause and the specific execution phase, while execution retries are strictly governed by defined Retry strategies.

All transformations, translations, and assembly required for AI processing must occur entirely within the Compiler side, prohibiting the introduction of provider-specific logic into the execution flow. Pipelines must be purposefully engineered as reusable components that accept context and definitions from upper packages and translate them into standardized operational elements like Routes, Prompts, execution strategies, and validation layers. Contributors are expected to maintain these architectural boundaries rigidly, ensuring that the codebase preserves a deterministic, decoupled design where execution strategy, validation, and provider access remain cleanly isolated.

## Public API

- Docstring Management Schemas - Defines structured schemas, replacement actions, and execution plans for deterministic AI-driven docstring generation and code updates.
- LLM Context Rendering - Constructs conversation messages, prompts, and context structures for generating architectural overviews, constraints, and design sections.
- README Generation Pipelines - Builds prompts, data structures, and message flows for creating comprehensive README documentation sections.
- Translation Execution Engine - Executes document translation tasks incorporating retry mechanisms, temporary state tracking, and validation formatting.
- Code Declaration Contexts - Models declaration contexts, file states, and retry options to support code analysis and docstring pipelines.

## License

MIT