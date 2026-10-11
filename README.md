# Gyomu

US English | [JP 日本語](README.ja.md)

> **Stop maintaining docs & tests manually. Own your AI coding harness with Python.**

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Gyomu** is a repository-centric, open AI agent system that automates and maintains **Python docstring generation, directory/package-level design concept extraction, and multilingual README creation**.

Gyomu also generates and maintains LLM Context documents that capture architectural knowledge, design principles, editing rules, and important project constraints.

In the future, Gyomu aims to extend its capabilities to automatically update and maintain related development assets alongside code changes, including test code synchronization and correction.

Instead of locking your agent's feedback loops inside black-box AI provider platforms, Gyomu keeps your context, evaluation, and knowledge right inside your repository as human-readable artifacts, including YAML knowledge files, Python docstrings, and tests.

This project is organized as a monorepo.

**Documentation for packages outside the root package, including Python docstrings and README.md files, is automatically generated and maintained by Gyomu.**

---

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) for dependency management
- An AI provider API key for LLM-powered generation

Gyomu is designed to minimize development costs and support workflows that can operate within free-tier AI service limits, depending on the selected provider, model, and usage.

---

## ⚡ Demos

### 1. Multi-language README Generation

Generates and maintains multilingual READMEs based on your codebase structure, extracted package concepts, and lightweight YAML knowledge files.

![Multi-language README Generation Demo](docs/assets/readme-generation-demo.gif)

### 2. Automated Docstring & Context Extraction

Analyzes Python code and generates docstrings, directory/package-level design concepts, and LLM Context documents to keep documentation aligned with the implementation.

![Docstring Generation Demo](docs/assets/tsdoc-generation-demo.gif)

---

## 💡 Why This Project?

### 1. Escape the "Docs & Tests Maintenance Hell"

High-quality AI-assisted coding requires up-to-date docstrings, architectural context, and robust test suites. However, manually maintaining them is one of the most tedious and time-consuming tasks for developers.

By delegating documentation generation and maintenance to an agent, **developers can focus more of their energy on creative coding and system design**.

Gyomu's long-term goal is to extend this approach to development assets such as tests, helping keep implementation and verification in sync.

### 2. Platform-Agnostic "Open Harness"

AI coding tools increasingly provide their own integrated feedback loops for planning, testing, and fixing code.

Gyomu takes a repository-centric approach: your rules, domain concepts, architectural knowledge, and development context remain in your repository as inspectable artifacts.

This keeps your project knowledge under your control and helps reduce dependence on any single AI provider.

### 3. Built with Python's Type System and Explicit Dependencies

Gyomu uses Python's type system, strict static type checking, and explicit dependency injection to make its workflows easier to understand, test, and maintain.

Its AI infrastructure supports retry policies, model routing, and fallback mechanisms. Pydantic provides schema validation at data boundaries, while `returns` provides explicit `Result`, `Success`, and `Failure` values for error handling.

The result is a modular agent system designed for predictable workflows and maintainable code.

---

## 🛠 Tech Stack

- **Language:** Python 3.13+
- **Package & Environment Management:** [uv](https://docs.astral.sh/uv/)
- **Data Validation:** [Pydantic](https://docs.pydantic.dev/)
- **Explicit Error Handling:** [returns](https://returns.readthedocs.io/)
- **Static Type Checking:** [mypy](https://mypy.readthedocs.io/)
- **Linting:** [Ruff](https://docs.astral.sh/ruff/)
- **Testing:** [pytest](https://docs.pytest.org/)
- **AI Integration:** Pydantic AI and supported LLM providers
- **Configuration & Knowledge:** YAML, Python docstrings, and repository structure

---

## 🤝 Looking for Collaborators!

We welcome contributors who share this vision:

- 💡 **Python Architecture Enthusiasts:** Help us build maintainable, strictly typed AI agent workflows.
- 🧪 **Test & Context Pioneers:** Help us develop intelligent workflows that keep code, documentation, and tests in sync.
- 🌐 **Prompt & i18n Engineers:** Improve multilingual generation prompts, knowledge schemas, and documentation quality.

### How to Join

- Join the conversation in [GitHub Discussions](https://github.com/Yoshihisa-Matsumoto/Gyomu_Python/discussions).
- Check out [Good First Issues](https://github.com/Yoshihisa-Matsumoto/Gyomu_Python/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) to start contributing.

---

## 📖 Quick Start

```bash
# Clone the repository
git clone https://github.com/Yoshihisa-Matsumoto/Gyomu_Python.git
cd gyomu_python

# Install dependencies
uv sync

# Run the CLI
uv run gyomu --help
```

See the CLI help for available commands and options.

---

## 📜 License

MIT
