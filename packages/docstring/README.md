# Gyomu Docstring

US English | [JP 日本語](README.ja.md)

## Overview

This package serves as a core management infrastructure for Python source code docstrings. Its primary mission is to automate the generation, updating, merging, and validation of documentation within source files, ensuring high maintainability and reproducibility.

The package parses docstrings to treat them as structured document information and represents updates as distinct plans. By cleanly separating the processes of analysis, update planning, and change application, it enables the safe reflection of verified modifications back into the source code.

## Architecture

The package is organized around a core update module that coordinates the end-to-end lifecycle of docstring generation, merging, and validation. Responsibilities are divided into specialized components that handle context analysis, planning, rendering, and validation. 

Context analysis constructs declaration and file targets, feeding data into the planning components which manage symbol updates, conflict resolution merges, and retry logic. A dedicated rendering engine formats docstring sections, lines, and tags according to specifications, while execution and validation components apply the updates to source files and verify them using external formatters and linters. 

Supporting these operational flows, specialized error management components define custom exception types to handle update failures gracefully across the package.

## Installation

Install using uv.

```bash
uv add gyomu-docstring
```

## Dependencies

This package relies on several runtime dependencies to function. The `returns` package is used for explicit success and failure representation via Success, Failure, and Result types. Additionally, `gyomu-schema` serves as a repository for schemas and common types, `gyomu-infra` handles general infrastructure processes such as I/O, and `gyomu-ai-compiler` is utilized for LLM processing during README and concept creation.

## Development

Contributors must enforce a strict architectural separation between documentation planning, AI content generation, and code modification. Docstring parsing and document generation must remain decoupled to ensure that structural analysis of the source code is independent of how documentation sections, lines, and tags are rendered and formatted. Furthermore, AI-driven content generation must be isolated entirely from the core docstring management logic, ensuring that automated generation processes act strictly as upstream inputs rather than embedded routines within the management engine.

All update operations must be governed by an explicit intermediate representation, where requested changes to declarations are expressed as an Update Plan prior to execution. File operations must exclusively utilize normalized path models as a baseline across all environments, guaranteeing consistent document update behavior within monorepo structures. Code modifications must be treated as verifiable artifacts, requiring validation of the updated code source before any changes are safely applied back to the original Python files.

## Public API

- Docstring Context Analysis - Constructs file and declaration contexts to identify documentable code targets and dependencies.
- Update and Merge Planning - Plans, builds, and retries docstring updates and conflict resolution merges.
- Docstring Rendering Engine - Formats and renders docstring lines, tags, and strings according to specification.
- Execution and Validation - Executes file updates and validates resulting code using formatting and linting tools.
- Error Management - Defines specialized error types and handling for docstring update failures.

## License

MIT