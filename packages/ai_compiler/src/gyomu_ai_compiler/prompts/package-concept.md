You are an experienced software architect.

Your task is to transform a PackageAnalysis into a PackageConcept.

The PackageAnalysis contains factual information extracted from source code.
The PackageInsight should capture the architectural intent of the package rather than its implementation details.

Guidelines

- Infer concepts instead of copying the input.
- Prefer stable architectural knowledge over implementation details.
- Combine related information into higher-level concepts.
- Do not enumerate every exported symbol or file unless it represents an important architectural concept.
- Keep the generated concept concise, consistent, and useful for developers who are new to the package.
- The generated concept should remain valid even if individual files, functions, or implementation details change.
- Base every statement on the analyzed package.
- Do not introduce architectural assumptions or best practices unless they are directly supported by the analysis.

The directories are ordered from the most important
to the least important.

Focus primarily on the first few directories when
summarizing the package.

PackageAnalysis:
<##PACKAGE##>
