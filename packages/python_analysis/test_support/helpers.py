import ast
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from griffe import Class, Function, TypeAlias
from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.analyzers.ast.symbol import (
    AstTargetSymbolType,
    get_ast_index,
)
from gyomu_python_analysis.analysis.analyzers.cls import analyze_class
from gyomu_python_analysis.analysis.analyzers.context import initialize_symbol_context
from gyomu_python_analysis.analysis.analyzers.functions import analyze_function
from gyomu_python_analysis.analysis.analyzers.type_alias import analyze_type_alias
from gyomu_python_analysis.analysis.extract.symbols import _extract_imports
from gyomu_python_analysis.analysis.file.source_file_context import SourceFileContext
from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.analysis.load import load_module
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.analysis.load_module import load_module_analysis
from gyomu_python_analysis.analysis.workspace import initialize_workspace_context
from gyomu_python_analysis.error.analysis import AnalysisError, AnalysisPhase
from gyomu_python_analysis.error.resolve import ResolveError
from gyomu_python_analysis.project.context import ProjectContext, PyProjectConfig
from gyomu_python_analysis.project.workspace import (
    WorkspaceProject,
    WorkspaceRoot,
    WorkspaceRootKind,
)
from gyomu_python_analysis.resolve.file_analysis_cache import FileAnalysisCache
from gyomu_python_analysis.resolve.type_dump import dump_type
from gyomu_python_analysis.snapshot.models import (
    AnalyzeProjectChangesResult,
)
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis
from gyomu_schema.schemas.python.types import (
    ProjectRelativePath,
    PythonPath,
    WorkspaceRelativePath,
)
from gyomu_schema.schemas.python.variable import VariableAnalysis
from gyomu_schema.schemas.snapshot.types import (
    FileAdded,
    FileChange,
    FileDeleted,
    FileSnapshot,
    FileUpdated,
    ProjectSnapshot,
)
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Success

from packages.schema.test_support.helpers import (
    build_declaration_identity,
)

TEST_SUPPORT_ROOT = FullPath(Path(__file__).parent)
FIXTURES_ROOT = FullPath(Path(__file__).parent / "fixtures")
MONOREPO_FIXTURES_ROOT = FullPath(Path(__file__).parent / "monorepo_fixtures")


_default_project_config = PyProjectConfig(
    path=WorkspaceRelativePath(Path(".")),
    name="test",
    version="0.1",
    description=None,
    formatter_line_length=88,
    _toml_data={},
)

_default_workspace_path = WorkspaceRelativePath(Path("."))


def create_py_project_config(
    path: WorkspaceRelativePath = WorkspaceRelativePath(Path(".")),  # noqa: B008
    name: str = "test",
    version: str = "1.0",
    description: str | None = "",
    formatter_line_length: int = 88,
    _toml_data: Mapping[str, Any] = {},
) -> PyProjectConfig:
    return PyProjectConfig(
        path=path,
        name=name,
        version=version,
        description=description,
        formatter_line_length=formatter_line_length,
        _toml_data=_toml_data,
    )


def create_workspace_project(
    path: WorkspaceRelativePath = _default_workspace_path,
    config: PyProjectConfig = create_py_project_config(),  # noqa: B008
) -> WorkspaceProject:
    return WorkspaceProject(path=path, config=config)


def _create_context() -> ProjectContext:
    return initialize_project_context(
        project_root=FIXTURES_ROOT, source_root=ProjectRelativePath(Path("src"))
    ).unwrap()


def create_monorepo_context() -> ProjectContext:
    return initialize_project_context(
        project_root=MONOREPO_FIXTURES_ROOT / "packages" / "project_a",
        source_root=ProjectRelativePath(Path("src")),
    ).unwrap()


def create_file_snapshot(
    project_relative_path: ProjectRelativePath,
    raw_hash: str = "ABCDE",
    modified_at: datetime = datetime.now(),  # noqa: B008
) -> FileSnapshot:
    return FileSnapshot(
        project_relative_path=project_relative_path,
        raw_hash=raw_hash,
        modified_at=modified_at,
    )


def create_file_added(current: FileSnapshot) -> FileAdded:
    return FileAdded(
        project_relative_path=current.project_relative_path, current=current
    )


