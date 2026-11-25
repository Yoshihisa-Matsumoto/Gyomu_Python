from pathlib import Path
from unittest.mock import Mock, sentinel

from gyomu_schema.schemas.interaction.request import (
    InputMode,
    InteractionDocumentRequest,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
    InteractionCancelled,
)
from gyomu_schema.schemas.python.types import SymbolId
from gyomu_test.helper.defaults.requirements import ResolvedParameterDefault
from gyomu_workflow.test.helpers._internal.document import (
    ComplexValueProvider,
    _build_document_interaction_request,
    _build_necessary_import_lines,
    _build_variable_line,
    define_document_parameter,
)
from gyomu_workflow.test.helpers._internal.models import DefaultTypeParameterContext
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_literal_value_type,
    create_package_type,
    create_primitive_type,
    create_symbol_type,
)
from packages.schema.test_support.helpers import (
    create_class_analysis,
    create_gyomu_error,
    create_type_analysis,
    create_validation_error,
    simple_create_declaration_identity,
)
from packages.schema.test_support.testing_helpers import create_parameter_info
from packages.test.test_support.helpers import create_missing_parameter_default
from packages.workflow.test_support.helpers import create_default_type_parameter_context


class TestBuildNecessaryImportLines:
    def test_preserves_type_order(
        self,
    ) -> None:

        context: DefaultTypeParameterContext = create_default_type_parameter_context(
            parameter=create_missing_parameter_default(
                missing_types=(
                    create_package_type(symbol_id=SymbolId("package.a.b::Package")),
                    create_primitive_type(),
                    create_symbol_type(
                        symbol=create_class_analysis(
                            identity=simple_create_declaration_identity(
                                "symbol.b.c::Symbol"
                            )
                        )
                    ),
                    create_literal_value_type(),
                )
            )
        )
        assert _build_necessary_import_lines(context) == (
            "from package.a.b import Package",
            "from symbol.b.c import Symbol",
        )

    def test_without_missing_types(
        self,
    ) -> None:
        context: DefaultTypeParameterContext = create_default_type_parameter_context(
            parameter=create_missing_parameter_default(missing_types=())
        )
        assert _build_necessary_import_lines(context) == ()


class TestBuildVariableLine:
    def test_builds_parameter_name_and_type_annotation(self) -> None:
        context: DefaultTypeParameterContext = create_default_type_parameter_context(
            parameter=create_missing_parameter_default(
                parameter=create_parameter_info(
                    name="user_id", parameter_type=create_type_analysis(text="str")
                )
            )
        )

        assert _build_variable_line(context) == "user_id: str = "


class TestComplexValueProvider:
    class TestCreateInitialText:
        def test_create_initial_text_with_imports(self) -> None:
            context: DefaultTypeParameterContext = (
                create_default_type_parameter_context(
                    parameter=create_missing_parameter_default(
                        parameter=create_parameter_info(
                            name="user_id",
                            parameter_type=create_type_analysis(text="str"),
                        ),
                        missing_types=(
                            create_package_type(
                                symbol_id=SymbolId("package.a.b::Package")
                            ),
                            create_symbol_type(
                                symbol=create_class_analysis(
                                    identity=simple_create_declaration_identity(
                                        "symbol.b.c::Symbol"
                                    )
                                )
                            ),
                        ),
                    )
                )
            )

            result = ComplexValueProvider().create_initial_text(context)

            assert isinstance(result, Success)
            assert result.unwrap() == (
                "from package.a.b import Package\n"
                "from symbol.b.c import Symbol\n"
                "user_id: str = "
            )

        def test_create_initial_text_without_imports(self) -> None:
            context: DefaultTypeParameterContext = (
                create_default_type_parameter_context(
                    parameter=create_missing_parameter_default(
                        parameter=create_parameter_info(
                            name="user_id",
                            parameter_type=create_type_analysis(text="str"),
                        ),
                        missing_types=(),
                    )
                )
            )

            result = ComplexValueProvider().create_initial_text(context)

            assert isinstance(result, Success)
            assert result.unwrap() == "user_id: str = "

    class TestParse:
        def test_returns_validated_parameter(
            self,
            mocker,
            tmp_path: Path,
        ) -> None:
            context: DefaultTypeParameterContext = (
                create_default_type_parameter_context()
            )
            expected_parameter = sentinel.parameter
            validate_mock = mocker.patch(
                "gyomu_workflow.test.helpers._internal.document.validate_file_parameter",
                return_value=Success(expected_parameter),
            )

            result = ComplexValueProvider().parse(
                document=tmp_path / "parameter.py",
                context=context,
            )

            assert isinstance(result, Success)
            assert result.unwrap() is expected_parameter
            validate_mock.assert_called_once_with(
                file_path=tmp_path / "parameter.py",
                root_project_context=context.workspace_root_project_context,
                project_context=context.project_context,
                workspace_context=context.workspace_context,
                parameter_name=context.parameter.parameter.name,
            )

        def test_converts_validation_error(
            self,
            mocker,
            tmp_path: Path,
        ) -> None:
            context: DefaultTypeParameterContext = (
                create_default_type_parameter_context()
            )
            original_error = create_validation_error(
                message="invalid parameter",
                location=("parameter.py",),
            )
            mocker.patch(
                "gyomu_workflow.test.helpers._internal.document.validate_file_parameter",
                return_value=Failure(original_error),
            )

            result = ComplexValueProvider().parse(
                document=tmp_path / "parameter.py",
                context=context,
            )

            assert isinstance(result, Failure)
            error = result.failure()
            assert error.message == "fail to compute parameter"
            assert error.location == (str(tmp_path / "parameter.py"),)
            assert error.__cause__ is original_error


