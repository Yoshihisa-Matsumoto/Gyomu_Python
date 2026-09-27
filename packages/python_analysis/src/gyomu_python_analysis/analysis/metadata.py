from gyomu_schema.schemas.python.class_analysis import ClassAnalysis, InnerClassAnalysis
from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.file_analysis import FileAnalysisMetadata
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.symbol import MemberAnalysis, SymbolAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity


def create_file_analysis_metadata(
    module_analysis: ModuleAnalysis,
) -> FileAnalysisMetadata:
    """Create file analysis metadata from a module analysis.

    Creates file analysis metadata from a module analysis result.

    Args:
        module_analysis (ModuleAnalysis): The module analysis result to process.

    Returns:
        FileAnalysisMetadata: The created file analysis metadata containing parsed
            docstrings and symbols.
    """
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
    """Register class metadata into the symbol and docstring dictionaries.

    Registers class metadata, including inner classes, methods, variables, and type
    aliases, into the symbol and docstring dictionaries.

    Args:
        cls (ClassAnalysis | InnerClassAnalysis): The class or inner class analysis to
            register.
        symbols (dict[DeclarationIdentity, SymbolAnalysis | MemberAnalysis]): Dictionary
            mapping declaration identities to symbols or member analyses.
        parsed_docstring (dict[DeclarationIdentity, DocstringAnalysis]): Dictionary
            mapping declaration identities to docstring analyses.

    Returns:
        None: None
    """
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
