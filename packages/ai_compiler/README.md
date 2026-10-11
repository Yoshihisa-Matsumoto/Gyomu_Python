# Gyomu AI Compiler

US English | [JP 日本語](README.ja.md)

## Overview

The package serves as an AI processing compilation and execution infrastructure within the Gyomu ecosystem. Its primary mission is to translate AI processing definitions and contexts provided by upper-level packages into structured components such as routes, prompts, execution strategies, and validation mechanisms for consistent execution via gyomu-ai.

The software provides a collection of AI compilation pipelines focused on automating developer documentation tasks, including docstring generation, README creation, document translation, and architectural concept compilation. It structures these automated workflows into modular components comprising schemas, context models, renderers, and execution logic.

## Architecture

The package is organized around modular AI compilation pipelines that automate developer documentation tasks. Responsibilities are divided across collaborating components that handle structured data schemas, context models, prompt rendering, and execution logic.

Data structures and schemas define deterministic plans and actions for tasks such as docstring updates, while dedicated context models represent declarations and files during generation processes. Rendering components format conversation messages and prompts for LLM interactions across various document sections, including project overviews, architectural concepts, and README files. 

Execution components drive specific workflows, such as document translation, by managing state, handling validations, and incorporating retry support. Together, these modular components collaborate to process source code inputs and generate structured, AI-driven documentation.

## Installation

Install using uv.

```bash
uv add gyomu-ai-compiler
```

## Dependencies

This package requires the runtime dependencies `returns` for explicit success and failure representation using Success, Failure, and Result, as well as `gyomu-schema` for schemas and common types. 

Additionally, it relies on `gyomu-infra` for general infrastructure processing such as I/O, and `gyomu-ai` for handling LLM processing.

## Development

Contributors must strictly adhere to abstraction boundaries by routing all AI processing exclusively through `gyomu-ai`, ensuring that Provider-specific logic never leaks into the compiler. AI tasks must be decoupled from underlying model configurations by relying strictly on Route identifiers for task distinction. Furthermore, all inputs must be explicitly structured as Prompts containing necessary execution contexts, while outputs require mandatory validation via defined Schemas and Validators before consumption.

Execution resilience and error management must follow standardized architectural controls. Contributors are required to use defined Retry strategies to govern execution retries and must handle all processing failures as structured Errors that retain diagnostic details such as failure causes and execution phases. Finally, all necessary transformations and component assemblies for AI processing must occur entirely within the Compiler layer, maintaining Pipelines as modular, reusable components across workflows.

## Public API

- Docstring Update Generation - Builds deterministic AI plans, actions, and schemas for automatically updating function, method, and class docstrings.
- LLM Context Rendering - Renders and formats conversation messages and prompts for generating LLM context across various document sections.
- README Documentation Generation - Constructs prompts, user data structures, and message flows for automatically generating project README documentation.
- Document Translation Execution - Executes document translation pipelines with built-in validation handling, retry support, and state management.
- Package and Directory Compilation - Analyzes and compiles high-level package and directory architectural concepts from source code inputs.

## License

MIT