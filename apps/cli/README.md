# Gyomu CLI

US English | [JP 日本語](README.ja.md)

## Overview

The package serves as the primary command-line interface entry point for the Gyomu suite. Its mission is to provide an execution interface that accepts user commands, arguments, and options, building the necessary input information to invoke core application functions such as workflows. 

By separating command-line input processing from application logic, the package ensures that Gyomu's features are accessible through a consistent interface. It coordinates interactions across various internal domain packages, exposing user-facing capabilities smoothly and effectively.

## Architecture

The gyomu-cli package is structured around a central command-line interface entry point that coordinates user interactions for the Gyomu suite. Built using Typer, the package exposes user-facing commands such as greetings, Google routing configuration, AI settings, and code snapshots. Responsibility is divided between interface management and system integration. The core source directory houses the primary application instance, which wires together command-line execution flows with underlying workspace systems. Rather than containing domain logic itself, the package acts as a bridge, delegating commands to internal gyomu domain components—including schema definitions, infrastructure services, AI models, compilers, and workflow automation services—to execute complex operations seamlessly.

## Installation

Install using uv.

```bash
uv add gyomu-cli
```

## Dependencies

This package relies on several runtime dependencies to function. It uses pydantic for schema definition, data validation, and serialization or deserialization. gyomu-schema serves as a repository for schemas and common types, while gyomu-infra handles general infrastructure processing such as I/O. Additionally, gyomu-ai is used for LLM initialization and routing table construction, gyomu-ai-compiler retrieves routing table IDs, and gyomu-workflow implements snapshot-related tasks.

## Development

Contributors must strictly separate command-line input handling from underlying domain logic. The package acts as the primary user-facing entry point and Composition Root, responsible exclusively for receiving commands, arguments, and options, performing input validation at the boundary, and constructing type-safe inputs. Contributors must never implement individual application processing, workflow control, or AI model selection, retry, and routing details within this package. Instead, all execution requests must be wired to underlying domain logic, AI configuration, and workflow services exclusively through defined public interfaces, ensuring that CLI-specific concerns never leak into lower packages.

All commands, arguments, and options must be designed for clarity and consistent behavior to avoid unpredictable operations and implicit settings. Contributors are required to handle execution targets and options explicitly, utilizing constructor injection and related patterns to pass necessary dependencies. Furthermore, contributors must ensure that the package properly distinguishes between processing results and errors, presenting required information to users while returning appropriate exit statuses without assuming responsibility for workflow sequencing or re-execution logic.

## Public API

- Command Line Interface - Provides command-line execution flows for interacting with core gyomu domain capabilities.
- System Integration - Integrates core workspace systems including schema definitions, infrastructure services, AI models, and workflow automation.

## License

MIT