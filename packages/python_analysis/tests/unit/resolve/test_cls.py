from pathlib import Path
from typing import cast

import pytest
from gyomu_python_analysis.analysis.initialize import (
    initialize_project_context,
    initialize_project_from_workspace,
)
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.analysis.workspace import initialize_workspace_context
from gyomu_python_analysis.project.context import ProjectContext, PyProjectConfig
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
    WorkspaceRoot,
    WorkspaceRootKind,
)
from gyomu_python_analysis.resolve.cls import (
    collect_class_hierarchy,
    inherits_from_gyomu_base_error,
    inherits_from_pydantic_basemodel,
    is_dataclass_class,
    resolve_class_analysis,
)
from gyomu_python_analysis.resolve.file_analysis_cache import FileAnalysisCache
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    ProjectRelativePath,
    SymbolId,
    WorkspaceRelativePath,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    FIXTURES_ROOT,
    MONOREPO_FIXTURES_ROOT,
    create_analysis_error,
)
from packages.schema.test_support.helpers import (
    create_class_analysis,
    create_file_analysis_context,
    create_variable_analysis,
)


class TestIsDataclassClass:
    config = PyProjectConfig(
        path=WorkspaceRelativePath(Path(".")),
        name="test",
        version="0.1",
        description=None,
        formatter_line_length=88,
        _toml_data={},
    )

    @pytest.mark.parametrize(
        ("file_name_part", "symbol_name", "expected"),
        [
            ("models", "User", True),
            ("models", "UserWithoutDataclass", False),
            ("aliased", "Product", True),
        ],
    )
    def test_dataclass_check(
        self, file_name_part: str, symbol_name: str, expected: bool
    ) -> None:

        context = ProjectContext(
            project_root=MONOREPO_FIXTURES_ROOT / "packages" / "project_b",
            source_root=ProjectRelativePath(Path("src")),
            config=self.config,
        )
        result = load_file_analysis_context(
            context,
            ProjectRelativePath(
                Path("src/project_b") / "dataclass_models" / f"{file_name_part}.py"
            ),
        )
        declaration_identity = DeclarationIdentity(
            symbol_id=SymbolId(
                f"project_b.dataclass_models.{file_name_part}::{symbol_name}"
            ),
            declaration_id=DeclarationId("."),
        )
        assert isinstance(result, Success)

        file_context = result.unwrap()
        symbol = file_context.metadata.symbols.get(declaration_identity)

        assert symbol is not None
        assert isinstance(symbol, ClassAnalysis)
        is_dataclass = is_dataclass_class(cls=symbol, module=file_context.analysis)
        assert is_dataclass == expected


@pytest.fixture
def workspace_context() -> WorkspaceContext:

    result = initialize_workspace_context(
        root=WorkspaceRoot(
            path=MONOREPO_FIXTURES_ROOT, kind=WorkspaceRootKind.UV_WORKSPACE
        )
    )

    assert isinstance(result, Success)

    return result.unwrap()


