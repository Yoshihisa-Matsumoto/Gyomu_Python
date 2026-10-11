# Gyomu Concept

US English | [JP 日本語](README.ja.md)

## Overview

Gyomu Concept is a core Python package that structures project architecture, responsibilities, design intent, and operational knowledge. Its primary purpose is to build structured project models by combining code analysis with human-managed knowledge, serving as a shared knowledge representation for both humans and AI. 

The package is responsible for constructing directory and package concepts and utilizing this structured information to generate project documentation and LLM contexts. It provides a modular framework encompassing document building, translation, section assembly, and markdown rendering, all supported by domain-specific error handling.

## Architecture

The package is organized around collaborating components that divide responsibilities into domain analysis, document generation, and error management. Core logic is structured to separate filesystem and package-level abstractions from output rendering. 

Project structure analysis is handled by dedicated components that build, process, load, save, and manage directory concepts, file summary records, and package dependencies. These internal mechanisms handle path resolution and state persistence to supply accurate structural data.

The document generation framework collaborates with specialized builders, context initializers, and markdown renderers to compile project overviews, such as README files and LLM contexts. Asynchronous section builders process enabled sections and translations to assemble the final output. 

Finally, a dedicated error-handling component classifies exceptions using domain-specific error classes and execution phase definitions, ensuring robust error management across both concept analysis and document building workflows.

## Installation

Install using uv.

```bash
uv add gyomu-concept
```

## Dependencies

This package relies on several runtime dependencies for its core functionality. It uses `returns` for explicit success and failure representation via Success, Failure, and Result, while `gyomu-schema` serves as the repository for schemas and common types. 

Additionally, the package utilizes `gyomu-infra` for general infrastructure processing such as I/O operations, and `gyomu-ai-compiler` to handle LLM processing when creating READMEs and concepts.

## Development

Contributors must treat the Concept as a structured knowledge model that represents project architecture, responsibilities, design intent, and operational knowledge without depending on specific document formats or output languages. Because the Concept functions as a shared knowledge representation for both humans and AI, it must be constructed by combining source code analysis results with human-managed Knowledge, while keeping source code analysis, Concept construction, and document generation strictly independent as separate responsibilities. Furthermore, different granularities of Concepts—such as Package and Directory concepts—must be managed distinctly according to their specific responsibilities.

When implementing AI-driven processes, contributors must execute them exclusively through `gyomu-ai-compiler` to prevent direct dependencies on AI providers or specific models. Document-specific definitions, such as the translation methods for document content, must be explicitly expressed on the Concept side rather than embedded within AI execution logic. During document generation, the system must treat Concepts and Knowledge purely as inputs to transform into document-specific structures, ensuring domain-specific error management and phase classifications are properly applied for robust error handling across all build, processing, dependency collection, and persistence operations.

## Public API

- Document Generation Framework - Defines document generation structures, base contexts, renderers, models, and asynchronous building blocks for documentation and project overviews.
- Directory Concept Management - Builds, processes, loads, saves, and manages directory concepts and file summary records from filesystem paths.
- Package Analysis and Concepts - Handles package-level analysis, concept building, dependency collection, path resolution, and internal state persistence.
- README Generation - Provides specialized document definitions, contexts, section builders, and markdown renderers for generating project README files.
- LLM Context Generation - Supplies specialized document definitions, contexts, section builders, and markdown renderers for compiling LLM context files.
- Domain Error Handling - Defines domain-specific error classes, exception types, and phase classifications for error handling across concepts and document building.

## License

MIT