def create_file_updated(current: FileSnapshot, previous: FileSnapshot) -> FileUpdated:
    return FileUpdated(
        project_relative_path=current.project_relative_path,
        current=current,
        previous=previous,
    )


def create_file_deleted(previous: FileSnapshot) -> FileDeleted:
    return FileDeleted(
        project_relative_path=previous.project_relative_path, previous=previous
    )


def create_project_snapshot(
    files: tuple[FileSnapshot, ...] = tuple(),
    project_root: WorkspaceRelativePath = WorkspaceRelativePath(  # noqa: B008
        Path("projects/project_a")
    ),
) -> ProjectSnapshot:
    return ProjectSnapshot(project_root=project_root, files=files)


def create_workspace_root(
    path: FullPath = FIXTURES_ROOT,
    kind: WorkspaceRootKind = WorkspaceRootKind.UV_WORKSPACE,
) -> WorkspaceRoot:
    return WorkspaceRoot(path=path, kind=kind)


def create_analyze_project_change(
    current_snapshot: ProjectSnapshot,
    project_id: str = "ABC",
    snapshot_path: FullPath = FullPath(Path("/tmp")),  # noqa: B008
    previous_snapshot: ProjectSnapshot | None = None,
    diff: tuple[FileChange, ...] = tuple(),
) -> AnalyzeProjectChangesResult:
    return AnalyzeProjectChangesResult(
        project_id=project_id,
        snapshot_path=snapshot_path,
        previous_snapshot=previous_snapshot,
        current_snapshot=current_snapshot,
        diff=diff,
    )


def create_analysis_error(
    message: str = "test error",
    file_path: PythonPath | FullPath = PythonPath("test"),
    phase: AnalysisPhase = "project-load",
    details: Mapping[str, object] | None = None,
) -> AnalysisError:
    return AnalysisError(
        message=message, file_path=file_path, phase=phase, details=details
    )


def create_resolve_error(
    message: str = "test error",
    reference: str = "test",
    details: Mapping[str, object] | None = None,
) -> ResolveError:
    return ResolveError(message=message, reference=reference, details=details)


def assert_class_type(class_analysis: ClassAnalysis) -> None:
    for base in class_analysis.bases:
        assert_type_analysis(base, class_analysis.name)
    for variable in class_analysis.variables:
        assert_type_analysis(variable.type, class_analysis.name)
    for method in class_analysis.methods:
        assert_type_analysis(method.return_type, class_analysis.name)
        for parameter in method.parameters:
            assert_type_analysis(parameter.type, class_analysis.name)


def assert_function_type(function: FunctionAnalysis) -> None:
    assert_type_analysis(function.return_type)
    for parameter in function.parameters:
        assert_type_analysis(parameter.type)


def assert_variable_type(variable: VariableAnalysis) -> None:
    assert_type_analysis(variable.type)


def assert_type_analysis(
    type_analysis: TypeAnalysis | None, class_name: str | None = None
) -> None:
    if type_analysis is None:
        return
    generated = dump_type(type_analysis=type_analysis, class_name=class_name)
    if type_analysis.text != generated:
        print(f"generated:{generated}")
        print(f"original:{type_analysis.text}")
    original = (
        type_analysis.text.replace("'", '"')
        if class_name is None
        else type_analysis.text.replace("'", '"').replace("Self", class_name)
    )
    assert original == generated


