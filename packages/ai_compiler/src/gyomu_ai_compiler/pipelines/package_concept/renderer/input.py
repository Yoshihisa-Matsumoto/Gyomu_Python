from gyomu_ai_compiler.pipelines.package_concept.context.input import (
    PackageConceptInput,
    PackageDependencyInput,
    PublicApiSymbol,
    PublicSymbolsModule,
    TopDirectory,
)
from gyomu_facts.package.analysis import PackageFacts, TopScoreDirectorySelection
from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis


def build_package_concept_input(context: PackageAnalysis) -> PackageConceptInput:
    symbols: dict[str, list[PublicApiSymbol]] = {}
    for item in context.public_files:
        for declaration in item.exports:
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
    for item in PackageFacts(context).get_ranked_directories(
        TopScoreDirectorySelection(limit=5)
    ):
        top_directories.append(
            TopDirectory(
                path=item.path,
                importance=item.concept.importance,
                responsibilities=tuple(item.concept.responsibilities),
                summary=item.concept.summary,
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
