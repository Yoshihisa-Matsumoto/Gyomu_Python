from pathlib import Path
from typing import cast
from unittest.mock import Mock

from gyomu_config.request import ConfigRequest
from gyomu_python_analysis.project.context import ProjectContext, WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceRoot
from gyomu_schema.error.config import ConfigError
from gyomu_schema.schemas.config.test.model_defaults import (
    ModelDefault,
    ModelDefaults,
    PackageModelDefaults,
    PrimitiveDefault,
    PrimitiveDefaults,
)
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.types import FullPath
from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.defaults.save import (
    DefaultConfigPathResolver,
    _retrieve_existing_config,
    _save_config,
    _update_primitive,
    _update_symbol,
    build_config_request,
    save_primitive_parameter_default_config,
    save_symbol_parameter_default_config,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.test_support.helpers import create_parameter_default


def create_primitive_default(
    type_name: str = "int",
    variable_name: str = "value",
    parameters: tuple = (),
) -> PrimitiveDefault:
    return PrimitiveDefault(
        type_name=type_name,
        variable_name=variable_name,
        parameters=parameters,
    )


def create_model_default(
    symbol_name: str,
    parameters: tuple = (),
) -> ModelDefault:
    return ModelDefault(
        symbol_name=symbol_name,
        parameters=parameters,
    )


def create_package_model_defaults() -> PackageModelDefaults:
    return PackageModelDefaults(
        models_per_module_path={},
        primitives_per_type={},
    )


class TestDefaultConfigPathResolver:
    def test_get_path_returns_context(self) -> None:
        context = cast(FullPath, Path("/workspace/config.json"))

        result = DefaultConfigPathResolver().get_path(context)

        assert isinstance(result, Success)
        assert result.unwrap() == context


class TestBuildConfigRequest:
    def test_builds_request(self) -> None:
        config_path = cast(FullPath, Path("/workspace/config.json"))

        request = build_config_request(config_path)

        assert isinstance(request, ConfigRequest)
        assert request.config_type is PackageModelDefaults
        assert request.context == config_path

        path_result = request.path_resolver.get_path(request.context)
        assert isinstance(path_result, Success)
        assert path_result.unwrap() == config_path


class TestRetrieveExistingConfig:
    def test_returns_existing_config(self, mocker: MockerFixture) -> None:
        config_path = cast(FullPath, Path("/workspace/config.json"))
        expected = create_package_model_defaults()

        retrieve_mock = mocker.patch(
            "gyomu_test.helper.defaults.save.retrieve_config",
            return_value=Success(expected),
        )

        result = _retrieve_existing_config(config_path)

        assert isinstance(result, Success)
        assert result.unwrap() is expected
        retrieve_mock.assert_called_once()

    def test_creates_empty_config_when_config_is_missing(
        self,
        mocker: MockerFixture,
    ) -> None:
        config_path = cast(FullPath, Path("/workspace/config.json"))

        mocker.patch(
            "gyomu_test.helper.defaults.save.retrieve_config",
            return_value=Success(None),
        )

        result = _retrieve_existing_config(config_path)

        assert isinstance(result, Success)
        assert result.unwrap() == create_package_model_defaults()

    def test_returns_failure_when_retrieval_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        config_path = cast(FullPath, Path("/workspace/config.json"))
        config_error = cast(ConfigError, Exception("read failed"))

        mocker.patch(
            "gyomu_test.helper.defaults.save.retrieve_config",
            return_value=Failure(config_error),
        )

        result = _retrieve_existing_config(config_path)

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)