@dataclass
class BaseContext:
    project: ProjectContext
    source: SourceFileContext
    file_analysis_cach: FileAnalysisCache


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
        symbol, source_lines, source, _ = self._analyze_symbol(
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
        symbol, source_lines, target_ast, _ = self._analyze_symbol(
            file_name, symbol_name, dump_required
        )
        assert isinstance(symbol, Function)
        assert symbol.lineno
        # print(index.keys())
        # print(symbol.name)
        # print(repr(ast_symbol))
        assert isinstance(target_ast, ast.FunctionDef | ast.AsyncFunctionDef)
        return analyze_function(
            func=symbol,
            name=symbol_name,
            context=initialize_symbol_context(
                module_name=file_name, name=symbol_name, source_lines=source_lines
            ),
            ast_func=target_ast,
        )

    def _analyze_variable_base(
        self, file_name: PythonPath, symbol_name: str, dump_required: bool = False
    ) -> tuple[VariableAnalysis, BaseContext, FileAnalysisContext]:
        # symbol, source_lines, target_ast, imported = self._analyze_symbol(
        #     file_name, symbol_name, dump_required
        # )
        # assert isinstance(symbol, Attribute)
        # return analyze_variable(
        #     variable=symbol,
        #     name=symbol_name,
        #     context=initialize_symbol_context(
        #         module_name=file_name, name=symbol_name, source_lines=source_lines
        #     ),
        #     ast_symbol=target_ast,
        #     imported=imported,
        # ), base_context
        file_analysis_context, base_context = self._analyze_file_full(
            file_name=file_name
        )
        target_identity = build_declaration_identity(
            module_path=file_name, symbol_name=symbol_name
        )
        symbol = file_analysis_context.metadata.symbols.get(target_identity)
        assert isinstance(symbol, VariableAnalysis)
        return symbol, base_context, file_analysis_context

    def _analyze_class_base(
        self, file_name: PythonPath, symbol_name: str, dump_required: bool = False
    ) -> ClassAnalysis:
        symbol, source_lines, target_ast, imported = self._analyze_symbol(
            file_name, symbol_name, dump_required
        )
        assert isinstance(symbol, Class)
        assert symbol.lineno
        assert isinstance(target_ast, ast.ClassDef)
        return analyze_class(
            cls=symbol,
            name=symbol_name,
            context=initialize_symbol_context(
                module_name=file_name, name=symbol_name, source_lines=source_lines
            ),
            ast=target_ast,
            imported=imported,
        )

    def _analyze_file_full(
        self, file_name: PythonPath
    ) -> tuple[FileAnalysisContext, BaseContext]:
        module_name = file_name
        context = self._read_module_fixture(module_name)
        analysis_result = load_file_analysis_context(
            context=context.project,
            file_path=context.project.source_root / context.source.path,
            option=AnalysisOption(no_check_cache=True),
        )
        assert isinstance(analysis_result, Success)
        analysis_context = analysis_result.unwrap()
        return analysis_context, context

    def _analyze_symbol(
        self, file_name: PythonPath, symbol_name: str, dump_required: bool = False
    ) -> tuple[
        SymbolAnalysis,
        list[str],
        AstTargetSymbolType | None,
        tuple[ImportAnalysis, ...],
    ]:
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
        source = source_full_path.read_text(
            encoding="utf-8",
        )
        source_lines = source.splitlines(keepends=True)

        index = None
        ast = get_ast_index(index, source, module_name)
        target_ast = None
        for key in ast:
            if key.name == symbol_name:
                target_ast = ast[key]

        imported = _extract_imports(
            module=module, source=source, source_lines=source_lines
        )

        return symbol, source_lines, target_ast, tuple(imported)

    _default_index: dict[str, AstTargetSymbolType] = {}

    def _build_class_function_index(
        self,
        tree: ast.Module | ast.ClassDef,
        index: dict[str, AstTargetSymbolType] = _default_index,
    ) -> dict[str, AstTargetSymbolType]:

        for child in ast.iter_child_nodes(tree):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                key = child.name
                index[key] = child
            if isinstance(child, ast.Assign):  # noqa: SIM102
                if child.end_lineno is not None:
                    for target in child.targets:
                        if isinstance(target, ast.Name):
                            key = target.id
                            index[key] = child
            if isinstance(child, ast.AnnAssign):  # noqa: SIM102
                if child.end_lineno is not None:  # noqa: SIM102
                    if isinstance(child.target, ast.Name):
                        key = child.target.id
                        index[key] = child
            if isinstance(child, ast.ClassDef):
                self._build_class_function_index(child, index)
        return index

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

        workspace_result = initialize_workspace_context(
            root=WorkspaceRoot(
                path=MONOREPO_FIXTURES_ROOT, kind=WorkspaceRootKind.UV_WORKSPACE
            )
        )

        assert isinstance(result, Success)

        workspace_context = workspace_result.unwrap()
        file_analysis_cache = FileAnalysisCache(workspace_context=workspace_context)

        return BaseContext(
            project=context,
            source=source_file_context,
            file_analysis_cach=file_analysis_cache,
        )
