from dataclasses import dataclass
from pathlib import Path

from griffe import Attribute, Class, Function, TypeAlias
from gyomu_docstring.update.docstring.file_update_plan import FileUpdatePlanEntry
from gyomu_docstring.update.docstring.rendered_symbol import (
    RenderedSymbolDocstring,
)
from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.analyzers.cls import analyze_class
from gyomu_python_analysis.analysis.analyzers.context import initialize_symbol_context
from gyomu_python_analysis.analysis.analyzers.functions import analyze_function
from gyomu_python_analysis.analysis.analyzers.type_alias import analyze_type_alias
from gyomu_python_analysis.analysis.analyzers.variables import analyze_variable
from gyomu_python_analysis.analysis.file.source_file_context import SourceFileContext
from gyomu_python_analysis.analysis.load import load_module
from gyomu_python_analysis.analysis.load_module import load_module_analysis
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.file_analysis import (
    FileAnalysisContext,
    FileAnalysisMetadata,
)
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.method_analysis import MethodAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.symbol import MemberAnalysis, SymbolAnalysis
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    ProjectRelativePath,
    PythonPath,
    SourceRelativePath,
    SymbolId,
)
from gyomu_schema.schemas.python.variable import VariableAnalysis
from gyomu_schema.schemas.python.visibility import Visibility
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure

FIXTURES_ROOT = FullPath(Path(__file__).parent / "fixtures")

print("LOADED DOCSTRING TESTS.HELPERS")


def _create_context() -> ProjectContext:
    return ProjectContext(
        project_root=FIXTURES_ROOT,
        source_root=ProjectRelativePath(Path("src")),
    )


def create_declaration_identity(id: str) -> DeclarationIdentity:
    return DeclarationIdentity(
        symbol_id=SymbolId(id),
        declaration_id=DeclarationId("."),
    )


def create_location(
    start_offset: int = 0,
    end_offset: int = 0,
    start_line: int = 1,
    start_column: int = 0,
    end_line: int = 1,
    end_column: int = 0,
) -> SourceLocation:
    return SourceLocation(
        start_line=start_line,
        start_offset=start_offset,
        end_line=end_line,
        end_offset=end_offset,
        start_column=start_column,
        end_column=end_column,
    )


_default_identity = DeclarationIdentity(
    symbol_id=SymbolId("test.User"),
    declaration_id=DeclarationId("."),
)


def create_entry(
    start_offset: int = 0,
    end_offset: int = 0,
    identity: DeclarationIdentity = _default_identity,
    new_text: str = "",
) -> FileUpdatePlanEntry:

    return FileUpdatePlanEntry(
        identity=identity,
        location=create_location(start_offset=start_offset, end_offset=end_offset),
        new_text=new_text,
    )


def create_rendered_docstring(
    docstring: str | None,
    start_offset: int = 0,
    end_offset: int = 0,
    identity: DeclarationIdentity = _default_identity,
) -> RenderedSymbolDocstring:
    return RenderedSymbolDocstring(
        identity=identity,
        docstring=docstring,
        location=create_location(start_offset=start_offset, end_offset=end_offset),
    )


def create_type_alias_analysis(
    indent: int,
    location: SourceLocation,
    name: str = "test_func",
    identity: DeclarationIdentity | None = None,
) -> TypeAliasAnalysis:
    if identity is None:
        identity = create_declaration_identity(name)
    return TypeAliasAnalysis(
        name=name,
        docstring=None,
        identity=identity,
        decorators=tuple(),
        dependencies=tuple(),
        indent=indent,
        kind=DeclarationKind.TYPEALIAS,
        visibility=Visibility.PUBLIC,
        location=location,
        alias_type=None,
    )


def create_variable_analysis(
    indent: int,
    location: SourceLocation,
    name: str = "test_func",
    identity: DeclarationIdentity | None = None,
) -> VariableAnalysis:
    if identity is None:
        identity = create_declaration_identity(name)
    return VariableAnalysis(
        name=name,
        docstring=None,
        identity=identity,
        decorators=tuple(),
        dependencies=tuple(),
        indent=indent,
        kind=DeclarationKind.VARIABLE,
        visibility=Visibility.PUBLIC,
        location=location,
        type=None,
        value_source=None,
    )


def create_function_analysis(
    indent: int,
    location: SourceLocation,
    name: str = "test_func",
    identity: DeclarationIdentity | None = None,
) -> FunctionAnalysis:
    if identity is None:
        identity = create_declaration_identity(name)
    return FunctionAnalysis(
        name=name,
        docstring=None,
        identity=identity,
        decorators=tuple(),
        dependencies=tuple(),
        indent=indent,
        is_async=False,
        kind=DeclarationKind.FUNCTION,
        parameters=tuple(),
        return_type=None,
        visibility=Visibility.PUBLIC,
        location=location,
    )


def create_method_analysis(
    indent: int | None,
    location: SourceLocation | None,
    name: str = "test_func",
    identity: DeclarationIdentity | None = None,
) -> MethodAnalysis:
    if identity is None:
        identity = create_declaration_identity(name)
    return MethodAnalysis(
        name=name,
        docstring=None,
        identity=identity,
        decorators=tuple(),
        indent=indent,
        is_async=False,
        kind=DeclarationKind.METHOD,
        parameters=tuple(),
        return_type=None,
        visibility=Visibility.PUBLIC,
        location=location,
    )


