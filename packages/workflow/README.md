# Gyomu Workflow

US English | [JP 日本語](README.ja.md)

## Overview

The package serves as an orchestration foundation for executing code analysis, concept generation, and documentation processes as a consistent workflow within Gyomu. Its primary purpose is to manage processing order and state through checkpoints, enabling seamless process resumption and incremental updates. 

By separating individual task implementations from overall workflow control, the package implements the core snapshot workflow for the Gyomu CLI. It governs project validation, structure repair, pipelined execution, and action runners for tasks like docstrings, packages, and LLM context generation, ensuring reliable state persistence and maintainable project processing.

## Architecture

The `gyomu-workflow` package is organized to handle project snapshot workflows through a set of collaborating components that divide responsibilities across validation, orchestration, state management, and task execution. 

At its core, the package validates request parameters and verifies Python project structures, automatically applying structural repairs when necessary. It orchestrates pipelined workflow execution by coordinating target resolution and managing incremental steps. 
,
State persistence is handled via checkpoints and input fingerprints, allowing the workflow to track progress reliably. Specialized action runners execute domain-specific tasks such as docstring processing, package analysis, LLM context generation, and documentation updates. Together, these components ensure a structured and resilient execution pipeline for project snapshots.

## Installation

Install using uv.

```bash
uv add gyomu-workflow
```

## Dependencies

This package requires Pydantic version 2.x for schema definition, data validation, and serialization. 

The runtime dependencies include `pydantic`, `gyomu-schema` for schemas and common types, `gyomu-infra` for I/O and general infrastructure processing, `gyomu-python-analysis` for Python package and file analysis, `gyomu-docstring` for updating Python file docstrings, and `gyomu-concept` for creating directory concepts, package concepts, and README.md files.

## Development

Contributors must enforce a strict separation of concerns between workflow orchestration and individual processing logic. The workflow engine manages execution order, step conditions, and checkpoint tracking without knowing the internal implementation details of pipeline actions, snapshot generation, or change detection. Actions must remain independent and communicate with the workflow exclusively through defined interfaces, preventing the workflow from depending directly on lower-level package implementations. Furthermore, the workflow must remain agnostic to its consumption layer, operating independently of whether it is invoked via a CLI or MCP.

State management relies on decoupled execution checkpoints and artifact existence checks. Checkpoints serve strictly as historical records of past successful steps rather than proof that generated files currently exist. If a required artifact is missing, the workflow must re-execute the necessary processing step regardless of the checkpoint status. Steps must handle success and failure explicitly, halting execution immediately upon encountering a failed step to preserve pipeline integrity and ensure deterministic, reproducible project processing.

## Public API

- Snapshot Workflow Orchestration - Orchestrates project snapshot workflows, coordinate execution steps, manage target resolution, and run targeted processing actions.
- Structure Validation and Repair - Validates Python project structures and request parameters, and provides automated structural repair mechanisms.
- State Persistence and Checkpointing - Manages pipeline state persistence, step tracking, and incremental execution via checkpoints and input fingerprints.
- Action Runners and Processing - Executes domain-specific actions including docstring processing, package analysis, LLM context generation, and documentation updates.

## License

MIT