# Gyomu Python Analysis

US English | [JP 日本語](README.ja.md)

## Overview

This package provides a comprehensive Python source code analysis foundation for Gyomu. Its primary purpose is to parse Python projects and workspaces, extracting structural elements, declarations, and dependencies into a unified, structured analysis model. 

The software manages analysis targets and configurations consistently through project and workspace contexts. By representing results and project states in a reusable format, it delivers a shared analysis infrastructure that upper layers can utilize for concepts, facts, and documentation.

## Architecture

The package is organized into collaborating components that divide responsibilities across project management, code analysis, AST inspection, and snapshot tracking. 

The workspace and project context layer handles initialization, discovers package roots, parses configuration files, and manages module loading and caching. Building upon this context, the core analyzers extract structural metadata, types, decorators, imports, docstrings, and dependencies from Python code elements, including Pydantic models.

For granular code inspection, the AST and expression utilities parse statements and expressions, evaluate literal values, and build symbol and class indexes. Finally, the snapshot component manages project state by enumerating target files, generating version metadata, and computing structural differences to track code evolution across versions.

## Installation

Install using uv.

```bash
uv add gyomu-python-analysis
```

## Dependencies

This package relies on several runtime dependencies to function. It uses `returns` for explicit success and failure representation via Success, Failure, and Result types. For schemas and common types, it utilizes `gyomu-schema`, while `gyomu-infra` handles general infrastructure processing such as I/O. Additionally, `griffelib` is used for Python syntax analysis, and `docstring-parser` is required for parsing docstrings.

## Development

Contributors must enforce strict boundaries between project-level analysis and individual source file parsing, ensuring these responsibilities remain entirely independent. All analysis results must be derived deterministically from the source code and project settings, and exposed strictly as read-only, structured models that never modify the underlying source files. Project Context and Workspace Context must be utilized consistently to manage analysis targets, configuration, and module discovery, while path resolution must follow uniform rules across the entire project and workspace to maintain reliable module boundaries and source root definitions.

To support upper layers such as Concept, Facts, and Docstring without leaking implementation details, all Python-specific parsing logic must be consolidated within this shared foundation. Project states must be persisted exclusively as Snapshots to track code evolution and enable reuse by subsequent processes, keeping Snapshot generation strictly isolated from upper-layer tasks like document updates. Contributors must preserve these structural constraints to guarantee that the analysis model remains a reliable, side-effect-free representation of the codebase's current state.

## Public API

- Python Code Analysis - Extract structural metadata, types, decorators, and definitions from Python code elements including classes, functions, variables, and Pydantic models.
- Project and Workspace Context - Initialize workspaces, parse configuration files, discover package roots, and load and cache Python modules.
- Snapshot Management - Create project snapshots, enumerate target files, track changes, and compute structural differences across versions.
- AST Inspection and Indexing - Parse and inspect Abstract Syntax Trees to evaluate Python statements, expressions, and build symbol indices.

## License

MIT