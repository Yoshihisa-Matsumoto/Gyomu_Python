import ast
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from griffe import Attribute, Class, Function, TypeAlias
from gyomu_infra.filesystem.file_io import read_source_text
from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.analyzers.cls import analyze_class
from gyomu_python_analysis.analysis.analyzers.context import initialize_symbol_context
from gyomu_python_analysis.analysis.analyzers.functions import analyze_function
from gyomu_python_analysis.analysis.analyzers.type_alias import analyze_type_alias
from gyomu_python_analysis.analysis.analyzers.variables import analyze_variable
from gyomu_python_analysis.analysis.file.source_file_context import SourceFileContext
from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.analysis.load import load_module
from gyomu_python_analysis.analysis.load_module import load_module_analysis
from gyomu_python_analysis.project.context import ProjectContext, PyProjectConfig
from gyomu_python_analysis.snapshot.models import (
    AnalyzeProjectChangesResult,
    FileAdded,
    FileChange,
    FileDeleted,
    FileSnapshot,
    FileUpdated,
    ProjectSnapshot,
)
from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis
from gyomu_schema.schemas.python.types import (
    ProjectRelativePath,
    PythonPath,
    WorkspaceRelativePath,
)
from gyomu_schema.schemas.python.variable import VariableAnalysis
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure

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


def _create_context() -> ProjectContext:
    return initialize_project_context(
        project_root=FIXTURES_ROOT, source_root=ProjectRelativePath(Path("src"))
    ).unwrap()


def create_test_file_snapshot(
    project_relative_path: ProjectRelativePath,
    raw_hash: str = "ABCDE",
) -> FileSnapshot:
    modified_at: datetime = datetime.now()
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
        symbol, source_lines, source = self._analyze_symbol(
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
        symbol, source_lines, index = self._analyze_symbol(
            file_name, symbol_name, dump_required
        )
        assert isinstance(symbol, Function)
        assert symbol.lineno
        ast_symbol = index.get(symbol.name)
        # print(index.keys())
        # print(symbol.name)
        # print(repr(ast_symbol))
        assert isinstance(ast_symbol, ast.FunctionDef | ast.AsyncFunctionDef)
        return analyze_function(
            func=symbol,
            name=symbol_name,
            context=initialize_symbol_context(
                module_name=file_name, name=symbol_name, source_lines=source_lines
            ),
            ast=ast_symbol,
        )

    def _analyze_variable_base(
        self, file_name: PythonPath, symbol_name: str, dump_required: bool = False
    ) -> VariableAnalysis:
        symbol, source_lines, index = self._analyze_symbol(
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
        symbol, source_lines, index = self._analyze_symbol(
            file_name, symbol_name, dump_required
        )
        assert isinstance(symbol, Class)
        assert symbol.lineno
        ast_symbol = index.get(symbol.name)
        assert isinstance(ast_symbol, ast.ClassDef)
        return analyze_class(
            cls=symbol,
            name=symbol_name,
            context=initialize_symbol_context(
                module_name=file_name, name=symbol_name, source_lines=source_lines
            ),
            ast=ast_symbol,
        )

    def _analyze_symbol(
        self, file_name: PythonPath, symbol_name: str, dump_required: bool = False
    ) -> tuple[
        SymbolAnalysis,
        list[str],
        dict[str, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef],
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
        read_result = read_source_text(source_full_path)
        if isinstance(read_result, Failure):
            raise read_result.failure()
        source = read_result.unwrap()
        source_lines = source.splitlines(keepends=True)
        tree = ast.parse(source=source, filename=module_name)
        # index = _analyze_ast_module(source=source, source_path=module_name)
        index: dict[str, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef] = (
            self._build_class_function_index(tree)
        )

        return symbol, source_lines, index

    def _build_class_function_index(
        self,
        tree: ast.Module | ast.ClassDef,
        index: dict[str, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef] = {},
    ) -> dict[str, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef]:

        for child in ast.iter_child_nodes(tree):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                key = child.name
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

        return BaseContext(project=context, source=source_file_context)
