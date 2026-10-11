# Gyomu Workflow

US English | [JP 日本語](README.ja.md)

## Overview

`gyomu-workflow` serves as the core workflow engine for the Gyomu CLI, providing an orchestration foundation that executes code analysis, concept generation, and documentation processes as a cohesive pipeline. Its primary purpose is to manage execution order and track checkpoints and artifact states, ensuring that only necessary tasks are performed to enable seamless resumption and incremental updates. 

By decoupling individual task implementations from overall workflow control, the package establishes a reproducible and maintainable project environment. It drives the snapshot pipeline by coordinating request translation, validation, checkpoint tracking, target resolution, and specialized project actions.

## Architecture

The package is organized around a core snapshot workflow pipeline that drives request processing and execution. Responsibilities are divided into distinct collaborative components handling request validation, state tracking, target resolution, and action execution. 

The architecture centers on the snapshot module, which serves as the primary execution runner. It coordinates the workflow by first translating and validating user requests and package structures. It then tracks pipeline state and step completion through persistent checkpoints and input fingerprints, while resolving and filtering target source files. 

Once targets and state are verified, the runner delegates the execution of specialized project actions—such as generating docstrings, READMEs, packages, and LLM contexts—ensuring a modular and structured workflow pipeline.

## Installation

Install using uv.

```bash
uv add gyomu-workflow
```

## Dependencies

This package requires Pydantic version 2.x for schema definition, data validation, and serialization. 

Additionally, it relies on several runtime dependencies including gyomu-schema for common types and schemas, gyomu-infra for I/O and general infrastructure processing, gyomu-python-analysis for file and package analysis, gyomu-docstring for updating docstrings, and gyomu-concept for generating directory and package concepts as well as README.md files.

## Development

Contributors must strictly separate the execution order of the workflow from the detailed implementation of individual processing steps. Every workflow step must be treated as an independent Action, ensuring that the workflow engine manages only sequencing and execution conditions while delegating concrete domain tasks—such as snapshots and change detection—to specialized subordinate packages through defined interfaces. Furthermore, the package must remain agnostic to execution interfaces like CLI or MCP, ensuring that all processing logic is reusable and decoupled from specific user interaction layers.

State management relies on persistent checkpoints and input fingerprinting to track step completion, but checkpoints must be treated strictly as historical records of past success rather than proxies for current artifact existence. If a required generated artifact is missing, the corresponding step must be re-executed even if marked as completed in the checkpoint, thereby supporting incremental updates and resilient workflow resumption. Contributors must preserve this decoupling between historical state tracking and physical artifact validation to maintain predictable pipeline recovery.

Pipeline execution must adhere to fail-fast principles where the success and failure of each step are explicitly handled, preventing any downstream execution after a step fails. Contributors are strictly prohibited from introducing direct dependencies from the workflow layer onto the implementation details of lower-level packages. All interactions with domain-specific logic must strictly traverse established interfaces, preserving the boundaries required for reproducible, maintainable, and modular project processing.

## Public API

- Request Validation and Translation - Translates and validates user requests and structural requirements for generating project snapshots.
- Checkpoint and State Tracking - Tracks execution progress, file changes, and step completion using checkpoints and input fingerprints.
- Target Resolution and Filtering - Resolves snapshot targets and filters project files according to specified path patterns.
- Workflow Action Execution - Executes modular workflow actions including docstring processing, package analysis, README generation, and LLM context creation.

## License

MIT