def create_class_analysis(
    indent: int,
    location: SourceLocation,
    name: str = "test_class",
    identity: DeclarationIdentity | None = None,
) -> ClassAnalysis:
    if identity is None:
        identity = create_declaration_identity(name)
    return ClassAnalysis(
        name=name,
        docstring=None,
        identity=identity,
        decorators=tuple(),
        dependencies=tuple(),
        indent=indent,
        kind=DeclarationKind.CLASS,
        bases=tuple(),
        visibility=Visibility.PUBLIC,
        location=location,
        methods=tuple(),
        variables=tuple(),
        type_aliases=tuple(),
        inner_classes=tuple(),
    )


def create_file_analysis_context(
    symbol: SymbolAnalysis | MemberAnalysis | None = None,
    symbol2: SymbolAnalysis | MemberAnalysis | None = None,
    symbol3: SymbolAnalysis | MemberAnalysis | None = None,
) -> FileAnalysisContext:
    symbols: dict[DeclarationIdentity, SymbolAnalysis | MemberAnalysis]
    symbols = dict([(symbol.identity, symbol)]) if symbol else dict()

    if symbol2:
        symbols[symbol2.identity] = symbol2
    if symbol3:
        symbols[symbol3.identity] = symbol3
    return FileAnalysisContext(
        metadata=FileAnalysisMetadata(parsed_docstring=dict(), symbols=symbols),
        analysis=ModuleAnalysis(
            path=SourceRelativePath(Path(".")),
            name="test",
            module_name=PythonPath(""),
            docstring=None,
            imports=tuple(),
            symbols=(),
        ),
    )


@dataclass
class BaseContext:
    project: ProjectContext
    source: SourceFileContext


class AnalysisTestBase:
    def _analyze_module_base(self, file_name: PythonPath) -> ModuleAnalysis:
        context = self._read_module_fixture(file_name)
        result = load_module_analysis(context.project, file_name)
        if isinstance(result, Failure):
            raise result.failure()

        return result.unwrap()

    def _analyze_typealias_bases(
        self, file_name: PythonPath, symbol_name: str, dump_required: bool = False
    ) -> TypeAliasAnalysis:
        symbol, source_lines = self._analyze_symbol(
            file_name, symbol_name, dump_required
        )
        assert isinstance(symbol, TypeAlias)
        return analyze_type_alias(
            alias=symbol,
            name=symbol_name,
            context=initialize_symbol_context(
                module_name=file_name, name=symbol_name, source_lines=source_lines
            ),
        )

    def _analyze_function_base(
        self, file_name: PythonPath, symbol_name: str, dump_required: bool = False
    ) -> FunctionAnalysis:
        symbol, source_lines = self._analyze_symbol(
            file_name, symbol_name, dump_required
        )
        assert isinstance(symbol, Function)
        return analyze_function(
            func=symbol,
            name=symbol_name,
            context=initialize_symbol_context(
                module_name=file_name, name=symbol_name, source_lines=source_lines
            ),
        )

    def _analyze_variable_base(
        self, file_name: PythonPath, symbol_name: str, dump_required: bool = False
    ) -> VariableAnalysis:
        symbol, source_lines = self._analyze_symbol(
            file_name, symbol_name, dump_required
        )
        assert isinstance(symbol, Attribute)
        return analyze_variable(
            variable=symbol,
            name=symbol_name,
            context=initialize_symbol_context(
                module_name=file_name, name=symbol_name, source_lines=source_lines
            ),
        )

    def _analyze_class_base(
        self, file_name: PythonPath, symbol_name: str, dump_required: bool = False
    ) -> ClassAnalysis:
        symbol, source_lines = self._analyze_symbol(
            file_name, symbol_name, dump_required
        )
        assert isinstance(symbol, Class)
        return analyze_class(
            cls=symbol,
            name=symbol_name,
            context=initialize_symbol_context(
                module_name=file_name, name=symbol_name, source_lines=source_lines
            ),
        )

    def _analyze_symbol(
        self, file_name: PythonPath, symbol_name: str, dump_required: bool = False
    ) -> tuple[SymbolAnalysis, list[str]]:
        module_name = file_name
        context = self._read_module_fixture(module_name)
        module = context.source.module
        symbol = module[symbol_name]

        if dump_required:
            logger.info(symbol.as_dict())

        source_full_path = (
            context.project.project_root
            / context.project.source_root
            / context.source.path
        )
        source_lines = source_full_path.read_text(
            encoding="utf-8",
        ).splitlines(keepends=True)

        return symbol, source_lines

    def _read_module_fixture(self, module_path: PythonPath) -> BaseContext:
        context = _create_context()
        # search_path = context.project_root / context.source_root
        # print("search:", search_path)
        # print("modulePath:", modulePath)

        # loader = GriffeLoader(
        #     search_paths=[search_path],
        # )
        # module = loader.load(modulePath)
        # if isinstance(module, Module):
        #     print("location:", module.filepath)
        #     return module
        # raise ValueError("Invalid:")
        result = load_module(context, module_path)

        source_file_context = result.unwrap()

        return BaseContext(project=context, source=source_file_context)
