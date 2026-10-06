You are analyzing a Python source directory.

Your task is to infer the architectural purpose of this directory from the provided file summaries and child directory concepts.

Generate a DirectoryConcept object.
A DirectoryConcept describes why these files and child directories belong together as a group, not what each individual file does.
Focus on the common purpose of the directory as a cohesive unit.

Guidelines

- Think at the directory level rather than the individual file level.
- Identify the shared responsibility across files and child directories.
- Merge similar ideas instead of repeating them.
- Do not mention filenames.

Evidence and inference

- Only describe information that can be reasonably inferred from the provided file summaries and child directory concepts.
- When an interpretation is uncertain or weakly supported, omit it rather than guessing.
- Do not introduce architectural patterns, domain concepts, consumers, or application structure unless they are explicitly evidenced.
- Do not infer a dependency or relationship between child directories merely because one child directory's concept says that it provides something "used by", "shared by", or "available to" other components.
- A relationship between directories may only be described when the provided file summaries explicitly contain dependency information supporting that relationship.
- Do not reverse the direction of a dependency. If A depends on B, describe A → B, not B → A.
- Do not treat a child directory's `relationships` as evidence that another child directory depends on it unless that dependency is explicitly supported by file dependencies.
- If no explicit dependency evidence exists, omit the relationship rather than guessing.

Concepts and terminology

- Concepts should be concise noun phrases (1–4 words).
- Prefer concrete responsibilities and terminology over abstract software architecture language.
- Reuse terminology from the provided summaries whenever possible.

Directory contents


Files:
<##FILES##>

Child directories:
<##DIRECTORIES##>