class TestUpdatePrimitive:
    def test_adds_new_type_and_variable(self) -> None:
        existing = create_package_model_defaults()
        primitive = create_primitive_default("int", "value")

        result = _update_primitive(existing, primitive)

        assert (
            result.primitives_per_type["int"].defaults_per_variable_name["value"] == ()
        )
        assert result.models_per_module_path == {}

    def test_adds_variable_to_existing_type(self) -> None:
        existing = PackageModelDefaults(
            models_per_module_path={},
            primitives_per_type={
                "int": PrimitiveDefaults(defaults_per_variable_name={"count": ()})
            },
        )

        result = _update_primitive(
            existing,
            create_primitive_default("int", "value"),
        )

        assert result.primitives_per_type["int"].defaults_per_variable_name == {
            "count": (),
            "value": (),
        }

    def test_replaces_existing_variable_parameters(self) -> None:
        old_parameter = create_parameter_default()
        new_parameter = create_parameter_default()

        existing = PackageModelDefaults(
            models_per_module_path={},
            primitives_per_type={
                "int": PrimitiveDefaults(
                    defaults_per_variable_name={
                        "value": (old_parameter,),
                        "count": (),
                    }
                )
            },
        )
        primitive = create_primitive_default(
            "int",
            "value",
            (new_parameter,),
        )

        result = _update_primitive(existing, primitive)

        actual = result.primitives_per_type["int"].defaults_per_variable_name
        assert actual["value"] == (new_parameter,)
        assert actual["count"] == ()

    def test_does_not_mutate_existing_config(self) -> None:
        existing = PackageModelDefaults(
            models_per_module_path={},
            primitives_per_type={
                "int": PrimitiveDefaults(defaults_per_variable_name={"count": ()})
            },
        )

        _update_primitive(
            existing,
            create_primitive_default("int", "value"),
        )

        assert existing.primitives_per_type["int"].defaults_per_variable_name == {
            "count": ()
        }


class TestUpdateSymbol:
    def test_adds_new_module_and_symbol(self) -> None:
        existing = create_package_model_defaults()
        module_path = cast(PythonPath, "my_package.models")
        model_default = create_model_default("Product")

        result = _update_symbol(existing, module_path, model_default)

        assert result.models_per_module_path[module_path].models == (model_default,)

    def test_adds_symbol_to_existing_module(self) -> None:
        module_path = cast(PythonPath, "my_package.models")
        existing_model = create_model_default("Customer")
        existing = PackageModelDefaults(
            models_per_module_path={
                module_path: ModelDefaults(models=(existing_model,))
            },
            primitives_per_type={},
        )
        new_model = create_model_default("Product")

        result = _update_symbol(existing, module_path, new_model)

        assert result.models_per_module_path[module_path].models == (
            existing_model,
            new_model,
        )

    def test_replaces_existing_symbol(self) -> None:
        module_path = cast(PythonPath, "my_package.models")
        old_model = create_model_default("Product")
        new_model = create_model_default("Product")
        other_model = create_model_default("Customer")
        existing = PackageModelDefaults(
            models_per_module_path={
                module_path: ModelDefaults(models=(old_model, other_model))
            },
            primitives_per_type={},
        )

        result = _update_symbol(existing, module_path, new_model)

        assert result.models_per_module_path[module_path].models == (
            new_model,
            other_model,
        )

    def test_removes_duplicate_symbol_entries(self) -> None:
        module_path = cast(PythonPath, "my_package.models")
        first = create_model_default("Product")
        second = create_model_default("Product")
        replacement = create_model_default("Product")
        existing = PackageModelDefaults(
            models_per_module_path={module_path: ModelDefaults(models=(first, second))},
            primitives_per_type={},
        )

        result = _update_symbol(existing, module_path, replacement)

        assert result.models_per_module_path[module_path].models == (replacement,)

    def test_does_not_mutate_existing_config(self) -> None:
        module_path = cast(PythonPath, "my_package.models")
        existing_model = create_model_default("Customer")
        existing = PackageModelDefaults(
            models_per_module_path={
                module_path: ModelDefaults(models=(existing_model,))
            },
            primitives_per_type={},
        )

        _update_symbol(
            existing,
            module_path,
            create_model_default("Product"),
        )

        assert existing.models_per_module_path[module_path].models == (existing_model,)


