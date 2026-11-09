from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, Mock

import pytest
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
    WorkspaceRoot,
    WorkspaceRootKind,
)
from gyomu_python_analysis.resolve.models import (
    LiteralValueType,
    PrimitiveType,
    SymbolType,
)
from gyomu_schema.schemas.config.test.model_defaults import (
    PackageModelDefaults,
)
from gyomu_schema.schemas.python.types import DeclarationIdentity
from gyomu_schema.schemas.testing.helper import (
    HelperInventoryItem,
    ParameterInfo,
)
from gyomu_schema.schemas.types import FullPath
from gyomu_test.error.parameter import MissingFunctionParameterDefault
from gyomu_test.helper.defaults import resolution as resolver_module
from gyomu_test.helper.defaults.resolution import (
    PrimitiveDefaultConfigContext,
    PrimitiveDefaultResolver,
    SymbolDefaultConfigContext,
    SymbolDefaultResolver,
    find_missing_function_parameter_defaults,
)
from returns.result import Failure, Success

from packages.schema.test_support.helpers import (
    create_config_error,
    create_parameter_default,
    create_primitive_default,
)


class TestFindMissingFunctionParameterDefaults:
    def test_returns_none_when_all_parameters_have_defaults(self) -> None:
        parameter_with_default = ParameterInfo(
            name="name",
            parameter_type=MagicMock(),
            default=MagicMock(),
        )
        inventory = HelperInventoryItem(
            target_identity=MagicMock(spec=DeclarationIdentity),
            function_name="create_example",
            parameters=(parameter_with_default,),
        )

        actual = find_missing_function_parameter_defaults(inventory)

        assert actual is None

    def test_returns_missing_parameter_when_default_is_none(self) -> None:
        identity = MagicMock(spec=DeclarationIdentity)
        parameter_without_default = ParameterInfo(
            name="name",
            parameter_type=MagicMock(),
            default=None,
        )
        inventory = HelperInventoryItem(
            target_identity=identity,
            function_name="create_example",
            parameters=(parameter_without_default,),
        )

        actual = find_missing_function_parameter_defaults(inventory)

        assert actual == (
            MissingFunctionParameterDefault(
                identity=identity,
                parameter=parameter_without_default,
            ),
        )

    def test_returns_all_parameters_without_defaults(self) -> None:
        identity = MagicMock(spec=DeclarationIdentity)
        parameter_with_default = ParameterInfo(
            name="name",
            parameter_type=MagicMock(),
            default=MagicMock(),
        )
        first_parameter_without_default = ParameterInfo(
            name="package",
            parameter_type=MagicMock(),
            default=None,
        )
        second_parameter_without_default = ParameterInfo(
            name="completed_steps",
            parameter_type=MagicMock(),
            default=None,
        )
        inventory = HelperInventoryItem(
            target_identity=identity,
            function_name="create_example",
            parameters=(
                parameter_with_default,
                first_parameter_without_default,
                second_parameter_without_default,
            ),
        )

        actual = find_missing_function_parameter_defaults(inventory)

        assert actual == (
            MissingFunctionParameterDefault(
                identity=identity,
                parameter=first_parameter_without_default,
            ),
            MissingFunctionParameterDefault(
                identity=identity,
                parameter=second_parameter_without_default,
            ),
        )

    def test_returns_none_when_inventory_has_no_parameters(self) -> None:
        inventory = HelperInventoryItem(
            target_identity=MagicMock(spec=DeclarationIdentity),
            function_name="create_example",
            parameters=(),
        )

        actual = find_missing_function_parameter_defaults(inventory)

        assert actual is None


