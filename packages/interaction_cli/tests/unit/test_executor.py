from pathlib import Path

from gyomu_interaction_cli.editor.protocol import VSCODE_SETTING
from gyomu_interaction_cli.executor import CliInteractionExecutor
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.schemas.interaction.request import (
    InteractionDirectRequest,
    InteractionDocumentRequest,
    InteractionRequest,
    InteractionSelectRequest,
    SelectionOption,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Result, Success


class StringCodec:
    def parse(
        self,
        raw_input: str,
        context: None,
    ) -> Success[str] | Failure[ValidationError]:
        if raw_input == "invalid":
            return Failure(ValidationError("Invalid value."))

        return Success(raw_input)


class PathCodec:
    def parse(
        self,
        document: Path,
        context: None,
    ) -> Result[str, ValidationError]:
        return Success("test")


class SelectProvider:
    def create_selections(
        self, context: None
    ) -> Result[tuple[SelectionOption[str], ...], GyomuError]:
        return Success((SelectionOption[str](label="label", value="value"),))


def create_direct_request() -> InteractionRequest[str, Path, None, str]:
    return InteractionDirectRequest(
        instruction="Enter a value",
        context=None,
        codec=StringCodec(),
    )


def create_selection_request() -> InteractionRequest[str, Path, None, str]:
    return InteractionSelectRequest(
        instruction="Enter a value", context=None, selection_provider=SelectProvider()
    )


class StringDocumentTextProvider:
    def create_initial_text(
        self,
        context: None,
    ) -> Result[str, GyomuError]:
        return Success("test")


def create_document_request(
    codec: PathCodec,
) -> InteractionRequest[str, Path, None, str]:
    return InteractionDocumentRequest(
        instruction="Enter a value",
        context=None,
        codec=codec,
        text_provider=StringDocumentTextProvider(),
    )


class TestCliInteractionExecutor:
    def test_accepts_valid_direct_input(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "gyomu_interaction_cli.direct.text",
        ).return_value.ask.return_value = "hello"
        mocker.patch(
            "gyomu_interaction_cli.direct.confirm_or_cancel",
            return_value=True,
        )

        executor = CliInteractionExecutor()

        result = executor.execute(create_direct_request())

        assert result == Success(InteractionAccepted("hello"))

    def test_accepts_valid_document_input(self, mocker: MockerFixture) -> None:
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
            return_value=Success(None),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.confirm_or_cancel",
            return_value=True,
        )

        executor = CliInteractionExecutor()

        result = executor.execute(create_document_request(codec=PathCodec()))

        assert result == Success(InteractionAccepted("test"))

    def test_retries_when_document_input_is_invalid(
        self,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "gyomu_interaction_cli.document.load_gyomu_config_section",
            return_value=Success(VSCODE_SETTING),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.create_initial_document",
            return_value=Success(Path("initial.json")),
        )
        open_document = mocker.patch(
            "gyomu_interaction_cli.document.open_document",
            return_value=Success(None),
        )
        mocker.patch(
            "gyomu_interaction_cli.document.confirm_or_cancel",
            side_effect=[True, True],
        )
        mocker.patch(
            "gyomu_interaction_cli.document.questionary_print",
        )

        codec = PathCodec()
        mocker.patch.object(
            codec,
            "parse",
            side_effect=[
                Failure(ValidationError("Invalid value.")),
                Success("hello"),
            ],
        )

        executor = CliInteractionExecutor()

        result = executor.execute(create_document_request(codec=codec))

        assert result == Success(InteractionAccepted("hello"))
        assert open_document.call_count == 2

    def test_accepts_selection_input(self, mocker: MockerFixture) -> None:
        expected = Success(InteractionAccepted("selected"))
        execute_selection = mocker.patch(
            "gyomu_interaction_cli.executor.execute_selection_interaction",
            return_value=expected,
        )

        request = create_selection_request()  # 既存のSelection用factoryを利用

        executor = CliInteractionExecutor()

        result = executor.execute(request)

        assert result == expected
        execute_selection.assert_called_once_with(request=request)
