from pathlib import Path
from unittest.mock import Mock

from gyomu_python_analysis.resolve.models import ReferencedType
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_test.helper.inventory.update import update_helper_file
from pytest import MonkeyPatch
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import create_analysis_error
from packages.schema.test_support.helpers import (
    create_gyomu_io_error,
    create_model_default,
)
from packages.schema.test_support.testing_helpers import (
    create_helper_inventory_item,
)
from packages.test.tests.unit.helper.helpers import create_gyomu_test_error


class TestUpdateHelperFile:
    def test_returns_helper_file_path_when_update_succeeds(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        item = create_helper_inventory_item()
        model_default = create_model_default()
        referenced_types: tuple[ReferencedType, ...] = ()

        project_root = Path("/workspace")
        helper_file_absolute_path = project_root / "src/helpers.py"
        helper_file_path = ProjectRelativePath(Path("src/helpers.py"))

        workspace_context = Mock()
        workspace_context.root_project_context = Mock()
        workspace_context.root_project_context.project_root = project_root
        project_context = Mock()

        helper_file_analysis = Mock(source_lines=["from typing import Any\n", "\n"])
        get_helper_path = Mock(return_value=Success(helper_file_absolute_path))
        load_file = Mock(return_value=Success(helper_file_analysis))
        reflect_inventory = Mock(return_value=item)
        generate_function = Mock(
            return_value=["def create_test() -> Any:\n", "    ...\n"]
        )
        get_last_import = Mock(return_value=1)
        generate_import = Mock(return_value=["from example import Example\n"])
        write_file = Mock(return_value=Success(None))

        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.get_helper_file_path",
            get_helper_path,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.load_file_analysis_context",
            load_file,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.reflect_updated_inventory",
            reflect_inventory,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.generate_function_code_lines",
            generate_function,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.get_import_insertion_line",
            get_last_import,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.generate_import_code_lines",
            generate_import,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.write_text",
            write_file,
        )

        # Act
        result = update_helper_file(
            item=item,
            workspace_context=workspace_context,
            project_context=project_context,
            model_default=model_default,
            referenced_types=referenced_types,
        )

        # Assert
        assert result == Success(helper_file_path)

        get_helper_path.assert_called_once_with(
            model_identity=item.target_identity,
            project_context=project_context,
        )
        load_file.assert_called_once_with(
            workspace_context.root_project_context,
            helper_file_path,
        )
        reflect_inventory.assert_called_once_with(
            inventory=item,
            model_default=model_default,
        )
        generate_function.assert_called_once_with(item)
        get_last_import.assert_called_once_with(helper_file_analysis)
        generate_import.assert_called_once_with(item, referenced_types)
        write_file.assert_called_once_with(
            project_root / helper_file_path,
            "from typing import Any\n"
            "from example import Example\n"
            "def create_test() -> Any:\n"
            "    ...\n",
        )

    def test_returns_failure_when_helper_file_path_retrieval_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        item = create_helper_inventory_item()
        workspace_context = Mock()
        workspace_context.root_project_context = Mock()
        project_context = Mock()
        model_default = create_model_default()
        error = create_gyomu_test_error()
        get_helper_path = Mock(return_value=Failure(error))

        load_file = Mock()
        write_file = Mock()

        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.get_helper_file_path",
            get_helper_path,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.load_file_analysis_context",
            load_file,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.write_text",
            write_file,
        )

        # Act
        result = update_helper_file(
            item=item,
            workspace_context=workspace_context,
            project_context=project_context,
            model_default=model_default,
            referenced_types=(),
        )

        # Assert
        assert isinstance(result, Failure)
        get_helper_path.assert_called_once_with(
            model_identity=item.target_identity,
            project_context=project_context,
        )
        load_file.assert_not_called()
        write_file.assert_not_called()
        assert result.failure() is error

    def test_returns_failure_when_loading_helper_file_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        item = create_helper_inventory_item()
        project_root = Path("/workspace")
        helper_file_absolute_path = project_root / "src/helpers.py"
        helper_file_path = ProjectRelativePath(Path("src/helpers.py"))
        workspace_context = Mock()
        workspace_context.root_project_context = Mock()
        workspace_context.root_project_context.project_root = project_root
        project_context = Mock()
        get_helper_path = Mock(return_value=Success(helper_file_absolute_path))
        error = create_analysis_error()
        load_file = Mock(return_value=Failure(error))

        write_file = Mock()

        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.get_helper_file_path",
            get_helper_path,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.load_file_analysis_context",
            load_file,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.write_text",
            write_file,
        )

        # Act
        result = update_helper_file(
            item=item,
            workspace_context=workspace_context,
            project_context=project_context,
            model_default=create_model_default(),
            referenced_types=(),
        )

        # Assert
        assert isinstance(result, Failure)
        get_helper_path.assert_called_once_with(
            model_identity=item.target_identity,
            project_context=project_context,
        )
        load_file.assert_called_once_with(
            workspace_context.root_project_context,
            helper_file_path,
        )
        write_file.assert_not_called()
        assert result.failure().__cause__ == error

    def test_returns_failure_when_writing_helper_file_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        item = create_helper_inventory_item()
        project_root = Path("/workspace")
        helper_file_absolute_path = project_root / "src/helpers.py"
        # helper_file_path = ProjectRelativePath(Path("src/helpers.py"))
        workspace_context = Mock()
        workspace_context.root_project_context = Mock()
        workspace_context.root_project_context.project_root = project_root
        project_context = Mock()
        helper_file_analysis = Mock(source_lines=["from typing import Any\n", "\n"])

        get_helper_path = Mock(return_value=Success(helper_file_absolute_path))
        load_file = Mock(return_value=Success(helper_file_analysis))
        reflect_inventory = Mock(return_value=item)
        generate_function = Mock(
            return_value=["def create_test() -> Any:\n", "    ...\n"]
        )
        get_last_import = Mock(return_value=1)
        generate_import = Mock(return_value=["from example import Example\n"])
        error = create_gyomu_io_error()
        write_file = Mock(return_value=Failure(error))

        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.get_helper_file_path",
            get_helper_path,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.load_file_analysis_context",
            load_file,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.reflect_updated_inventory",
            reflect_inventory,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.generate_function_code_lines",
            generate_function,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.get_import_insertion_line",
            get_last_import,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.generate_import_code_lines",
            generate_import,
        )
        monkeypatch.setattr(
            "gyomu_test.helper.inventory.update.write_text",
            write_file,
        )

        # Act
        result = update_helper_file(
            item=item,
            workspace_context=workspace_context,
            project_context=project_context,
            model_default=create_model_default(),
            referenced_types=(),
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().__cause__ is error
