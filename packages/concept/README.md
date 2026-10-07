# Gyomu Concept

US English | [JP 日本語](README.ja.md)

## Overview

Gyomu Concept is a core architectural tool designed to analyze, build, and manage structured software project concepts, directories, and packages. Its primary purpose is to establish a structured project model that represents architectural designs, responsibilities, intent, and operational knowledge. 

Rather than serving as a traditional document, the package bridges source code analysis with human-managed knowledge. This creates a unified knowledge representation that can be utilized effectively by both humans and AI. 

Leveraging dedicated builders and context management, the system utilizes these structured concepts and accumulated knowledge to seamlessly generate, translate, and render comprehensive project documentation and README files.

## Architecture

The Gyomu Concept package is organized around collaborating components that divide responsibilities into conceptual modeling, documentation generation, and error handling. Package and directory management components handle the structural analysis, loading, saving, and processing of source code concepts, including dependency collection and file summary records. Documentation generation is managed by dedicated components that initialize base contexts, translate assets, and render structured outputs asynchronously. These generation workflows are supported by specialized builders that construct elements such as sections and bullet lists, alongside README orchestration utilities that configure project documentation. Additionally, a dedicated error handling component defines domain-specific exceptions and phase classifications to manage faults across conceptual execution phases.

## Installation

Install using uv.

```bash
uv add gyomu-concept
```

## Dependencies

This package relies on several runtime dependencies to function. The `returns` package is used for explicit success and failure expression using Success, Failure, and Result. 

For schemas and common types, the package depends on `gyomu-schema`. General infrastructure processing such as I/O relies on `gyomu-infra`, while LLM processing for creating README and concept documentation utilizes `gyomu-ai-compiler`.

## Development

Contributors must maintain a strict separation between source code analysis, Concept construction, and documentation generation, treating them as independent responsibilities. The Concept model itself must remain decoupled from specific document formats and output languages, serving purely as a structured knowledge model that merges source code analysis with human-managed Knowledge. To ensure portability and prevent tight coupling, any AI-driven processing must be executed exclusively through `gyomu-ai-compiler`, avoiding direct dependencies on specific AI providers or models. 

Within this architecture, Concept definitions must encapsulate document-specific configurations, such as translation methods for document content, rather than embedding these rules into execution logic. Contributors are responsible for managing Concepts across varying granularities—such as Directory Concepts and Package Concepts—tailoring each to its specific structural responsibility. When building documentation, contributors must ensure that the generator treats Concepts and Knowledge strictly as input data, transforming them into the required target structures without polluting the core knowledge model.

## Public API

- Directory Concept Management - Builds, processes, loads, and saves structured conceptual representations of source code directories and their file summaries.
- Package Concept Management - Analyzes, builds, loads, saves, and processes package-level concepts and their dependency collections.
- Documentation Generation and Rendering - Generates, translates, renders, and constructs structured documentation and sections asynchronously using definitions and contexts.
- README Orchestration - Orchestrates the generation and configuration of project README files with specialized builders for overview, architecture, dependencies, and development sections.

## License

MIT