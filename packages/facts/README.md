# Gyomu Facts

US English | [JP 日本語](README.ja.md)

## Overview

The package structures project facts and configuration data, providing a type-safe and consistent foundation to retrieve and reference development context across upper-layer processes. 

It supplies core analysis capabilities to compile package information alongside directory ranking mechanisms to evaluate codebase importance. By treating structural details as uniform facts, it enables systems to consistently utilize project context and assess directory relevance.

## Architecture

The gyomu-facts package is organized around a core analytical structure designed to evaluate software projects. Responsibilities are divided into components that handle package analysis, directory ranking, and targeted selection. The package roots coordinate the primary analysis routines and compile comprehensive factual summaries representing package structures.

Within this structure, specialized modules implement scoring and ranking algorithms. These components evaluate directories based on structural importance and feed score calculations directly into the broader package analysis routines. Simultaneously, flexible selection options filter and target specific areas of the codebase, working collaboratively with the ranking logic to assess codebase importance.

## Installation

Install using uv.

```bash
uv add gyomu-facts
```

## Dependencies

This package relies on several runtime dependencies to function. The `returns` package is used for explicit success and failure expression using Success, Failure, and Result. Additionally, `gyomu-schema` serves as a storage location for schemas and common types, `gyomu-infra` handles general foundational processes such as I/O, and `gyomu-python-analysis` is utilized for Python analysis.

## Development

To achieve the core objective of providing a type-safe and consistent foundation for project and package facts, contributors must strictly decouple fact definitions from their retrieval mechanisms. Fact models must be defined declaratively and with strict type safety, avoiding any implicit type conversions on the consumer side. By separating how facts are defined from how they are fetched, the architecture ensures that consuming code never depends on the implementation details of data retrieval. Furthermore, new kinds of facts must be designed to integrate seamlessly without requiring unnecessary modifications to existing fact consumers, and related facts must be grouped into type-safe collections to maintain uniform access patterns.

The internal architecture enforces a clear boundary between the structural analysis of source code and configuration data, and the subsequent evaluation processes. Specifically, Package Analysis is strictly responsible for structuring verifiable facts from project sources, while Directory Ranking handles the evaluation of directory importance based explicitly on defined scoring criteria. Contributors must maintain this separation of concerns, ensuring that the acquisition of facts remains entirely isolated from the higher-level analytical and decision-making logic that consumes them.

## Public API

- Package Analysis - Compile comprehensive factual summaries and data models representing package structures.
- Directory Ranking - Evaluate and score directories based on structural importance and configurable criteria.
- Directory Selection - Configure flexible strategies for filtering and selecting relevant target directories.

## License

MIT