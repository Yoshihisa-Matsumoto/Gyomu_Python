Generate the "Editing Rules" section for an LLM Context document.

# Goal

Generate concise rules that guide an AI when modifying this package.

The rules should describe how changes should be implemented, validated, tested, and integrated into the existing codebase.

# Input

The input contains coding guidelines defined at both the repository level and the package level.

Repository-level rules describe conventions that apply across the entire repository.

Package-level rules extend or specialize those conventions for this package.

# Instructions

- Merge repository-level and package-level rules into a single coherent list.
- Remove duplicate or equivalent rules.
- Preserve package-specific rules even when they are more restrictive.
- Rewrite rules as concise, imperative instructions.
- Prefer actionable instructions beginning with verbs such as:
  - Use
  - Keep
  - Avoid
  - Validate
  - Depend on
  - Generate
  - Update
  - Preserve
  - Test
  - Do not
  - Never
- Keep each rule to a single sentence.
- Focus on implementation, testing, dependencies, schemas, error handling, APIs, documentation, and AI integration.
- Include a rule only when it can directly guide a code change.
- Prefer existing project patterns over introducing new abstractions or conventions.
- Preserve existing public APIs and architectural boundaries unless the input explicitly requires changing them.
- Require tests when a change affects observable behavior.
- Do not explain the rationale.
- Do not repeat the input verbatim.
- Do not duplicate constraints that belong in Important Constraints.
- Do not invent new rules or project conventions.

# Output

Return only a Bullet List.

Keep the list concise.

Example:

- Use Effect Schema for persisted and externally exchanged data.
- Depend only on public APIs of other packages.
- Validate AI-generated data with Effect Schema before use.
- Represent effectful operations with Effect.
- Update tests when observable behavior changes.
- Preserve existing barrel-file export patterns.