class TestBuildDocumentInteractionRequest:
    def test_builds_document_interaction_request(
        self,
        mocker,
        tmp_path: Path,
    ) -> None:
        context: DefaultTypeParameterContext = create_default_type_parameter_context()
        temporary_directory = tmp_path / "validation"
        prepare_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.document.prepare_directory",
            return_value=Success(temporary_directory),
        )

        result = _build_document_interaction_request(
            parameter_context=context,
        )

        assert isinstance(result, Success)
        request = result.unwrap()
        assert isinstance(request, InteractionDocumentRequest)
        assert request.instruction == "Please define your type parameter for "
        assert request.context is context
        assert request.input_mode == InputMode.DOCUMENT
        assert isinstance(request.temporary_directory, Path)
        assert request.temporary_directory == temporary_directory
        assert request.codec is request.text_provider
        prepare_mock.assert_called_once_with(project_context=context.project_context)

    def test_wraps_directory_preparation_failure(
        self,
        mocker,
    ) -> None:
        context: DefaultTypeParameterContext = create_default_type_parameter_context()
        original_error = create_gyomu_error(
            "directory preparation failed",
            operation="test",
            domain="test",
            reason="external_failure",
        )
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.document.prepare_directory",
            return_value=Failure(original_error),
        )

        result = _build_document_interaction_request(
            parameter_context=context,
        )

        assert isinstance(result, Failure)
        error = result.failure()
        assert error.message == "fail to prepare validation directory"
        assert error.__cause__ is original_error


class TestDefineDocumentParameter:
    def test_returns_executor_failure(
        self,
        mocker,
    ) -> None:
        context: DefaultTypeParameterContext = create_default_type_parameter_context()
        error = create_gyomu_error(
            "interaction failed",
            operation="test",
            domain="test",
            reason="external_failure",
        )
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.document._build_document_interaction_request",
            return_value=Success(sentinel.request),
        )
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.document.prepare_directory",
        )
        interaction = Mock()
        interaction.execute.return_value = Failure(error)

        result = define_document_parameter(
            parameter_context=context,
            interaction=interaction,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
        interaction.execute.assert_called_once_with(request=sentinel.request)

    def test_returns_resolved_parameter_default_when_accepted(
        self,
        mocker,
    ) -> None:
        context: DefaultTypeParameterContext = create_default_type_parameter_context()
        parameter = context.parameter.parameter
        expected_value = sentinel.value
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.document._build_document_interaction_request",
            return_value=Success(sentinel.request),
        )
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.document.save_symbol_type_parameter_default_in_workspace",
            return_value=Success(None),
        )
        interaction = Mock()
        interaction.execute.return_value = Success(
            InteractionAccepted(value=expected_value)
        )

        result = define_document_parameter(
            parameter_context=context,
            interaction=interaction,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == ResolvedParameterDefault(
            parameter=parameter, default=expected_value, referenced_types=()
        )
        interaction.execute.assert_called_once_with(request=sentinel.request)

    def test_returns_failure_when_cancelled(
        self,
        mocker,
    ) -> None:
        context: DefaultTypeParameterContext = create_default_type_parameter_context()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.document._build_document_interaction_request",
            return_value=Success(sentinel.request),
        )
        interaction = Mock()
        interaction.execute.return_value = Success(InteractionCancelled())

        result = define_document_parameter(
            parameter_context=context,
            interaction=interaction,
        )

        assert isinstance(result, Failure)
        error = result.failure()
        assert error.message == "parameter was not defined by user"
        assert error.operation == "test"
        assert error.domain == "test"
        assert error.reason == "external_failure"
        interaction.execute.assert_called_once_with(request=sentinel.request)