class TestCollectClassHierarchy:
    @pytest.mark.parametrize(
        (
            "project_name",
            "python_path",
            "symbol_name",
            "is_base_first",
            "expected_resolved",
            "expected_unresolved",
            "expected_unresolved_reason",
            "expected_external",
        ),
        [
            (
                "project-b",
                "project_b.class_hierarchy.base",
                "Base",
                True,
                ["Base"],
                [],
                [],
                [],
            ),
            (
                "project-b",
                "project_b.class_hierarchy.intermediate",
                "Intermediate",
                True,
                ["Base", "Intermediate"],
                [],
                [],
                [],
            ),
            (
                "project-b",
                "project_b.class_hierarchy.derived",
                "Derived",
                True,
                ["Base", "Intermediate", "Derived"],
                [],
                [],
                [],
            ),
            (
                "project-b",
                "project_b.class_hierarchy.multiple_inheritance",
                "Diamond",
                True,
                ["Base", "Left", "Right", "Diamond"],
                [],
                [],
                [],
            ),
            (
                "project-b",
                "project_b.class_hierarchy.multiple_inheritance",
                "Diamond",
                False,
                [
                    "Diamond",
                    "Left",
                    "Base",
                    "Right",
                ],
                [],
                [],
                [],
            ),
            (
                "project-b",
                "project_b.class_hierarchy.external",
                "PydanticBase",
                True,
                [
                    "PydanticBase",
                ],
                [],
                [],
                ["pydantic::BaseModel"],
            ),
            (
                "project-b",
                "project_b.class_hierarchy.unresolved",
                "DerivedFromUnknown",
                True,
                [
                    "DerivedFromUnknown",
                ],
                ["UnknownBase"],
                ["reference-not-resolved"],
                [],
            ),
            (
                "project-b",
                "project_b.class_hierarchy.unresolved",
                "DerivedFromUnknown3",
                True,
                [
                    "DerivedFromUnknown3",
                ],
                ["UnresolvedSymbol"],
                ["symbol-not-found-in-module"],
                [],
            ),
            (
                "project-b",
                "project_b.class_hierarchy.unresolved",
                "DerivedFromUnknown4",
                True,
                [
                    "DerivedFromUnknown4",
                ],
                ["NotClass"],
                ["symbol-is-not-class"],
                [],
            ),
            (
                "project-b",
                "project_b.class_hierarchy.unresolved",
                "DerivedFromUnknown5",
                True,
                [
                    "DerivedFromUnknown5",
                ],
                ["NonExistence"],
                ["reference-not-resolved"],
                [],
            ),
            (
                "project-b",
                "project_b.class_hierarchy.unresolved",
                "MixedUnknown",
                True,
                [
                    "Base",
                    "Intermediate",
                    "MixedUnknown",
                ],
                ["UnknownBase"],
                ["reference-not-resolved"],
                [],
            ),
        ],
    )
    def test_hierarchy(
        self,
        project_name: str,
        python_path: str,
        symbol_name: str,
        is_base_first: bool,
        expected_resolved: list[str],
        expected_unresolved: list[str],
        expected_unresolved_reason: list[str],
        expected_external: list[str],
        workspace_context: WorkspaceContext,
    ) -> None:
        target_project = next(
            (
                project
                for project in workspace_context.projects
                if project.config.name == project_name
            ),
            None,
        )
        # for project in workspace_context.projects:
        #     print(project.config.name)
        assert target_project is not None

        project_context = initialize_project_from_workspace(
            workspace_context.path, target_project
        )
        target_source_path = Path(python_path.replace(".", "/") + ".py")
        result = load_file_analysis_context(
            project_context,
            ProjectRelativePath(Path("src") / target_source_path),
            option=AnalysisOption(no_check_cache=True),
        )
        declaration_identity = DeclarationIdentity(
            symbol_id=SymbolId(f"{python_path}::{symbol_name}"),
            declaration_id=DeclarationId("."),
        )
        assert isinstance(result, Success)

        file_context = result.unwrap()
        symbol = file_context.metadata.symbols.get(declaration_identity)
        assert symbol is not None
        assert isinstance(symbol, ClassAnalysis)

        result = collect_class_hierarchy(
            cls=symbol,
            module=file_context.analysis,
            workspace=workspace_context,
            is_base_first=is_base_first,
        )
        assert isinstance(result, Success)
        class_resolutions = result.unwrap()

        resolved = [resolved.symbol.name for resolved in class_resolutions.resolved()]
        unresolved = [
            unresolved.reference_name for unresolved in class_resolutions.unresolved()
        ]
        unresolved_reason = [
            unresolved.reason for unresolved in class_resolutions.unresolved()
        ]
        external = [
            external.reference.symbol_id for external in class_resolutions.external()
        ]
        if len(external) > 0:
            print(class_resolutions.external())
        assert expected_resolved == resolved
        assert expected_unresolved == unresolved
        assert expected_unresolved_reason == unresolved_reason
        assert expected_external == external


class TestInheritsFromPydanticBasemodel:
    @pytest.mark.parametrize(
        ("project_name", "python_path", "symbol_name", "expected"),
        [
            ("project-a", "project_a.pydantic_models.base", "ProjectABaseModel", True),
            (
                "project-b",
                "project_b.pydantic_models.intermediate",
                "IntermediateModel",
                True,
            ),
            (
                "project-b",
                "project_b.pydantic_models.models",
                "UserModel",
                True,
            ),
            (
                "project-b",
                "project_b.pydantic_models.inheritance",
                "LocalBaseModel",
                True,
            ),
            (
                "project-b",
                "project_b.pydantic_models.inheritance",
                "LocalDerivedModel",
                True,
            ),
            (
                "project-b",
                "project_b.pydantic_models.inheritance",
                "PlainDerived",
                False,
            ),
            (
                "project-b",
                "project_b.pydantic_models.inheritance",
                "MixedDerived",
                True,
            ),
        ],
    )
    def test_pydantic_basemodel(
        self,
        project_name: str,
        python_path: str,
        symbol_name: str,
        expected: bool,
        workspace_context: WorkspaceContext,
    ) -> None:
        target_project = next(
            (
                project
                for project in workspace_context.projects
                if project.config.name == project_name
            ),
            None,
        )
        # for project in workspace_context.projects:
        #     print(project.config.name)
        assert target_project is not None

        project_context = initialize_project_from_workspace(
            workspace_context.path, target_project
        )
        target_source_path = Path(python_path.replace(".", "/") + ".py")
        result = load_file_analysis_context(
            project_context,
            ProjectRelativePath(Path("src") / target_source_path),
        )
        declaration_identity = DeclarationIdentity(
            symbol_id=SymbolId(f"{python_path}::{symbol_name}"),
            declaration_id=DeclarationId("."),
        )
        assert isinstance(result, Success)

        file_context = result.unwrap()
        symbol = file_context.metadata.symbols.get(declaration_identity)
        assert symbol is not None
        assert isinstance(symbol, ClassAnalysis)
        is_pydantic_result = inherits_from_pydantic_basemodel(
            cls=symbol, module=file_context.analysis, workspace=workspace_context
        )
        assert isinstance(is_pydantic_result, Success)
        assert is_pydantic_result.unwrap() == expected


