from io import StringIO
from pathlib import Path
from unittest.mock import Mock

from gyomu_interaction_cli.editor.protocol import VSCODE_SETTING
from gyomu_interaction_cli.executor import CliInteractionExecutor
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.schemas.interaction.request import (
    InteractionDirectRequest,
    InteractionDocumentRequest,
    InteractionRequest,
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


def create_direct_request() -> InteractionRequest[str, Path, None, str]:
    return InteractionDirectRequest(
        instruction="Enter a value",
        context=None,
        codec=StringCodec(),
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
    def test_accepts_valid_direct_input(self) -> None:
        input_func = Mock(side_effect=["hello", "y"])
        output = StringIO()
        executor = CliInteractionExecutor(
            input_func=input_func,
            output=output,
        )

        result = executor.execute(create_direct_request())

        assert result == Success(InteractionAccepted("hello"))
        assert input_func.call_count == 2
        assert output.getvalue() == ""

    def test_accepts_valid_document_input(self, mocker: MockerFixture) -> None:
        input_func = Mock(side_effect=["y"])
        output = StringIO()
        executor = CliInteractionExecutor(
            input_func=input_func,
            output=output,
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
            return_value=Success(None),
        )
        # mocker.patch(
        #     "gyomu_interaction_cli.document.read_text",
        #     return_value=Success("hello"),
        # )

        result = executor.execute(create_document_request(codec=PathCodec()))

        assert result == Success(InteractionAccepted("test"))
        assert input_func.call_count == 1
        assert output.getvalue() == ""

    def test_retries_when_document_input_is_invalid(
        self, mocker: MockerFixture
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
        codec = PathCodec()
        mocker.patch.object(
            codec,
            "parse",
            side_effect=[
                Failure(ValidationError("Invalid value.")),
                Success("hello"),
            ],
        )

        # confirm_or_cancel は、1回目は確定、2回目も確定する想定
        # input_func の呼び出し回数は confirm_or_cancel の実装に合わせる
        input_func = Mock(side_effect=["y", "y"])
        output = StringIO()
        executor = CliInteractionExecutor(
            input_func=input_func,
            output=output,
        )

        result = executor.execute(create_document_request(codec=codec))

        assert result == Success(InteractionAccepted("hello"))
        assert input_func.call_count == 2
        assert output.getvalue() == "Invalid input: Invalid value.\n"
        assert open_document.call_count == 2
