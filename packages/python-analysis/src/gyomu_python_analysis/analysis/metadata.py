from gyomu_schema.schemas.python.class_analysis import ClassAnalysis, InnerClassAnalysis
from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.file_analysis import FileAnalysisMetadata
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.symbol import MemberAnalysis, SymbolAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity


def create_file_analysis_metadata(
    module_analysis: ModuleAnalysis,
) -> FileAnalysisMetadata:
    parsed_docstring: dict[DeclarationIdentity, DocstringAnalysis] = {}
    symbols: dict[DeclarationIdentity, SymbolAnalysis | MemberAnalysis] = {}

    for symbol in module_analysis.symbols:
        symbols[symbol.identity] = symbol
        if symbol.docstring is not None:
            parsed_docstring[symbol.identity] = symbol.docstring

        if isinstance(symbol, ClassAnalysis):
            register_class_metadata(symbol, symbols, parsed_docstring)
    return FileAnalysisMetadata(parsed_docstring, symbols)


def register_class_metadata(
    cls: ClassAnalysis | InnerClassAnalysis,
    symbols: dict[DeclarationIdentity, SymbolAnalysis | MemberAnalysis],
    parsed_docstring: dict[DeclarationIdentity, DocstringAnalysis],
) -> None:
    for inner in cls.inner_classes:
        symbols[inner.identity] = inner
        if inner.docstring is not None:
            parsed_docstring[inner.identity] = inner.docstring
        register_class_metadata(inner, symbols, parsed_docstring)

    for method in cls.methods:
        symbols[method.identity] = method
        if method.docstring is not None:
            parsed_docstring[method.identity] = method.docstring

    for variable in cls.variables:
        symbols[variable.identity] = variable
        if variable.docstring is not None:
            parsed_docstring[variable.identity] = variable.docstring

    for alias in cls.type_aliases:
        symbols[alias.identity] = alias
        if alias.docstring is not None:
            parsed_docstring[alias.identity] = alias.docstring
