from gyomu_facts.package.analysis import PackageFacts, TopScoreDirectorySelection
from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis

from gyomu_ai_compiler.pipelines.package_concept.context.input import (
    PackageConceptInput,
    PackageDependencyInput,
    PublicApiSymbol,
    PublicSymbolsModule,
    TopDirectory,
)


def build_package_concept_input(context: PackageAnalysis) -> PackageConceptInput:
    """Build package concept input data for rendering.

    Builds the package concept input from the given package analysis context.

    Args:
        context (PackageAnalysis): The package analysis context containing package
            information, public files, and dependencies.

    Returns:
        PackageConceptInput: The constructed package concept input structure.
    """
    symbols: dict[str, list[PublicApiSymbol]] = {}
    for file in context.public_files:
        for declaration in file.exports:
            module, _, name = declaration.symbol.rpartition(".")
            # module = declaration.symbol  # split in last "." and first part
            # name = declaration.symbol  # split in last "." and last part
            summary = declaration.summary

            if module not in symbols:
                symbols[module] = []
            symbols[module].append(PublicApiSymbol(name=name, summary=summary))

    public_symbols: list[PublicSymbolsModule] = []

    for module in symbols:
        public_symbols.append(
            PublicSymbolsModule(module=module, symbols=tuple(symbols[module]))
        )

    top_directories: list[TopDirectory] = []
    for directory in PackageFacts(context).get_ranked_directories(
        TopScoreDirectorySelection(limit=5)
    ):
        top_directories.append(
            TopDirectory(
                path=directory.path,
                importance=directory.concept.importance,
                responsibilities=tuple(directory.concept.responsibilities),
                summary=directory.concept.summary,
            )
        )
    return PackageConceptInput(
        package=context.package,
        dependencies=tuple(
            [
                PackageDependencyInput(
                    package_name=item.package_name, version=item.required_version or ""
                )
                for item in context.dependencies
                if item.source == "dependency"
            ]
        ),
        public_symbols=tuple(public_symbols),
        top_directories=tuple(top_directories),
    )
