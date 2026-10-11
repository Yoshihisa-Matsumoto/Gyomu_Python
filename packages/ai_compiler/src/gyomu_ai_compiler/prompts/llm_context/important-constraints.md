Generate the "Important Constraints" section.

# Goal

Identify the architectural and technical boundaries that must be preserved when modifying this package.

The constraints should help an AI determine what changes are prohibited or require special care.

# Input

The input may contain:

- Human-defined constraints.
- Package architecture and responsibilities.
- Design principles.
- Repository-level constraints.
- Package-level constraints.

# Instructions

- Extract constraints that materially restrict how this package may be changed.
- Merge human-defined and strongly supported inferred constraints.
- Preserve package-specific constraints when they are more restrictive than repository-level constraints.
- Prefer concrete, testable, and actionable constraints.
- Express each constraint as a prohibition, requirement, or boundary.
- Focus on dependencies, public APIs, data models, side effects, I/O, architectural boundaries, compatibility, and other hard restrictions.
- Distinguish constraints from design preferences or implementation guidelines.
- Do not include rationale or explanations.
- Do not include general best practices unless explicitly supported by the input.
- Do not repeat equivalent constraints.
- Do not include instructions about how to implement a change; those belong in Editing Rules.
- Do not invent constraints that are not supported by the input.

# Output

Return only a Bullet List.

Keep the list concise.

Example:

- Do not depend on other `@gyomu` packages.
- Do not perform file system, network, or database I/O.
- Preserve the existing public export structure.
- Define persisted and externally exchanged data with Effect Schema.
- Do not introduce business logic into this package.