class TestDefaultResolvers:
    @staticmethod
    def _create_workspace_root(
        path: Path,
        kind: WorkspaceRootKind,
    ) -> WorkspaceRoot:
        workspace_root = Mock()
        workspace_root.path = path
        workspace_root.kind = kind
        return cast(WorkspaceRoot, workspace_root)

    @staticmethod
    def _create_project_context(project_root: Path) -> ProjectContext:
        project_context = Mock()
        project_context.project_root = project_root
        return cast(ProjectContext, project_context)

    @staticmethod
    def _create_workspace_context() -> WorkspaceContext:
        return cast(WorkspaceContext, Mock())

    @staticmethod
    def _create_primitive_type(
        parameter_name: str = "value",
        primitive_type: str = "str",
    ) -> PrimitiveType:
        return PrimitiveType(
            parameter_name=parameter_name,
            primitive_type=primitive_type,
        )

    @staticmethod
    def _create_literal_type(
        parameter_name: str = "value",
        value: str | bytes | bool | int | float | complex | None = "sample",
    ) -> LiteralValueType:
        return LiteralValueType(
            parameter_name=parameter_name,
            value=value,
        )

    @staticmethod
    def _create_symbol_type(
        module_name: str = "other_package.models",
        symbol_name: str = "SampleModel",
    ) -> SymbolType:
        context = Mock()
        context.analysis.module_name = module_name

        symbol = Mock()
        symbol.name = symbol_name
        symbol.identity = f"{module_name}.{symbol_name}"

        return SymbolType(symbol=symbol, context=context)

    @staticmethod
    def _create_primitive_context(
        type_default: PrimitiveType | LiteralValueType,
        workspace_root: WorkspaceRoot,
        project_context: ProjectContext,
    ) -> PrimitiveDefaultConfigContext:
        return PrimitiveDefaultConfigContext(
            type_default=type_default,
            workspace_root=workspace_root,
            workspace_context=TestDefaultResolvers._create_workspace_context(),
            project_context=project_context,
        )

    @staticmethod
    def _create_symbol_context(
        type_default: SymbolType,
        workspace_root: WorkspaceRoot,
        project_context: ProjectContext,
    ) -> SymbolDefaultConfigContext:
        return SymbolDefaultConfigContext(
            type_default=type_default,
            workspace_root=workspace_root,
            workspace_context=TestDefaultResolvers._create_workspace_context(),
            project_context=project_context,
        )

    class TestPrimitiveDefaultResolver:
        def test_workspace_returns_project_then_workspace_paths(self):
            workspace_path = Path("/workspace")
            project_path = workspace_path / "packages" / "my_package"

            context = TestDefaultResolvers._create_primitive_context(
                type_default=TestDefaultResolvers._create_primitive_type(),
                workspace_root=TestDefaultResolvers._create_workspace_root(
                    workspace_path,
                    WorkspaceRootKind.UV_WORKSPACE,
                ),
                project_context=TestDefaultResolvers._create_project_context(
                    project_path,
                ),
            )

            result = PrimitiveDefaultResolver().get_paths(context)

            assert result == Success(
                (
                    FullPath(
                        project_path / ".gyomu/config/$Package.default.json",
                    ),
                    FullPath(
                        workspace_path / ".gyomu/config/$Workspace.default.json",
                    ),
                )
            )

        def test_non_workspace_returns_only_project_path(self):
            project_path = Path("/project")

            context = TestDefaultResolvers._create_primitive_context(
                type_default=TestDefaultResolvers._create_primitive_type(),
                workspace_root=TestDefaultResolvers._create_workspace_root(
                    project_path,
                    cast(WorkspaceRootKind, Mock()),
                ),
                project_context=TestDefaultResolvers._create_project_context(
                    project_path,
                ),
            )

            result = PrimitiveDefaultResolver().get_paths(context)

            assert result == Success(
                (
                    FullPath(
                        project_path / ".gyomu/config/$Package.default.json",
                    ),
                )
            )

    class TestSymbolDefaultResolver:
        def test_target_helper_function_returns_empty_paths(
            self,
            monkeypatch: pytest.MonkeyPatch,
        ):
            monkeypatch.setattr(
                resolver_module,
                "_get_model_kind",
                lambda *_: Success("target_helper"),
            )

            workspace_path = Path("/workspace")
            project_path = workspace_path / "packages/my_package"

            context = TestDefaultResolvers._create_symbol_context(
                type_default=TestDefaultResolvers._create_symbol_type(),
                workspace_root=TestDefaultResolvers._create_workspace_root(
                    workspace_path,
                    WorkspaceRootKind.UV_WORKSPACE,
                ),
                project_context=TestDefaultResolvers._create_project_context(
                    project_path,
                ),
            )

            result = SymbolDefaultResolver().get_paths(context)

            assert result == Success(())

        def test_symbol_in_same_project_does_not_add_duplicate_project_path(
            self,
            monkeypatch: pytest.MonkeyPatch,
        ):
            monkeypatch.setattr(
                resolver_module,
                "_get_model_kind",
                lambda *_: Success(None),
            )
            monkeypatch.setattr(
                resolver_module,
                "is_file_in_project",
                lambda **_: True,
            )

            find_workspace_project = Mock()
            monkeypatch.setattr(
                resolver_module,
                "find_workspace_project",
                find_workspace_project,
            )

            workspace_path = Path("/workspace")
            project_path = workspace_path / "packages/my_package"

            context = TestDefaultResolvers._create_symbol_context(
                type_default=TestDefaultResolvers._create_symbol_type(),
                workspace_root=TestDefaultResolvers._create_workspace_root(
                    workspace_path,
                    WorkspaceRootKind.UV_WORKSPACE,
                ),
                project_context=TestDefaultResolvers._create_project_context(
                    project_path,
                ),
            )

            result = SymbolDefaultResolver().get_paths(context)

            assert result == Success(
                (
                    FullPath(
                        project_path / ".gyomu/config/$Package.default.json",
                    ),
                    FullPath(
                        workspace_path / ".gyomu/config/$Workspace.default.json",
                    ),
                )
            )
            find_workspace_project.assert_not_called()

        def test_symbol_in_another_project_adds_referenced_project_path(
            self,
            monkeypatch: pytest.MonkeyPatch,
        ):
            monkeypatch.setattr(
                resolver_module,
                "_get_model_kind",
                lambda *_: Success(None),
            )
            monkeypatch.setattr(
                resolver_module,
                "is_file_in_project",
                lambda **_: False,
            )

            workspace_project = Mock()
            workspace_project.path = Path("packages/other_package")

            monkeypatch.setattr(
                resolver_module,
                "find_workspace_project",
                lambda **_: Success(workspace_project),
            )

            workspace_path = Path("/workspace")
            project_path = workspace_path / "packages/my_package"
            referenced_project_path = workspace_path / "packages/other_package"

            context = TestDefaultResolvers._create_symbol_context(
                type_default=TestDefaultResolvers._create_symbol_type(),
                workspace_root=TestDefaultResolvers._create_workspace_root(
                    workspace_path,
                    WorkspaceRootKind.UV_WORKSPACE,
                ),
                project_context=TestDefaultResolvers._create_project_context(
                    project_path,
                ),
            )

            result = SymbolDefaultResolver().get_paths(context)

            assert result == Success(
                (
                    FullPath(
                        project_path / ".gyomu/config/$Package.default.json",
                    ),
                    FullPath(
                        referenced_project_path / ".gyomu/config/$Package.default.json",
                    ),
                    FullPath(
                        workspace_path / ".gyomu/config/$Workspace.default.json",
                    ),
                )
            )

        def test_model_kind_failure_is_propagated(
            self,
            monkeypatch: pytest.MonkeyPatch,
        ):
            config_error = create_config_error(
                "model kind error",
                source="json",
                phase="path-resolve",
            )
            monkeypatch.setattr(
                resolver_module,
                "_get_model_kind",
                lambda *_: Failure(config_error),
            )

            workspace_path = Path("/workspace")
            project_path = workspace_path / "packages/my_package"

            context = TestDefaultResolvers._create_symbol_context(
                type_default=TestDefaultResolvers._create_symbol_type(),
                workspace_root=TestDefaultResolvers._create_workspace_root(
                    workspace_path,
                    WorkspaceRootKind.UV_WORKSPACE,
                ),
                project_context=TestDefaultResolvers._create_project_context(
                    project_path,
                ),
            )

            result = SymbolDefaultResolver().get_paths(context)

            assert isinstance(result, Failure)

    class TestPrimitiveDefaultResolverExtract:
        def test_extracts_matching_primitive_default(self):
            # expected = cast(PrimitiveDefault, Mock())
            other = create_primitive_default(
                type_name="str",
                variable_name="other",
                parameters=(create_parameter_default(),),
            )
            other.variable_name = "other"
            other.type_name = "str"

            matching = create_primitive_default(
                type_name="str",
                variable_name="value",
                parameters=(create_parameter_default(),),
            )

            primitives = Mock()
            primitives.defaults_per_variable_name = {
                "other": other.parameters,
                "value": matching.parameters,
            }
            config = Mock()
            config.primitives_per_type = {"str": primitives}

            context = TestDefaultResolvers._create_primitive_context(
                type_default=TestDefaultResolvers._create_primitive_type(
                    parameter_name="value",
                    primitive_type="str",
                ),
                workspace_root=TestDefaultResolvers._create_workspace_root(
                    Path("/project"),
                    cast(WorkspaceRootKind, Mock()),
                ),
                project_context=TestDefaultResolvers._create_project_context(
                    Path("/project"),
                ),
            )

            # 設定エントリ自体を期待値として使う
            result = PrimitiveDefaultResolver().extract(
                cast(PackageModelDefaults, config),
                context,
            )

            assert result == Success(matching)

        def test_returns_none_when_primitive_default_is_missing(self):
            config = Mock()
            config.primitives_per_type = {}

            context = TestDefaultResolvers._create_primitive_context(
                type_default=TestDefaultResolvers._create_primitive_type(),
                workspace_root=TestDefaultResolvers._create_workspace_root(
                    Path("/project"),
                    cast(WorkspaceRootKind, Mock()),
                ),
                project_context=TestDefaultResolvers._create_project_context(
                    Path("/project"),
                ),
            )

            result = PrimitiveDefaultResolver().extract(
                cast(PackageModelDefaults, config),
                context,
            )

            assert result == Success(None)

        def test_extracts_literal_default_using_value_type_name(self):
            matching = create_primitive_default(
                type_name="str",
                variable_name="value",
                parameters=(create_parameter_default(),),
            )

            primitives = Mock()
            primitives.defaults_per_variable_name = {"value": matching.parameters}
            config = Mock()
            config.primitives_per_type = {"str": primitives}

            context = TestDefaultResolvers._create_primitive_context(
                type_default=TestDefaultResolvers._create_literal_type(
                    parameter_name="value",
                    value="sample",
                ),
                workspace_root=TestDefaultResolvers._create_workspace_root(
                    Path("/project"),
                    cast(WorkspaceRootKind, Mock()),
                ),
                project_context=TestDefaultResolvers._create_project_context(
                    Path("/project"),
                ),
            )

            result = PrimitiveDefaultResolver().extract(
                cast(PackageModelDefaults, config),
                context,
            )

            assert result == Success(matching)

    class TestSymbolDefaultResolverExtract:
        def test_extracts_matching_model_default(self):
            # expected = cast(ModelDefault, Mock())

            matching = Mock()
            matching.symbol_name = "SampleModel"

            other = Mock()
            other.symbol_name = "OtherModel"

            module_defaults = Mock()
            module_defaults.models = [other, matching]

            config = Mock()
            config.models_per_module_path = {
                "other_package.models": module_defaults,
            }

            context = TestDefaultResolvers._create_symbol_context(
                type_default=TestDefaultResolvers._create_symbol_type(
                    module_name="other_package.models",
                    symbol_name="SampleModel",
                ),
                workspace_root=TestDefaultResolvers._create_workspace_root(
                    Path("/project"),
                    cast(WorkspaceRootKind, Mock()),
                ),
                project_context=TestDefaultResolvers._create_project_context(
                    Path("/project"),
                ),
            )

            result = SymbolDefaultResolver().extract(
                cast(PackageModelDefaults, config),
                context,
            )

            assert result == Success(matching)

        def test_returns_none_when_module_is_missing(self):
            config = Mock()
            config.models_per_module_path = {}

            context = TestDefaultResolvers._create_symbol_context(
                type_default=TestDefaultResolvers._create_symbol_type(),
                workspace_root=TestDefaultResolvers._create_workspace_root(
                    Path("/project"),
                    cast(WorkspaceRootKind, Mock()),
                ),
                project_context=TestDefaultResolvers._create_project_context(
                    Path("/project"),
                ),
            )

            result = SymbolDefaultResolver().extract(
                cast(PackageModelDefaults, config),
                context,
            )

            assert result == Success(None)

        def test_returns_none_when_symbol_is_missing(self):
            module_defaults = Mock()
            module_defaults.models = []

            config = Mock()
            config.models_per_module_path = {
                "other_package.models": module_defaults,
            }

            context = TestDefaultResolvers._create_symbol_context(
                type_default=TestDefaultResolvers._create_symbol_type(),
                workspace_root=TestDefaultResolvers._create_workspace_root(
                    Path("/project"),
                    cast(WorkspaceRootKind, Mock()),
                ),
                project_context=TestDefaultResolvers._create_project_context(
                    Path("/project"),
                ),
            )

            result = SymbolDefaultResolver().extract(
                cast(PackageModelDefaults, config),
                context,
            )

            assert result == Success(None)