class TestSaveConfig:
    def test_returns_success_when_save_succeeds(
        self,
        mocker: MockerFixture,
    ) -> None:
        config_path = cast(FullPath, Path("/workspace/config.json"))
        config = create_package_model_defaults()

        save_mock = mocker.patch(
            "gyomu_test.helper.defaults.save.save_config",
            return_value=Success(None),
        )

        result = _save_config(config_path, config)

        assert isinstance(result, Success)
        request = save_mock.call_args.kwargs["request"]
        assert request.context == config_path
        assert save_mock.call_args.kwargs["value"] is config

    def test_returns_failure_when_save_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        config_path = cast(FullPath, Path("/workspace/config.json"))
        config_error = cast(ConfigError, Exception("write failed"))

        mocker.patch(
            "gyomu_test.helper.defaults.save.save_config",
            return_value=Failure(config_error),
        )

        result = _save_config(config_path, create_package_model_defaults())

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)


class TestSavePrimitiveParameterDefaultConfig:
    def test_saves_to_project_config(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_root = cast(WorkspaceRoot, Mock())
        project_context = cast(ProjectContext, Mock())
        primitive = create_primitive_default()
        config_path = cast(FullPath, Path("/project/.gyomu/config.json"))
        existing = create_package_model_defaults()
        updated = create_package_model_defaults()

        path_mock = mocker.patch(
            "gyomu_test.helper.defaults.save._get_project_config_path",
            return_value=config_path,
        )
        retrieve_mock = mocker.patch(
            "gyomu_test.helper.defaults.save._retrieve_existing_config",
            return_value=Success(existing),
        )
        update_mock = mocker.patch(
            "gyomu_test.helper.defaults.save._update_primitive",
            return_value=updated,
        )
        save_mock = mocker.patch(
            "gyomu_test.helper.defaults.save._save_config",
            return_value=Success(None),
        )

        result = save_primitive_parameter_default_config(
            workspace_root,
            project_context,
            primitive,
        )

        assert isinstance(result, Success)
        path_mock.assert_called_once_with(project_context=project_context)
        retrieve_mock.assert_called_once_with(config_path=config_path)
        update_mock.assert_called_once_with(
            existing_config=existing,
            primitive_default=primitive,
        )
        save_mock.assert_called_once_with(
            config_path=config_path,
            updated_config=updated,
        )

    def test_saves_to_workspace_config_when_project_context_is_none(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_root = cast(WorkspaceRoot, Mock())
        primitive = create_primitive_default()
        config_path = cast(FullPath, Path("/workspace/.gyomu/config.json"))

        mocker.patch(
            "gyomu_test.helper.defaults.save._get_workspace_config_path",
            return_value=config_path,
        )
        mocker.patch(
            "gyomu_test.helper.defaults.save._retrieve_existing_config",
            return_value=Success(create_package_model_defaults()),
        )
        mocker.patch(
            "gyomu_test.helper.defaults.save._update_primitive",
            return_value=create_package_model_defaults(),
        )
        save_mock = mocker.patch(
            "gyomu_test.helper.defaults.save._save_config",
            return_value=Success(None),
        )

        result = save_primitive_parameter_default_config(
            workspace_root,
            None,
            primitive,
        )

        assert isinstance(result, Success)
        save_mock.assert_called_once()
        assert save_mock.call_args.kwargs["config_path"] == config_path

    def test_stops_when_retrieval_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_root = cast(WorkspaceRoot, Mock())
        primitive = create_primitive_default()
        error = cast(GyomuTestError, Exception("read failed"))

        mocker.patch(
            "gyomu_test.helper.defaults.save._get_workspace_config_path",
            return_value=cast(FullPath, Path("/workspace/config.json")),
        )
        mocker.patch(
            "gyomu_test.helper.defaults.save._retrieve_existing_config",
            return_value=Failure(error),
        )
        update_mock = mocker.patch("gyomu_test.helper.defaults.save._update_primitive")
        save_mock = mocker.patch("gyomu_test.helper.defaults.save._save_config")

        result = save_primitive_parameter_default_config(
            workspace_root,
            None,
            primitive,
        )

        assert isinstance(result, Failure)
        update_mock.assert_not_called()
        save_mock.assert_not_called()


class TestSaveSymbolParameterDefaultConfig:
    def test_saves_to_project_config(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_root = cast(WorkspaceRoot, Mock())
        workspace_project = cast(WorkspaceProject, Mock())
        module_path = cast(PythonPath, "my_package.models")
        model_default = create_model_default("Product")
        config_path = cast(FullPath, Path("/project/.gyomu/config.json"))
        existing = create_package_model_defaults()
        updated = create_package_model_defaults()

        path_mock = mocker.patch(
            "gyomu_test.helper.defaults.save._get_project_config_path_from_workspace",
            return_value=config_path,
        )
        retrieve_mock = mocker.patch(
            "gyomu_test.helper.defaults.save._retrieve_existing_config",
            return_value=Success(existing),
        )
        update_mock = mocker.patch(
            "gyomu_test.helper.defaults.save._update_symbol",
            return_value=updated,
        )
        save_mock = mocker.patch(
            "gyomu_test.helper.defaults.save._save_config",
            return_value=Success(None),
        )

        result = save_symbol_parameter_default_config(
            workspace_root,
            workspace_project,
            module_path,
            model_default,
        )

        assert isinstance(result, Success)
        path_mock.assert_called_once_with(
            workspace_root=workspace_root,
            workspace_project=workspace_project,
        )
        retrieve_mock.assert_called_once_with(config_path=config_path)
        update_mock.assert_called_once_with(
            existing_config=existing,
            module_path=module_path,
            model_default=model_default,
        )
        save_mock.assert_called_once_with(
            config_path=config_path,
            updated_config=updated,
        )

    def test_saves_to_workspace_config_when_workspace_project_is_none(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_root = cast(WorkspaceRoot, Mock())
        module_path = cast(PythonPath, "my_package.models")
        model_default = create_model_default("Product")
        config_path = cast(FullPath, Path("/workspace/.gyomu/config.json"))

        mocker.patch(
            "gyomu_test.helper.defaults.save._get_workspace_config_path",
            return_value=config_path,
        )
        mocker.patch(
            "gyomu_test.helper.defaults.save._retrieve_existing_config",
            return_value=Success(create_package_model_defaults()),
        )
        mocker.patch(
            "gyomu_test.helper.defaults.save._update_symbol",
            return_value=create_package_model_defaults(),
        )
        save_mock = mocker.patch(
            "gyomu_test.helper.defaults.save._save_config",
            return_value=Success(None),
        )

        result = save_symbol_parameter_default_config(
            workspace_root,
            None,
            module_path,
            model_default,
        )

        assert isinstance(result, Success)
        save_mock.assert_called_once()
        assert save_mock.call_args.kwargs["config_path"] == config_path

    def test_stops_when_retrieval_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_root = cast(WorkspaceRoot, Mock())
        module_path = cast(PythonPath, "my_package.models")
        model_default = create_model_default("Product")
        error = cast(GyomuTestError, Exception("read failed"))

        mocker.patch(
            "gyomu_test.helper.defaults.save._get_workspace_config_path",
            return_value=cast(FullPath, Path("/workspace/config.json")),
        )
        mocker.patch(
            "gyomu_test.helper.defaults.save._retrieve_existing_config",
            return_value=Failure(error),
        )
        update_mock = mocker.patch("gyomu_test.helper.defaults.save._update_symbol")
        save_mock = mocker.patch("gyomu_test.helper.defaults.save._save_config")

        result = save_symbol_parameter_default_config(
            workspace_root,
            None,
            module_path,
            model_default,
        )

        assert isinstance(result, Failure)
        update_mock.assert_not_called()
        save_mock.assert_not_called()
