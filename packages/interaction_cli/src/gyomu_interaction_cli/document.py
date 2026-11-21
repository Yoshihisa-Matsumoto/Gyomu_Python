import contextlib
import shlex
from pathlib import Path

from gyomu_config.gyomu.load import load_gyomu_config_section
from gyomu_infra.filesystem.file_io import (
    create_temp_file,
    delete_file,
    write_text,
)
from gyomu_infra.logger import logger
from gyomu_infra.process.executor import execute_background
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.interaction.request import InteractionDocumentRequest
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
    InteractionCancelled,
    InteractionResult,
)
from questionary import print as questionary_print
from returns.result import Failure, Result, Success

from gyomu_interaction_cli.confirm import confirm_or_cancel
from gyomu_interaction_cli.editor.protocol import (
    VSCODE_SETTING,
    TextEditorConfig,
)


def _wrap_gyomu_error(error: BaseException, message: str) -> GyomuError:
    return GyomuError(
        message=message,
        operation="document interaction",
        domain="interaction",
        reason="external_failure",
    ).chain(error)


def create_initial_document(
    initial_text: str, temporary_directory: Path | None
) -> Result[Path, GyomuError]:
    """Create a temporary document and write its initial text."""

    temp_file_result = create_temp_file(temporary_directory=temporary_directory)
    if isinstance(temp_file_result, Failure):
        return Failure(
            _wrap_gyomu_error(
                error=temp_file_result.failure(),
                message="fail to create temp file",
            )
        )

    temp_file = temp_file_result.unwrap()

    write_result = write_text(
        path=temp_file,
        content=initial_text,
    )
    if isinstance(write_result, Failure):
        with contextlib.suppress(OSError):
            delete_file(temp_file)

        return Failure(
            _wrap_gyomu_error(
                error=write_result.failure(),
                message="fail to write temp file",
            )
        )

    return Success(temp_file)


def open_document(command: str, file_path: Path) -> Result[None, GyomuError]:
    try:
        arguments = shlex.split(command)
    except ValueError as error:
        return Failure(
            _wrap_gyomu_error(
                error=error,
                message="fail to parse editor command",
            )
        )

    arguments = [
        argument.replace("##FILENAME##", str(file_path)) for argument in arguments
    ]

    result = execute_background(command=arguments)
    if isinstance(result, Failure):
        return result.alt(
            lambda error: _wrap_gyomu_error(
                error=error,
                message="fail to execute opening file",
            )
        )

    return Success(None)


def execute_document_interaction[ContextT, ValueT](
    request: InteractionDocumentRequest[Path, ContextT, ValueT],
) -> Result[InteractionResult[ValueT], GyomuError]:
    config_result = load_gyomu_config_section(
        section_name="test.interaction-cli.text-editor",
        model_type=TextEditorConfig,
        default=VSCODE_SETTING,
    )
    if isinstance(config_result, Failure):
        return config_result.alt(
            lambda error: _wrap_gyomu_error(
                error=error,
                message="fail to load config",
            )
        )

    text_result = request.text_provider.create_initial_text(
        context=request.context,
    )
    if isinstance(text_result, Failure):
        return text_result

    document_result = create_initial_document(
        initial_text=text_result.unwrap(),
        temporary_directory=request.temporary_directory,
    )
    if isinstance(document_result, Failure):
        return document_result

    temp_file = document_result.unwrap()

    try:
        while True:
            open_result = open_document(
                command=config_result.unwrap().command,
                file_path=temp_file,
            )
            if isinstance(open_result, Failure):
                return open_result

            confirmed = confirm_or_cancel()
            if not confirmed:
                return Success(InteractionCancelled())

            parsed = request.codec.parse(
                temp_file,
                request.context,
            )
            if isinstance(parsed, Failure):
                questionary_print(f"Invalid input: {parsed.failure()}")
                continue

            return Success(InteractionAccepted(parsed.unwrap()))
    finally:
        delete_result = delete_file(temp_file)
        if isinstance(delete_result, Failure):
            logger.warning(
                "Failed to delete temporary document: %s",
                delete_result.failure(),
            )
