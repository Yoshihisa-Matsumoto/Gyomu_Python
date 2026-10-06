# Gyomu AI Compiler

US English | [JP 日本語](README.ja.md)

## Overview

The package serves as the compilation and execution infrastructure for AI processing within the Gyomu project. Its primary mission is to translate AI processing definitions and contexts provided by upper-level packages into structured components such as routes, prompts, execution strategies, and validations, executing them consistently through gyomu-ai.

To achieve this, the software provides specialized compilation pipelines dedicated to AI-driven code analysis and documentation generation. It establishes core data schemas, execution contexts, and renderers designed specifically for updating Python docstrings and analyzing package and directory concepts.

## Architecture

The package is organized around dedicated compilation pipelines that coordinate AI-driven code analysis and documentation generation. Responsibilities are divided into specialized pipeline domains and shared support components, separating data modeling, context management, and rendering tasks across the architecture.

The docstring update pipeline handles Python documentation modifications through dedicated context and schema components. The context subsystems model declaration and file structures, while the schema components define deterministic update plans, actions, and reasoning for parameters, raises, and returns.

Concurrently, the package concept pipeline processes directory and package structures. Its context components capture dependencies, public API symbols, and modules, while its renderer and input-building components synthesize this data into structured package analysis summaries. 

Finally, a centralized prompt management component supplies prompt templates and base configurations to drive AI interactions uniformly across the compiler framework.

## Installation

Install using uv.

```bash
uv add gyomu-ai-compiler
```

## Dependencies

This package relies on several runtime dependencies to function. It uses the `returns` package for explicit success and failure expression through Success, Failure, and Result. Additionally, it requires `gyomu-schema` for schemas and common types, `gyomu-infra` for general infrastructure processing such as I/O, and `gyomu-ai` for LLM processing.

## Development

Contributors must strictly enforce the separation of concerns by ensuring that AI models and providers are never accessed directly; all AI interactions must go through the execution mechanisms of `gyomu-ai`. Furthermore, AI tasks must be identified exclusively through Routes, cleanly separating the functional content of the AI processing from the underlying model configurations. Inputs directed at the AI need to be structured as explicit Prompts that clearly articulate the required execution context, while all outputs must be rigorously validated against defined Schemas and Validators before any downstream utilization.

To maintain system resilience and diagnostic clarity, execution retries must be strictly governed by defined Retry strategies, and any operational failures must be handled as structured Errors carrying critical diagnostic information such as the exact cause and execution phase. All necessary transformations, context tracking, and assembly logic for AI processing must reside entirely within the Compiler components. Contributors are strictly prohibited from introducing Provider-specific logic or bypassing the established compilation pipelines, thereby preserving a uniform, decoupled execution architecture across the package.

## Public API

- Docstring Generation and Updates - Defines structured schemas and execution plans for deterministic AI-driven code docstring updates, including replacement actions, parameter changes, raises, and returns.
- Package and Directory Analysis - Processes package-level and directory-level concepts, synthesizing public API symbols, dependencies, and code structure into structured inputs and analysis summaries.
- Prompt Management - Manages and loads prompt templates and base configurations to drive AI compilation tasks.

## License

MIT