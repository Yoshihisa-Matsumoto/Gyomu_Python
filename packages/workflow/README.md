# Gyomu Workflow

US English | [JP 日本語](README.ja.md)

## Overview

The gyomu-workflow package provides the core orchestration engine for the Gyomu CLI, establishing a consistent workflow for code analysis, concept generation, and documentation processing. Its primary purpose is to manage execution order and state through checkpoints, ensuring that only necessary tasks run to enable seamless resumption and incremental updates. 

By separating individual processing implementations from overall workflow control, the package delivers a reproducible and maintainable environment for project operations. It handles snapshot execution, request validation, target resolution, and specialized pipeline actions to streamline complex development tasks efficiently.

## Architecture

The package is organized around a core workflow orchestration engine that divides responsibilities into distinct operational layers. At the root package level, components handle snapshot execution, request validation, target resolution, and incremental processing through checkpoints. 

Responsibilities are further structured through specialized internal modules that collaborate to execute the pipeline. A dedicated snapshot component manages workflow execution, tracks pipeline states, and verifies Python package structures. 

These components interact within a pipeline architecture where the workflow runner coordinates snapshot execution, action configurations, and checkpoint management. Together, they drive specialized tasks such as directory generation, docstring updates, LLM context generation, package processing, and README creation.

## Installation

Install using uv.

```bash
uv add gyomu-workflow
```

## Dependencies

This package is designed for compatibility with Pydantic version 2.x. 

For runtime operations, it relies on several packages including pydantic for schema definition, data validation, and serialization, as well as gyomu-schema for shared schemas and types, gyomu-infra for I/O and baseline processing, gyomu-python-analysis for Python package and file analysis, gyomu-docstring for updating docstrings, and gyomu-concept for creating directory and package concepts along with README.md files.

## Development

Contributors must strictly separate the orchestration of workflow execution order from the concrete implementation of individual processing actions. Workflows must manage step sequences and execution conditions without handling low-level processing details, delegating tasks such as snapshot management and change detection to specialized downstream packages through defined interfaces rather than direct dependencies. Every workflow step should be treated as an independent action, and the architecture must remain completely decoupled from specific usage interfaces such as CLI or MCP to ensure the orchestration layer stays reusable.

State management relies on clear boundaries between checkpoints and artifact existence. Checkpoints must be treated strictly as historical records of past successful step execution, entirely separate from the physical presence of current generated artifacts. If an artifact is missing, the system must re-execute the required processing even if the corresponding checkpoint indicates completion. Furthermore, the execution engine must handle step success and failure explicitly, halting execution immediately so that subsequent steps do not run after a failure occurs.

## Public API

- Workflow Pipeline and Checkpoints - Orchestrates workflow execution steps, manages checkpoints for incremental processing, and tracks pipeline states.
- Request Validation and Target Resolution - Resolves target files, validates snapshot requests, and verifies Python package structures.
- Specialized Pipeline Actions - Executes specialized pipeline tasks including directory generation, docstring updates, LLM context generation, and README creation.

## License

MIT