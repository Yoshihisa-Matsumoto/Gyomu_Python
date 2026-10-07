# Gyomu Python Analysis

US English | [JP 日本語](README.ja.md)

## Overview

This package serves as a comprehensive static analysis foundation for Python projects and workspaces within Gyomu. Its primary purpose is to examine language constructs and extract source code structures, declarations, and dependencies into a unified, structured analysis model. 

By managing targets and configurations consistently through project and workspace contexts, the toolkit enables analysis results and project states to be handled in a reusable format. This establishes a common infrastructure that empowers upper layers, such as concepts, facts, and docstrings, with reliable structural insights.

## Architecture

Gyomu Python Analysis is organized into modular components that divide responsibilities across language analysis, workspace management, and version tracking. The architecture centers on analyzing Python source structures through AST parsing and dedicated analyzers for language constructs, classes, functions, types, and Pydantic models.

The analysis subsystem handles project and workspace initialization, reads configurations, manages module loading, and maintains file analysis contexts. Within this subsystem, specialized components focus on deep AST inspection of statements and expressions, alongside symbol indexing and identity resolution.

Separately, the snapshot component manages project version tracking by creating, validating, and persisting project snapshots. It collaborates with the broader architecture by tracking file modifications and computing diffs to analyze code changes over time.

## Installation

Install using uv.

```bash
uv add gyomu-python-analysis
```

## Dependencies

This package relies on several runtime dependencies for its core functionality. It uses `returns` for explicit success and failure representation via Success, Failure, and Result, while `gyomu-schema` and `gyomu-infra` serve as repositories for common types and general infrastructure processing such as I/O. Additionally, `griffelib` and `docstring-parser` are utilized for AST and docstring analysis, respectively.

## Development

Contributors must ensure that all analysis results are deterministically derived exclusively from source code and project configurations, treating the underlying code as strictly read-only to prevent any unintended modifications during execution. Project Context and Workspace Context must be maintained as the central authorities for managing parsing targets, configuration rules, and path resolution uniformly across the entire scope. To preserve clean architectural boundaries, project-level analysis and individual source file parsing must be strictly separated as independent responsibilities, ensuring that Python-specific implementation details remain encapsulated within this shared foundation and are never leaked to upper layers.

State management relies on the creation, comparison, and persistence of project snapshots, which represent the exact current state of the code over time and must be handled independently of higher-level operations such as documentation updates. Contributors are required to structure all output data as immutable, read-structured models that can be efficiently reused by Concept, Facts, and Docstring layers. Furthermore, any evolution of the codebase must respect clearly defined project boundaries and source roots, maintaining a decoupled architecture where dependent layers interact solely through the provided analysis models and context interfaces rather than direct parsing libraries.

## Public API

- Python Language Analysis - Examines Python language constructs including classes, functions, variables, imports, dependencies, docstrings, type aliases, and Pydantic models.
- AST Parsing and Indexing - Parses Python Abstract Syntax Trees to analyze statements, expressions, and build symbol indexes and identities.
- Workspace and Project Management - Initializes project and workspace contexts, reads configurations, manages module loading, and handles caching.
- Snapshot and Version Tracking - Tracks file modifications, diffs changes between versions, and handles project snapshot creation, validation, and persistence.

## License

MIT