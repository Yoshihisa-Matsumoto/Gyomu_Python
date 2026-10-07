# Gyomu Workflow

US English | [JP 日本語](README.ja.md)

## Overview

The package powers the snapshot workflow engine for the Gyomu CLI, providing an orchestration foundation to execute code analysis, concept generation, and documentation generation as a unified pipeline. Its primary purpose is to manage execution order and monitor artifact states with checkpoints, enabling process resumption and incremental updates. By separating individual processing logic from overall workflow control, the package achieves reproducible and maintainable project operations. It handles execution pipelines, checkpoint management, target file resolution, and project structure validation to ensure consistent execution.

## Architecture

The `gyomu-workflow` package is organized around a core snapshot module that drives the workflow engine for the Gyomu CLI. Responsibilities are divided into distinct components that handle workflow orchestration, state persistence, target resolution, and validation.

The top-level `src/gyomu_workflow` package coordinates overall snapshot workflows, while the nested `snapshot` directory houses the concrete mechanisms for execution and validation. Together, these components collaborate to run pipeline steps, execute actions on target files, manage checkpoints for state tracking, and enforce configuration schemas and package structure rules.

## Installation

Install using uv.

```bash
uv add gyomu-workflow
```

## Dependencies

This package is designed for Pydantic version 2.x compatibility. 

Runtime dependencies include `pydantic` for schema definition, data validation, and serialization or deserialization. It also relies on `gyomu-schema` for schemas and common types, `gyomu-infra` for general infrastructure processing such as I/O, `gyomu-python-analysis` for Python package and file analysis, `gyomu-docstring` for updating Python file docstrings, and `gyomu-concept` for creating directory concepts, package concepts, and README.md files.

## Development

Contributors must enforce a strict separation between workflow orchestration and the underlying task implementations. The workflow engine manages execution order, step conditions, and state transitions, but it must delegate specialized tasks—such as snapshots and change detection—to their respective dedicated packages through defined interfaces rather than depending on implementation details. Furthermore, the orchestration layer must remain completely agnostic of delivery mechanisms like CLIs or MCPs, ensuring that workflow logic remains reusable and isolated from external interfaces.

To ensure reproducible and maintainable project processing, the state management system relies on checkpoints that record successful step execution independently of physical artifact existence. If a required artifact is missing, the workflow must re-execute the necessary step even if the checkpoint marks it as completed. Contributors must implement steps as independent actions that handle success and failure explicitly, halting execution immediately upon any step failure and executing only the steps required based on current checkpoints and artifact states.

## Public API

- Workflow Orchestration - Orchestrates the execution of snapshot workflows, coordinating pipeline steps, validating request parameters, and running actions on target files.
- Checkpoint Management - Manages snapshot state, persistence through checkpoints, and history tracking across workflow runs.
- Target Resolution and Filtering - Resolves target files and directories for snapshot execution, applying file filters and pattern matching.
- Configuration and Validation - Defines core data models, request configurations, and validation rules for snapshot execution and Python package structures.

## License

MIT