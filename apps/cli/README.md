# Gyomu CLI

US English | [JP 日本語](README.ja.md)

## Overview

This package serves as the primary command-line interface for the application, built using Typer. Its mission is to provide an execution interface that allows users to access system functions directly from the terminal. 

By receiving user commands, arguments, and options, it constructs the necessary input data to invoke underlying application functions like workflows. This design effectively separates command-line-specific input handling from core processing logic. 

Ultimately, it ensures that all features remain accessible through a consistent, unified interface by coordinating execution and integrating essential configuration settings.

## Architecture

The gyomu-cli package is structured around a Typer-based command-line interface that serves as the primary application entry point and orchestrates user commands. Responsibilities are divided into distinct capabilities covering top-level command routing, code snapshot execution workflows, and service integration. 

The core logic resides within the `src/gyomu_cli` directory, which unifies these collaborating components. The package coordinates execution flow by processing code snapshot requests while simultaneously initializing and registering configuration settings for AI and Google routing services. Through this organization, the command-line interface successfully bridges user input with core domain and infrastructure packages to manage execution and integration seamlessly.

## Installation

Install using uv.

```bash
uv add gyomu-cli
```

## Dependencies

This package relies on pydantic for schema definition, data validation, and serialization. For core operations, it requires gyomu-schema for shared types, gyomu-infra for I/O and infrastructure processing, and gyomu-workflow for snapshot-related tasks. Additionally, gyomu-ai is used for LLM initialization and routing table construction, while gyomu-ai-compiler is required to retrieve routing table IDs.

## Development

Contributors must strictly maintain a clean separation between command-line input handling and application business logic. The CLI interface is restricted to receiving and interpreting commands, arguments, and options, performing input validation at the boundary, and constructing type-safe inputs. Contributors are prohibited from implementing individual application processing logic, workflow control, or execution routing within the CLI layer. All workflow orchestration, execution targets, execution options, and AI model configurations—including selection, execution, retry, and routing mechanisms—must be delegated entirely to designated lower-level packages through defined public interfaces, avoiding any direct dependency on internal implementations.

Dependency management must adhere to the Composition Root pattern, ensuring that necessary dependencies are explicitly constructed and passed via mechanisms such as constructor injection. Contributors must ensure that execution options and targets are treated explicitly to prevent implicit configurations or unpredictable behaviors. Furthermore, command-line arguments and options must be designed with intuitive, consistent naming conventions and predictable behaviors, while processing results and errors must be clearly distinguished to present necessary information to users and return appropriate exit statuses without leaking CLI-specific concerns into underlying packages.

## Public API

- Command-Line Interface - Defines the command-line interface entry points and top-level command routing for the application.
- Snapshot Execution - Handles code snapshot execution and processing workflows.
- AI and Routing Configuration - Configures integration with Google routing and AI-related services.

## License

MIT