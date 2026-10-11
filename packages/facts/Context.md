# Gyomu Facts

## Repository Overview

The `gyomu-facts` package serves as a foundational infrastructure for structuring, retrieving, and referencing facts related to Gyomu projects and packages in a type-safe and consistent manner. Its primary responsibility is to compile project and package information into unified facts, enabling higher-level processes to utilize a consistent development context. Additionally, it provides the structural foundation for performing package analysis to structure package facts and utilizing directory ranking to evaluate the relative importance of code repository directories.

## Package Responsibilities

- Provide core analysis capabilities to extract and compile package facts.
- Implement scoring and ranking algorithms to order project directories by importance.
- Offer configurable selection options for targeting specific package areas.

## Architecture

The package is structured around the `src/gyomu_facts` root directory, which houses the primary package analysis and directory ranking capabilities. 

Within this root, the `src/gyomu_facts/package` subdirectory serves as a specialized architectural area responsible for package facts compilation, directory selection options, and score calculations. Rank and score calculations defined in this component are directly utilized within the broader package analysis routines.

## Design Principles

- Represent project and package facts as declarative, type-safe models to ensure consistent data handling without implicit type conversions.
- Decouple fact definitions from their retrieval mechanisms to isolate consumers from implementation details and storage dependencies.
- Group related facts into type-safe collections to maintain structural stability and prevent consumer disruption when introducing new fact types.
- Separate foundational fact acquisition from higher-level analysis, ranking, and decision-making logic to enable the reuse of facts across multiple processing workflows.
- Enforce strict architectural boundaries by excluding state management, persistence, code modification, and AI-driven inference from fact acquisition processes.

## Important Constraints

- Do not allow consumers to directly implement individual Fact retrieval logic.
- Do not mix Fact definitions with analysis and decision-making logic that uses Facts.
- Do not grant responsibility for modifying source code or project settings.
- Do not implement application-specific decision logic that utilizes Facts.
- Do not incorporate AI-based analysis or inference into Fact retrieval processing.
- Do not handle Fact visualization or document generation.
- Do not allow consumers to directly depend on Fact persistence methods or storage implementations.
- Do not directly depend on specific AI providers or models.
- Do not incorporate state management processes such as Snapshots or Change Detection into Fact retrieval processing.

## Editing Rules

- Explicitly specify argument and return types for public APIs and primary application logic.
- Maintain type-safe implementations compatible with strict mypy settings.
- Avoid Any and suppressions for type checking unless scopes and reasons are strictly limited.
- Define and validate structured data at external boundaries using explicit schemas such as Pydantic models.
- Use appropriate data structures like dataclasses for internal state representation.
- Avoid duplicating data structures or constraints for the same concept across multiple locations.
- Express expected application failures explicitly using returns.Result, Success, and Failure.
- Handle exceptions appropriately at boundaries rather than using them to communicate expected failures.
- Keep package responsibilities clear and direct dependencies from upper workflows to lower functions.
- Do not introduce circular dependencies between packages.
- Interact with other packages exclusively through their public APIs rather than internal implementation details.
- Use Protocols and constructor injection to specify contracts for external dependencies and interchangeable logic.
- Design based on current responsibilities and changes rather than speculative future abstractions.
- Implement side-effect-free logic as pure functions whenever possible.
- Separate I/O operations involving the file system, external services, or LLMs from business logic.
- Validate AI outputs with schemas before use.
- Encapsulate AI provider-specific APIs and types behind appropriate adapters and infrastructure boundaries.
- Design interfaces that separate AI execution, routing, fallback, and retry from callers.
- Use structured data such as concepts and analysis results as inputs for document generation.
- Keep document composition, content, translation, and rendering as independent responsibilities.
- Use structured intermediate representations like Document rather than building Markdown strings directly.
- Treat concepts derived from source code and human-managed knowledge as independent information sources.
- Update tests when observable behavior changes.
- Keep unit tests deterministic by isolating dependencies on LLMs and external services.
- Use temporary directories and fixtures for file system tests while mocking only external service dependencies.
- Mock dependencies based on public interfaces without depending excessively on internal implementation details.
- Consolidate shareable logic into existing packages without duplicating implementations.
- Evaluate standard libraries and existing dependencies before adding new packages.
- Follow existing naming conventions, package structures, and code styles while keeping change scopes minimal.
- Pass all repository checks and tests including ruff, mypy, and pytest.

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
