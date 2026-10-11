# Gyomu Python Analysis

## Repository Overview

Gyomu Python Analysis provides a foundational Python source code analysis infrastructure for Gyomu. Its primary responsibility is to inspect Python projects and workspaces, extracting source code structures, declarations, and dependencies into structured analysis models. 

By managing analysis targets and configurations consistently through Project and Workspace Contexts, the package enables the representation of analysis results and project states in a reusable format. It acts as a common analysis base layer that supplies structured data for upper layers such as Concept, Facts, and Docstring.

## Package Responsibilities

- Manage project and workspace configurations, source roots, and file enumerations for Python codebases.
- Analyze Python source code syntax, types, constructs, and metadata via AST parsing and expression evaluation.
- Track project file states, compute differences across snapshots, and validate change commitments.
- Provide symbol context and dependency resolution data during code structure analysis.

## Architecture

- **`src/gyomu_python_analysis/analysis`**: Serves as the core orchestration layer, responsible for project and workspace initialization, module and file context loading, cache management, metadata registration, and source root resolution.
- **`src/gyomu_python_analysis/analysis/analyzers`**: Provides core analyzers utilized by the analysis layer to extract structure, metadata, and dependencies from Python code elements. It maintains symbol context and relies on specialized subcomponents.
- **`src/gyomu_python_analysis/analysis/analyzers/ast`**: Sub-component providing AST-based code analysis capabilities, handling statements, expressions, and the construction of symbol and class/function indexes.
- **`src/gyomu_python_analysis/analysis/analyzers/expression`**: Sub-component nested under analyzers that delegates to specific handlers for analyzing various Python expression types and parsing literal values.
- **`src/gyomu_python_analysis/snapshot`**: Manages project snapshots independently, handling file enumeration, metadata generation, workspace identification, and computing changes or differences between previous and current snapshots.

## Design Principles

- Ensure deterministic derivation of analysis results strictly from source code and project configurations without incorporating AI-based inference or semantic analysis.
- Maintain strict separation of concerns between independent layers, isolating project-level and source-file-level analysis from upper-layer documentation generation, source code modification, and application-specific decision logic.
- Encapsulate Python-specific parsing mechanics within a centralized common foundation to prevent upper layers from directly depending on underlying analysis library implementation details.
- Manage analysis targets, project boundaries, source roots, and path resolution uniformly across projects and workspaces using centralized Context structures.
- Provide analysis results as read-only structured models and persist project states as immutable Snapshots to enable safe reusability across multiple downstream processes without side effects.

## Important Constraints

- Do not modify source code.
- Do not generate or update documentation, including READMEs and design documents.
- Do not generate, update, or apply docstrings.
- Do not implement AI-based inference or semantic analysis.
- Do not introduce project-specific analysis logic into the common analysis infrastructure.
- Do not expose implementation details of Python analysis libraries as part of the upper layer's public API.
- Do not implement application-specific decision logic that relies on analysis results.
- Do not couple analysis processing with documentation update processing.

## Editing Rules

- Explicitly specify parameter and return types for public APIs and primary application logic.
- Maintain type-safe implementations compatible with strict mypy settings.
- Avoid Any and type-checking suppression, limiting scope and rationale when necessary.
- Use explicit schemas such as Pydantic models to define and validate structured data at system boundaries.
- Use appropriate data structures like dataclasses for internal state representation.
- Do not duplicate the same data structures or constraints in multiple places.
- Represent expected application failures explicitly using returns.Result, Success, and Failure.
- Handle exceptions at system boundaries rather than using them for expected business failures.
- Design packages with clear responsibilities and unidirectional dependencies from higher-level workflows to lower-level functions.
- Do not introduce circular dependencies between packages.
- Rely on public APIs rather than internal implementation details when interacting with other packages.
- Use Protocols and constructor injection to define contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities and changes rather than speculative future abstractions.
- Implement stateless computations as pure functions where possible.
- Isolate side-effecting operations involving the file system, external services, or LLMs from business logic.
- Treat AI outputs as untrusted data and validate them with Pydantic models before use.
- Encapsulate AI provider-specific APIs and types within adapters and infrastructure boundaries.
- Design clean interfaces that separate AI execution, routing, fallback, and retry concerns from callers.
- Use structured data such as concepts and analysis results as inputs for documentation generation.
- Treat document structure, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document instead of building Markdown strings directly.
- Treat source-derived concepts and human-managed knowledge as independent information sources.
- Reference appropriate single sources of truth instead of duplicating design knowledge.
- Update or add corresponding tests when observable behavior changes.
- Keep unit tests deterministic by isolating LLMs and external services.
- Use actual temporary directories or fixtures for file system and project structure tests, mocking only external service dependencies.
- Base mock dependencies on public interfaces rather than internal implementation details or call counts.
- Consolidate shareable logic into existing packages without duplicating implementations.
- Evaluate standard libraries and existing dependencies before adding new packages.
- Follow existing naming conventions, package structures, and code styles while keeping change scopes minimal.
- Ensure code passes all repository checks and tests including ruff, mypy, and pytest.

## Navigation

This document provides a high-level overview of the package concept, responsibilities, and design decisions.

For more detailed information, refer to the following documents:



- **Architecture Documentation**
  Describes the internal architecture, major components, dependencies, and design decisions of this package.

- **API Reference**
  Describes public APIs, exported modules, and usage patterns.

- **Technical Documentation**
  Describes technical details, configuration, dependencies, and implementation-specific information.

- **Development Guide**
  Describes development workflows, coding conventions, testing strategies, and contribution guidelines.

- **Project Knowledge**
  Contains additional knowledge maintained by developers, including constraints, rationale, terminology, and operational guidelines.


When modifying this package, review the relevant documentation before making changes to preserve the intended responsibilities and architectural boundaries.
