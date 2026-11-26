from pathlib import Path

from gyomu_infra.process.error import ProcessError
from gyomu_interaction_cli.document import (
    create_initial_document,
    execute_document_interaction,
    open_document,
)
from gyomu_interaction_cli.editor.protocol import VSCODE_SETTING
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.interaction.request import InteractionDocumentRequest
from gyomu_schema.schemas.interaction.result import InteractionCancelled
from returns.result import Failure, Success

from packages.schema.test_support.helpers import create_gyomu_io_error


class TestCreateInitialDocument:
    def test_creates_temp_file_and_writes_initial_text(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        temporary_directory = tmp_path / "validation-workspace"
        temp_file = temporary_directory / "initial.json"
        initial_text = '{"name": "example"}'

        create_temp_file = mocker.patch(
            "gyomu_interaction_cli.document.create_temp_file",
            return_value=Success(temp_file),
        )
        write_text = mocker.patch(
            "gyomu_interaction_cli.document.write_text",
            return_value=Success(None),
        )

        result = create_initial_document(
            initial_text=initial_text,
            temporary_directory=temporary_directory,
            temporary_file_extension=None,
        )

        assert result == Success(temp_file)
        create_temp_file.assert_called_once_with(
            temporary_directory=temporary_directory, extension=None
        )
        write_text.assert_called_once_with(
            path=temp_file,
            content=initial_text,
        )

    def test_returns_failure_when_temp_file_creation_fails(
        self,
        mocker,
    ) -> None:
        error = create_gyomu_io_error()
        create_temp_file = mocker.patch(
            "gyomu_interaction_cli.document.create_temp_file",
            return_value=Failure(error),
        )
        write_text = mocker.patch(
            "gyomu_interaction_cli.document.write_text",
        )

        result = create_initial_document(
            initial_text="initial",
            temporary_directory=None,
            temporary_file_extension=None,
        )

        assert isinstance(result, Failure)
        create_temp_file.assert_called_once_with(
            temporary_directory=None, extension=None
        )
        write_text.assert_not_called()

    def test_returns_failure_when_initial_text_write_fails(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        temp_file = tmp_path / "initial.json"
        error = create_gyomu_io_error()
        mocker.patch(
            "gyomu_interaction_cli.document.create_temp_file",
            return_value=Success(temp_file),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.write_text",
            return_value=Failure(error),
        )
        delete_file = mocker.patch(
            "gyomu_interaction_cli.document.delete_file",
            return_value=Success(None),
        )

        result = create_initial_document(
            initial_text="initial",
            temporary_directory=None,
            temporary_file_extension=None,
        )

        assert isinstance(result, Failure)
        delete_file.assert_called_once_with(temp_file)

    def test_preserves_write_error_when_temp_file_deletion_raises(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        temp_file = tmp_path / "initial.json"
        write_error = create_gyomu_io_error()

        mocker.patch(
            "gyomu_interaction_cli.document.create_temp_file",
            return_value=Success(temp_file),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.write_text",
            return_value=Failure(write_error),
        )
        delete_file = mocker.patch(
            "gyomu_interaction_cli.document.delete_file",
            side_effect=OSError("Failed to delete temporary file."),
        )

        result = create_initial_document(
            initial_text="initial",
            temporary_directory=None,
            temporary_file_extension=None,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuError)
        assert result.failure().__cause__ is not None
        delete_file.assert_called_once_with(temp_file)


class TestOpenDocument:
    def test_success(self, mocker, tmp_path: Path) -> None:
        execute_background = mocker.patch(
            "gyomu_interaction_cli.document.execute_background",
            return_value=Success(None),
        )

        file_path = tmp_path / "example.json"

        result = open_document(
            command="code --reuse-window --wait ##FILENAME##",
            file_path=file_path,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

        execute_background.assert_called_once_with(
            command=[
                "code",
                "--reuse-window",
                "--wait",
                str(file_path),
            ],
        )

    def test_fails_when_editor_cannot_be_started(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        process_error = ProcessError(
            "editor not found",
            command=("editor-that-does-not-exist",),
            exit_code=None,
            details={"exception": "FileNotFoundError"},
        )
        mocker.patch(
            "gyomu_interaction_cli.document.execute_background",
            return_value=Failure(process_error),
        )

        result = open_document(
            command="editor-that-does-not-exist ##FILENAME##",
            file_path=tmp_path / "example.json",
        )

        assert isinstance(result, Failure)

        error = result.failure()
        assert isinstance(error, GyomuError)

    def test_returns_failure_when_editor_command_is_invalid(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        execute_background = mocker.patch(
            "gyomu_interaction_cli.document.execute_background",
        )

        result = open_document(
            command='code "unterminated',
            file_path=tmp_path / "example.json",
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuError)
        execute_background.assert_not_called()


class TestExecuteDocumentInteraction:
    def test_returns_failure_when_editor_cannot_be_opened(
        self,
        mocker,
    ) -> None:
        from gyomu_schema.error.gyomu import GyomuError
        from gyomu_schema.schemas.interaction.request import (
            InteractionDocumentRequest,
        )
        from returns.result import Failure

        error = GyomuError(
            message="editor failed",
            operation="document interaction",
            domain="interaction",
            reason="external_failure",
        )

        mocker.patch(
            "gyomu_interaction_cli.document.load_gyomu_config_section",
            return_value=Success(VSCODE_SETTING),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.create_initial_document",
            return_value=Success(Path("initial.json")),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.open_document",
            return_value=Failure(error),
        )
        delete_file = mocker.patch(
            "gyomu_interaction_cli.document.delete_file",
            return_value=Success(None),
        )

        request = mocker.Mock(spec=InteractionDocumentRequest)
        request.context = mocker.sentinel.context
        request.text_provider = mocker.Mock()
        request.text_provider.create_initial_text.return_value = Success(
            '{"name": "example"}'
        )
        input_func = mocker.Mock()

        result = execute_document_interaction(
            request,
        )

        assert isinstance(result, Failure)
        input_func.assert_not_called()
        delete_file.assert_called_once_with(Path("initial.json"))

        result_error = result.failure()
        assert isinstance(result_error, GyomuError)
        assert result_error.message == error.message

    def test_returns_cancelled_when_user_cancels(
        self,
        mocker,
    ) -> None:
        from gyomu_schema.schemas.interaction.result import InteractionCancelled

        temp_file = Path("initial.json")
        mocker.patch(
            "gyomu_interaction_cli.document.load_gyomu_config_section",
            return_value=Success(VSCODE_SETTING),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.create_initial_document",
            return_value=Success(temp_file),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.open_document",
            return_value=Success(None),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.confirm_or_cancel",
            return_value=False,
        )
        delete_file = mocker.patch(
            "gyomu_interaction_cli.document.delete_file",
            return_value=Success(None),
        )

        request = mocker.Mock(spec=InteractionDocumentRequest)
        request.context = mocker.sentinel.context
        request.text_provider = mocker.Mock()
        request.text_provider.create_initial_text.return_value = Success(
            '{"name": "example"}'
        )

        result = execute_document_interaction(
            request,
        )

        assert isinstance(result, Success)
        assert isinstance(result.unwrap(), InteractionCancelled)
        delete_file.assert_called_once_with(temp_file)

    def test_returns_accepted_when_user_confirms_valid_input(
        self,
        mocker,
    ) -> None:
        from gyomu_schema.schemas.interaction.result import InteractionAccepted

        temp_file = Path("initial.json")
        expected_value = mocker.sentinel.parsed_value

        mocker.patch(
            "gyomu_interaction_cli.document.load_gyomu_config_section",
            return_value=Success(VSCODE_SETTING),
        )
        create_initial_document = mocker.patch(
            "gyomu_interaction_cli.document.create_initial_document",
            return_value=Success(temp_file),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.open_document",
            return_value=Success(None),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.confirm_or_cancel",
            return_value=True,
        )
        request = mocker.Mock(spec=InteractionDocumentRequest)
        request.context = mocker.sentinel.context
        request.temporary_directory = Path("temporally-path")
        request.temporary_file_extension = "py"

        request.text_provider = mocker.Mock()
        request.text_provider.create_initial_text.return_value = Success(
            '{"name": "example"}'
        )

        request.codec = mocker.Mock()
        request.codec.parse.return_value = Success(expected_value)
        delete_file = mocker.patch(
            "gyomu_interaction_cli.document.delete_file",
            return_value=Success(None),
        )

        result = execute_document_interaction(
            request,
        )

        assert isinstance(result, Success)
        result_value = result.unwrap()
        assert isinstance(result_value, InteractionAccepted)
        assert result_value.value == expected_value
        delete_file.assert_called_once_with(temp_file)

        create_initial_document.assert_called_once_with(
            initial_text='{"name": "example"}',
            temporary_directory=Path("temporally-path"),
            temporary_file_extension=request.temporary_file_extension,
        )

        request.text_provider.create_initial_text.assert_called_once_with(
            context=request.context,
        )
        request.codec.parse.assert_called_once_with(
            temp_file,
            request.context,
        )

    def test_reopens_same_file_when_input_is_invalid(
        self,
        mocker,
    ) -> None:
        from gyomu_schema.schemas.interaction.result import InteractionAccepted

        temp_file = Path("initial.json")
        expected_value = mocker.sentinel.parsed_value

        mocker.patch(
            "gyomu_interaction_cli.document.load_gyomu_config_section",
            return_value=Success(VSCODE_SETTING),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.create_initial_document",
            return_value=Success(temp_file),
        )
        open_document = mocker.patch(
            "gyomu_interaction_cli.document.open_document",
            side_effect=[Success(None), Success(None)],
        )
        mocker.patch(
            "gyomu_interaction_cli.document.confirm_or_cancel",
            side_effect=[True, True],
        )
        delete_file = mocker.patch(
            "gyomu_interaction_cli.document.delete_file",
            return_value=Success(None),
        )

        request = mocker.Mock(spec=InteractionDocumentRequest)
        request.context = mocker.sentinel.context
        request.text_provider = mocker.Mock()
        request.text_provider.create_initial_text.return_value = Success(
            '{"name": "example"}'
        )
        request.codec = mocker.Mock()
        request.codec.parse.side_effect = [
            Failure(ValueError("invalid input")),
            Success(expected_value),
        ]

        result = execute_document_interaction(
            request,
        )

        assert isinstance(result, Success)
        result_value = result.unwrap()
        assert isinstance(result_value, InteractionAccepted)
        assert result_value.value == expected_value

        assert open_document.call_count == 2
        assert all(
            call.kwargs["file_path"] == temp_file
            for call in open_document.call_args_list
        )
        assert request.codec.parse.call_count == 2
        delete_file.assert_called_once_with(temp_file)

    def test_prints_error_when_input_is_invalid(
        self,
        mocker,
    ) -> None:
        temp_file = Path("initial.json")
        validation_error = ValueError("invalid input")

        mocker.patch(
            "gyomu_interaction_cli.document.load_gyomu_config_section",
            return_value=Success(VSCODE_SETTING),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.create_initial_document",
            return_value=Success(temp_file),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.open_document",
            side_effect=[Success(None), Success(None)],
        )
        mocker.patch(
            "gyomu_interaction_cli.document.confirm_or_cancel",
            side_effect=[True, False],
        )
        delete_file = mocker.patch(
            "gyomu_interaction_cli.document.delete_file",
            return_value=Success(None),
        )

        request = mocker.Mock(spec=InteractionDocumentRequest)
        request.context = mocker.sentinel.context
        request.text_provider = mocker.Mock()
        request.text_provider.create_initial_text.return_value = Success("initial text")
        request.codec = mocker.Mock()
        request.codec.parse.return_value = Failure(validation_error)
        mocker.patch(
            "gyomu_interaction_cli.document.questionary_print",
        )
        result = execute_document_interaction(
            request,
        )

        assert isinstance(result, Success)
        assert isinstance(result.unwrap(), InteractionCancelled)

        assert request.codec.parse.call_count == 1
        delete_file.assert_called_once_with(temp_file)

    def test_returns_cancelled_when_temp_file_deletion_fails(
        self,
        mocker,
    ) -> None:
        temp_file = Path("initial.json")

        mocker.patch(
            "gyomu_interaction_cli.document.load_gyomu_config_section",
            return_value=Success(VSCODE_SETTING),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.create_initial_document",
            return_value=Success(temp_file),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.open_document",
            return_value=Success(None),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.confirm_or_cancel",
            return_value=False,
        )
        delete_file = mocker.patch(
            "gyomu_interaction_cli.document.delete_file",
            return_value=Failure(
                GyomuError(
                    message="Failed to delete temporary file.",
                    operation="document interaction",
                    domain="interaction",
                    reason="external_failure",
                )
            ),
        )

        request = mocker.Mock(spec=InteractionDocumentRequest)
        request.context = mocker.sentinel.context
        request.text_provider = mocker.Mock()
        request.text_provider.create_initial_text.return_value = Success("initial text")

        result = execute_document_interaction(
            request,
        )

        assert isinstance(result, Success)
        assert isinstance(result.unwrap(), InteractionCancelled)
        delete_file.assert_called_once_with(temp_file)

    def test_returns_failure_when_initial_text_creation_fails(
        self,
        mocker,
    ) -> None:
        from gyomu_schema.error.gyomu import GyomuError

        error = GyomuError(
            message="Failed to create initial text.",
            operation="document interaction",
            domain="interaction",
            reason="external_failure",
        )

        mocker.patch(
            "gyomu_interaction_cli.document.load_gyomu_config_section",
            return_value=Success(VSCODE_SETTING),
        )

        request = mocker.Mock(spec=InteractionDocumentRequest)
        request.context = mocker.sentinel.context
        request.text_provider = mocker.Mock()
        request.text_provider.create_initial_text.return_value = Failure(error)

        create_initial_document = mocker.patch(
            "gyomu_interaction_cli.document.create_initial_document",
        )
        open_document = mocker.patch(
            "gyomu_interaction_cli.document.open_document",
        )
        delete_file = mocker.patch(
            "gyomu_interaction_cli.document.delete_file",
        )

        result = execute_document_interaction(
            request,
        )

        assert isinstance(result, Failure)
        create_initial_document.assert_not_called()
        open_document.assert_not_called()
        delete_file.assert_not_called()
        assert result.failure() is error

    def test_returns_failure_when_initial_document_creation_fails(
        self,
        mocker,
    ) -> None:
        from gyomu_schema.error.gyomu import GyomuError

        error = GyomuError(
            message="Failed to create initial document.",
            operation="document interaction",
            domain="interaction",
            reason="external_failure",
        )

        mocker.patch(
            "gyomu_interaction_cli.document.load_gyomu_config_section",
            return_value=Success(VSCODE_SETTING),
        )

        request = mocker.Mock(spec=InteractionDocumentRequest)
        request.context = mocker.sentinel.context
        request.text_provider = mocker.Mock()
        request.text_provider.create_initial_text.return_value = Success("initial text")

        mocker.patch(
            "gyomu_interaction_cli.document.create_initial_document",
            return_value=Failure(error),
        )
        open_document = mocker.patch(
            "gyomu_interaction_cli.document.open_document",
        )
        delete_file = mocker.patch(
            "gyomu_interaction_cli.document.delete_file",
        )

        result = execute_document_interaction(
            request,
        )

        assert isinstance(result, Failure)
        open_document.assert_not_called()
        delete_file.assert_not_called()

    def test_calls_confirm_or_cancel_without_arguments(
        self,
        mocker,
    ) -> None:
        # Arrange
        temp_file = Path("initial.json")
        mocker.patch(
            "gyomu_interaction_cli.document.load_gyomu_config_section",
            return_value=Success(VSCODE_SETTING),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.create_initial_document",
            return_value=Success(temp_file),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.open_document",
            return_value=Success(None),
        )
        confirm_or_cancel = mocker.patch(
            "gyomu_interaction_cli.document.confirm_or_cancel",
            return_value=False,
        )
        mocker.patch(
            "gyomu_interaction_cli.document.delete_file",
            return_value=Success(None),
        )

        request = mocker.Mock(spec=InteractionDocumentRequest)
        request.context = mocker.sentinel.context
        request.text_provider = mocker.Mock()
        request.text_provider.create_initial_text.return_value = Success("initial text")

        # Act
        result = execute_document_interaction(request)

        # Assert
        assert isinstance(result, Success)
        assert isinstance(result.unwrap(), InteractionCancelled)
        confirm_or_cancel.assert_called_once_with()

    def test_returns_failure_when_editor_config_loading_fails(
        self,
        mocker,
    ) -> None:
        from gyomu_schema.error.gyomu import GyomuError

        error = GyomuError(
            message="Failed to load editor config.",
            operation="document interaction",
            domain="interaction",
            reason="external_failure",
        )

        mocker.patch(
            "gyomu_interaction_cli.document.load_gyomu_config_section",
            return_value=Failure(error),
        )

        request = mocker.Mock(spec=InteractionDocumentRequest)
        request.context = mocker.sentinel.context
        request.text_provider = mocker.Mock()

        create_initial_document = mocker.patch(
            "gyomu_interaction_cli.document.create_initial_document",
        )
        open_document = mocker.patch(
            "gyomu_interaction_cli.document.open_document",
        )
        delete_file = mocker.patch(
            "gyomu_interaction_cli.document.delete_file",
        )

        result = execute_document_interaction(
            request,
        )

        assert isinstance(result, Failure)
        create_initial_document.assert_not_called()
        open_document.assert_not_called()
        delete_file.assert_not_called()
        request.text_provider.create_initial_text.assert_not_called()

    def test_preserves_cancelled_result_when_temp_file_deletion_raises(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        temp_file = tmp_path / Path("dummy-file.json")
        mocker.patch(
            "gyomu_interaction_cli.document.load_gyomu_config_section",
            return_value=Success(VSCODE_SETTING),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.create_initial_document",
            return_value=Success(temp_file),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.open_document",
            return_value=Success(None),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.confirm_or_cancel",
            return_value=False,
        )
        delete_file = mocker.patch(
            "gyomu_interaction_cli.document.delete_file",
            return_value=Failure(
                create_gyomu_io_error(message="Failed to delete temporary file.")
            ),
        )

        request = mocker.Mock(spec=InteractionDocumentRequest)
        request.context = mocker.sentinel.context
        request.text_provider = mocker.Mock()
        request.text_provider.create_initial_text.return_value = Success("initial text")
        request.temporary_directory = tmp_path

        result = execute_document_interaction(
            request,
        )

        assert isinstance(result, Success)
        assert isinstance(result.unwrap(), InteractionCancelled)
        delete_file.assert_called_once_with(temp_file)
