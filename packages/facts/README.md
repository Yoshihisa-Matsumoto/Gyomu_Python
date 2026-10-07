# Gyomu Facts

US English | [JP 日本語](README.ja.md)

## Overview

The gyomu-facts package provides a foundational infrastructure for structuring, retrieving, and referencing project facts in a type-safe and consistent manner. Its primary purpose is to enable applications to understand development contexts by modeling project structures, configurations, and related facts through a shared framework. 

By separating fact definitions and retrieval logic from consuming code, the package shields users from underlying changes in data sources. It delivers core analysis and directory ranking capabilities that compile package facts and compute importance scores, ultimately supporting automated architectural assessment and reusable development context management.

## Architecture

The gyomu-facts package is structured around two primary architectural capabilities: package analysis and directory ranking. Responsibilities are divided cleanly to separate the compilation of structural package metadata from the evaluation and scoring processes. At the organizational level, the codebase utilizes a centralized module structure rooted in `src/gyomu_facts`, with specialized logic isolated within the `src/gyomu_facts/package` directory. These components collaborate directly to support automated architectural assessments. Specifically, the core package analysis routines consume directory selection options alongside score calculations to evaluate and rank directories based on defined importance criteria.

## Installation

Install using uv.

```bash
uv add gyomu-facts
```

## Dependencies

This package relies on several runtime dependencies to function. It uses the `returns` library for explicit success and failure expression through Success, Failure, and Result. Additionally, it integrates `gyomu-schema` for schemas and common types, `gyomu-infra` for general infrastructure processing such as I/O, and `gyomu-python-analysis` for Python analysis tasks.

## Development

Contributors must maintain a strict separation between Fact definitions and their retrieval mechanisms to ensure that consumers remain isolated from implementation details. The architecture relies on dependency injection for Fact retrieval processes, preventing consumers from depending directly on concrete implementations. Furthermore, the model must be designed so that introducing new types of Facts does not require unnecessary modifications from existing Fact consumers, preserving extensibility as the package evolves.

All Fact models must be defined declaratively and in a strictly type-safe manner, avoiding any implicit type conversions on the consumer side. Related Facts should be grouped into type-safe collections to allow consistent handling across the application. Contributors must ensure that Fact implementations strictly represent facts obtainable from source code or project settings, leaving any analysis, judgment, or derived processing entirely outside the scope of the Fact definitions and retrieval layer.

## Public API

- Package Analysis - Analyze package structures and compile comprehensive package metadata and facts.
- Directory Ranking - Calculate scores and rank directories using configurable selection criteria.

## License

MIT