class TestInheritsFromGyomuBaseError:
    @pytest.mark.parametrize(
        ("project_name", "python_path", "symbol_name", "expected"),
        [
            ("project-a", "project_a.gyomu_errors.base", "BasedError", True),
            (
                "project-b",
                "project_b.gyomu_errors.errors",
                "InheritError",
                True,
            ),
            (
                "project-b",
                "project_b.gyomu_errors.errors",
                "NonTargetError",
                False,
            ),
        ],
    )
    def test_gyomu_base_error(
        self,
        project_name: str,
        python_path: str,
        symbol_name: str,
        expected: bool,
        workspace_context: WorkspaceContext,
    ) -> None:
        target_project = next(
            (
                project
                for project in workspace_context.projects
                if project.config.name == project_name
            ),
            None,
        )
        # for project in workspace_context.projects:
        #     print(project.config.name)
        assert target_project is not None

        project_context = initialize_project_from_workspace(
            workspace_context.path, target_project
        )
        target_source_path = Path(python_path.replace(".", "/") + ".py")
        result = load_file_analysis_context(
            project_context,
            ProjectRelativePath(Path("src") / target_source_path),
        )
        declaration_identity = DeclarationIdentity(
            symbol_id=SymbolId(f"{python_path}::{symbol_name}"),
            declaration_id=DeclarationId("."),
        )
        assert isinstance(result, Success)

        file_context = result.unwrap()
        symbol = file_context.metadata.symbols.get(declaration_identity)
        assert symbol is not None
        assert isinstance(symbol, ClassAnalysis)
        is_gyomu_base_error_result = inherits_from_gyomu_base_error(
            cls=symbol, module=file_context.analysis, workspace=workspace_context
        )
        assert isinstance(is_gyomu_base_error_result, Success)
        assert is_gyomu_base_error_result.unwrap() == expected


class TestResolveClassAnalysis:
    def test_success(
        self,
        mocker: MockerFixture,
    ) -> None:
        identity = DeclarationIdentity(
            symbol_id=SymbolId("project_a.models::Product"),
            declaration_id=DeclarationId("."),
        )
        class_analysis = create_class_analysis(identity=identity)
        file_analysis_context = create_file_analysis_context(symbol=class_analysis)
        project_context = initialize_project_context(
            project_root=FIXTURES_ROOT,
            source_root=ProjectRelativePath(Path("src")),
        ).unwrap()

        file_analysis_context.metadata.symbols[identity] = class_analysis

        file_analysis_cache = mocker.create_autospec(
            FileAnalysisCache,
            instance=True,
        )
        file_analysis_cache.get_file_analysis_context.return_value = Success(
            file_analysis_context
        )

        result = resolve_class_analysis(
            declaration_identity=identity,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
        )

        assert isinstance(result, Success)
        file_analysis, symbol = result.unwrap()
        assert file_analysis is file_analysis_context
        assert symbol is class_analysis

        file_analysis_cache.get_file_analysis_context.assert_called_once_with(
            project_context=project_context,
            identity=identity,
        )

    def test_symbol_resolution_failure_is_propagated(
        self,
        mocker: MockerFixture,
    ) -> None:
        identity = DeclarationIdentity(
            symbol_id=SymbolId("project_a.models::product_name"),
            declaration_id=DeclarationId("."),
        )
        project_context = initialize_project_context(
            project_root=FIXTURES_ROOT,
            source_root=ProjectRelativePath(Path("src")),
        ).unwrap()

        expected_error = create_analysis_error()

        file_analysis_cache = cast(FileAnalysisCache, mocker.Mock())
        resolve_symbol_analysis_mock = mocker.patch(
            "gyomu_python_analysis.resolve.cls.resolve_symbol_analysis",
            return_value=Failure(expected_error),
        )

        result = resolve_class_analysis(
            declaration_identity=identity,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
        )

        assert isinstance(result, Failure)
        assert result.failure() is expected_error

        resolve_symbol_analysis_mock.assert_called_once_with(
            identity,
            project_context,
            file_analysis_cache,
        )

    def test_symbol_is_not_class(self, mocker: MockerFixture) -> None:
        identity = DeclarationIdentity(
            symbol_id=SymbolId("project_a.models::product_name"),
            declaration_id=DeclarationId("."),
        )

        # 実際の SymbolAnalysis 型の fixture を使う。
        file_analysis_context = create_file_analysis_context(
            symbol=create_variable_analysis(identity=identity)
        )
        project_context = initialize_project_context(
            project_root=FIXTURES_ROOT,
            source_root=ProjectRelativePath(Path("src")),
        ).unwrap()

        file_analysis_cache = mocker.create_autospec(
            FileAnalysisCache,
            instance=True,
        )
        file_analysis_cache.get_file_analysis_context.return_value = Success(
            file_analysis_context
        )

        result = resolve_class_analysis(
            declaration_identity=identity,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
        )

        assert isinstance(result, Failure)
        error = result.failure()
        assert error.message == "symbol is not class"
        assert error.details == {"identity": identity}
