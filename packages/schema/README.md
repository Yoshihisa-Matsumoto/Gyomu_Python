# Gyomu Schema

US English | [JP 日本語](README.ja.md)

## Overview

The package provides canonical data models, validation rules, and schemas for the Gyomu ecosystem. Its primary purpose is to define shared schemas, type definitions, error types, protocols, and general utilities that establish data contracts between features like Python analysis, concepts, documents, knowledge, and snapshots. 

By defining these foundational contracts, the package maintains type safety and data consistency across the ecosystem while keeping package dependencies loosely coupled.

## Architecture

The package is structured around a centralized collection of domain-specific data models and validation rules that serve the Gyomu ecosystem. Responsibilities are divided into specialized modules handling Python code analysis, structured documents, error management, and knowledge representation, supported by underlying utility and serialization frameworks.

Code analysis is organized into dedicated components for modeling Python AST expressions, statements, type structures, and higher-level code constructs like classes, functions, modules, and dependencies. Concurrently, document and knowledge management components provide structured definitions, validation rules, and translation configurations for content elements, guidelines, technical references, and operational roadmaps.

Standardized domain error handling cuts across these layers, supplying base error classes, operational phases, and resolution strategies for AI, configuration, database, I/O, and validation tasks. These collaborating components ensure consistent schema enforcement, serialization, and validation across all application operations.

## Installation

Install using uv.

```bash
uv add gyomu-schema
```

## Dependencies

This package is designed for Pydantic version 2.x, which is required for schema definition, data validation, serialization, and deserialization. For runtime usage, the package relies on Pydantic and utilizes returns for explicit success and failure representation using Success, Failure, and Result.

## Development

Contributors must ensure that this package remains the independent shared foundation of the Gyomu ecosystem, maintaining zero dependencies on other Gyomu packages to keep inter-package relationships loosely coupled. All canonical data schemas governing data contracts across features like Python Analysis, Concept, Document, Knowledge, and Snapshot must be defined as Pydantic schemas, particularly when handling data at external boundaries such as JSON, persistence layers, and MCP. Implementation details restricted to internal processing should not be exposed as Pydantic schemas. To prevent value confusion and enforce type safety, contributors should use types to represent IDs, paths, and meaningful values wherever possible. Furthermore, Pydantic schema annotations must never be omitted, as they serve a critical role beyond runtime type information by supporting AI code generation, document generation, and knowledge generation.

Architectural boundaries require that Protocols define exclusively shared interface contracts without any concrete implementations, while utilities must remain generic and strictly devoid of specific Gyomu business logic. Error handling must adhere to standardized error structures to guarantee consistent error processing across application layers, and all APIs must be designed to be as immutable and declarative as possible. When evolving the codebase, contributors are expected to uphold these concrete design decisions and constraints to preserve data consistency, type safety, and architectural integrity across the entire Gyomu ecosystem.

## Public API

- Python Code Analysis Schemas - Comprehensive data models for representing Python code structures, AST expressions, statements, types, and module analyses.
- Document and Translation Schemas - Schemas, validation rules, and translation strategies for structured documents, sections, and content elements.
- Error Handling and Recovery Schemas - Core domain-specific error handling classes, resolution strategies, and retry policies for application operations.
- Knowledge Management Schemas - Schemas for representing developer-oriented operational knowledge, coding guidelines, roadmaps, and technical references.
- Utility and Serialization Framework - Serialization, validation, execution timing, and asynchronous/synchronous outcome utilities.

## License

MIT