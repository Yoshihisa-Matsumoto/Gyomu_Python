# Gyomu Concept

US English | [JP 日本語](README.ja.md)

## Overview

Gyomu Concept is a Python package that bridges source code analysis with human-managed knowledge to build structured project models. Its primary purpose is to represent a project's architecture, responsibilities, design intentions, and operational insights as a unified model that both humans and AI can utilize. 

Rather than functioning as a standard documentation tool, the package structures project knowledge to automatically generate comprehensive documentation, including README files and LLM contexts. By combining automated analysis with modular document definitions and section builders, it provides a consistent foundation for understanding and communicating complex project architectures.

## Architecture

The package is organized into modular components that divide responsibilities across document generation, LLM context composition, and structural analysis. The document subpackages coordinate output rendering, translation, context initialization, and asynchronous section building using configurable document definitions and file path resolvers. 

To construct specialized LLM contexts, dedicated section builders assemble specific components such as architecture, design principles, navigation, and package responsibilities. Underlying structural analysis is handled by the directory and package subpackages, which collaborate to build, process, load, persist, and manage hierarchical directory concepts, file summary records, and package dependencies.

## Installation

Install using uv.

```bash
uv add gyomu-concept
```

## Dependencies

This package relies on several runtime dependencies to function. It uses the `returns` package for explicit success and failure representations using Success, Failure, and Result types. Additionally, it integrates `gyomu-schema` for schemas and common types, `gyomu-infra` for general infrastructure processes such as I/O, and `gyomu-ai-compiler` for LLM processing during README and concept creation.

## Development

Contributors must strictly maintain the separation between the structured knowledge model and its final document representations. Because the Concept functions as an abstract knowledge model representing architecture, responsibilities, design intent, and operational knowledge, its internal schema must remain independent of specific document formats, output languages, and presentation styles. Source code analysis, Concept construction, and document generation operate as entirely independent concerns. Document generation must treat the Concept and human-managed Knowledge as input data, transforming them into format-specific structures through dedicated output renderers and file path resolvers rather than embedding formatting logic within the model itself.

All interactions involving artificial intelligence must strictly route through `gyomu-ai-compiler` to prevent direct coupling with external AI providers or specific models. While the execution mechanism is abstracted, document-specific definitions—such as content translation strategies—must be expressed directly within the Concept configuration. Furthermore, contributors need to manage different granularities of Concepts, such as Package Concept and Directory Concept, according to their distinct scopes, ensuring that hierarchical project models accurately synthesize automated source code analysis with human-curated Knowledge.

## Public API

- Document Generation and Rendering - Manages structured document generation, rendering, translation, and context initialization for creating project documentation.
- LLM Context Composition - Composes specialized sections—such as architecture, design principles, and guidelines—for constructing LLM contexts.
- Directory Concept Management - Builds, loads, processes, and persists hierarchical directory concepts and file summary records.
- Package Concept Operations - Handles package-level concepts, dependency collection, path resolution, and persistence operations.

## License

MIT