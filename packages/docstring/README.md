# Gyomu Docstring

US English | [JP 日本語](README.ja.md)

## Overview

This package provides a comprehensive docstring management foundation designed to automate the generation, updating, merging, and formatting of code documentation. Its primary purpose is to analyze source code contexts and structure document information, expressing updates as discrete plans before safely applying verified changes back to the source. By cleanly separating analysis, update planning, and change application, the package achieves reproducible and maintainable code documentation workflows. It also incorporates validation mechanisms to ensure that the resulting code meets established quality and linting standards.

## Architecture

The gyomu-docstring package is structured around a core set of collaborating components that manage the end-to-end lifecycle of automated docstring generation, updates, and merges. Responsibilities are divided across specialized modules that handle source context analysis, documentation planning, structural modeling, formatting, and quality control.

The package utilizes dedicated directories to separate concerns. The core update layer oversees the creation, execution, rendering, and validation of file modifications and merges, relying on internal utilities to build file contexts, formulate update and merge plans, render formatted strings, and validate signatures. A separate structural layer models the underlying lines, sections, and rendered symbols of docstrings. Additionally, a dedicated error handling component provides phase-aware exception types and custom definitions to manage update failures.

## Installation

Install using uv.

```bash
uv add gyomu-docstring
```

## Dependencies

For runtime dependencies, this package relies on `returns` for explicit success and failure expression using Success, Failure, and Result. Additionally, it uses `gyomu-schema` for schemas and common types, `gyomu-infra` for general infrastructure processing such as I/O, and `gyomu-ai-compiler` for LLM processing when creating README and concept files.

## Development

Contributors must strictly maintain the architectural separation between document generation, docstring parsing, update planning, and source code application. Docstrings are managed as direct artifacts corresponding to the source code structure, requiring file operations to be executed exclusively against normalized path models to ensure consistent processing across monorepo environments. AI-driven document content generation must remain entirely decoupled from the mechanical management and parsing of docstrings, ensuring that updates are treated as isolated, reproducible concerns rather than coupled side effects.

All modifications to docstrings must be explicitly represented as an Update Plan prior to application, allowing target signatures, modified source code, and update plans to undergo rigorous validation. Contributors must enforce this boundary between document update planning and source code application, ensuring that any changes destined for source files are handled in a verifiable format. Furthermore, developers must utilize phase-aware exception types designed specifically to handle docstring update failures, preserving the reliability and maintainability of the end-to-end lifecycle.

## Public API

- Docstring Context Analysis - Constructs structured representations of source files, declarations, and existing documentation to serve as the foundation for docstring updates.
- Update and Merge Planning - Plans and executes fine-grained additions, deletions, replacements, and semantic merges of docstring sections and symbols.
- Docstring Rendering - Renders docstring components, tags, and formatted lines into valid documentation strings.
- Validation and Quality Control - Validates docstring update plans, signatures, and resulting source code integrity using external formatting and linting tools.
- Error Handling - Provides custom exception definitions and phase tracking specifically for docstring update operations.

## License

MIT