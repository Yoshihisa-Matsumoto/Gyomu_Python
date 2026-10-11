# Gyomu Python Analysis

US English | [JP 日本語](README.ja.md)

## Overview

Gyomu Python Analysis is a comprehensive toolkit designed to serve as a robust source code inspection and analysis foundation for Python projects. Its primary purpose is to parse Python codebases, extracting code structures, declarations, and dependencies into structured analysis models. 

By managing analysis targets and configurations consistently through project and workspace contexts, the toolkit enables analysis results and project states to be handled in a reusable format. This establishes a common analysis infrastructure that empowers upper layers, such as concepts, facts, and docstrings, to effectively utilize standardized code insights.

## Architecture

The package is organized around collaborating components that divide responsibilities into workspace management, syntactic and semantic code analysis, and snapshot tracking. The core orchestration layer handles project and workspace initialization, resolving source roots, and loading module and file contexts. Code analysis is driven by a hierarchy of specialized analyzers that extract structure and metadata from Python code elements—such as classes, functions, and dependencies—while maintaining symbol context and dependency resolution data. This structural inspection is supported by AST and expression processing components that parse statements, evaluate literals and expressions, and build symbol indexes. Finally, a dedicated snapshot subsystem manages project states by enumerating target files, generating file metadata, computing differences across snapshots, and validating change management workflows.

## Installation

Install using uv.

```bash
uv add gyomu-python-analysis
```

## Dependencies

This package relies on several runtime dependencies to function. It uses the `returns` package for explicit success and failure representation via Success, Failure, and Result, while `gyomu-schema` serves as a repository for schemas and common types. 

Additionally, `gyomu-infra` is utilized for general infrastructure processing such as I/O. For parsing tasks, the package uses `griffelib` for Python syntax analysis and `docstring-parser` for docstring analysis.

## Development

Contributors must maintain a strict separation of concerns between project-level analysis and individual source file analysis, ensuring that all analysis results are derived deterministically from source code and project configurations without ever modifying the underlying code. The package relies on Project Context and Workspace Context to manage analysis targets and configurations consistently, while path resolution must follow unified rules across the entire workspace and project. Furthermore, Python-specific parsing logic must be consolidated within this shared infrastructure to prevent upper layers from taking direct dependencies on analysis library implementation details, and the resulting structured models must remain strictly read-only. State management is anchored by persisting project states as snapshots, which represent the current state of the analysis targets and must be treated independently from upper-layer processing such as document updates. Contributors must ensure that snapshot differences are tracked and change commitments are validated correctly, while clearly defining and managing project boundaries and source roots. By adhering to these constraints, the package preserves a reliable, reusable foundation that extracts code structures, declarations, and dependencies for higher layers like Concept, Facts, and Docstring.

## Public API

- Workspace and Project Context Management - Initializes and manages project workspaces, source roots, module caches, and configuration settings for Python code bases.
- Python Code Structure Analysis - Performs comprehensive structural code analysis on Python constructs, including classes, functions, variables, type aliases, imports, decorators, docstrings, and dependencies.
- AST and Expression Processing - Parses and evaluates Python statements, expressions, literals, and Abstract Syntax Trees to build symbol indexes and lookups.
- Snapshot and Change Tracking - Creates project snapshots, monitors files, computes snapshot differences, and validates change management workflows.

## License

MIT