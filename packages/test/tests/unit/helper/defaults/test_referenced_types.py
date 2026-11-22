from gyomu_python_analysis.resolve.models import ReferencedType
from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.defaults.referenced_types import (
    aggregate_referenced_types,
    deduplicate_referenced_types,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_package_type,
    create_resolve_error,
    create_symbol_type,
    create_workspace_context,
)
from packages.schema.test_support.helpers import (
    create_argument,
    create_arguments,
    create_attribute_parameter,
    create_call_parameter,
    create_dict_entry,
    create_dict_parameter,
    create_keyword_argument,
    create_lambda_parameter,
    create_list_parameter,
    create_name_parameter,
    create_tuple_parameter,
)


class TestDeduplicateReferencedTypes:
    def test_keeps_referenced_types_with_different_symbol_ids(self) -> None:
        first = create_symbol_type()
        second = create_package_type()

        result = deduplicate_referenced_types([first, second])

        assert result == (first, second)

    def test_keeps_first_referenced_type_when_symbol_ids_are_duplicated(self) -> None:
        first = create_symbol_type()
        duplicate = create_symbol_type()

        result = deduplicate_referenced_types([first, duplicate])

        assert len(result) == 1
        assert result[0] is first

    def test_keeps_first_package_type_when_symbol_ids_are_duplicated(self) -> None:
        first = create_package_type()
        duplicate = create_package_type(
            symbol_id=first.symbol_id,
        )

        result = deduplicate_referenced_types([first, duplicate])

        assert len(result) == 1
        assert result[0] is first


class TestAggregateReferencedTypes:
    def test_returns_existing_referenced_types_when_parameter_has_no_references(
        self,
        mocker: MockerFixture,
    ) -> None:
        parameter = create_name_parameter()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        workspace_context = create_workspace_context()

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert result == Success((existing,))
        assert referenced_types == [existing]

    def test_collects_referenced_types_from_call_parameter(
        self,
        mocker: MockerFixture,
    ) -> None:
        parameter = create_call_parameter()
        symbol_type = create_symbol_type()
        package_type = create_package_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Success((symbol_type, package_type)),
        )

        referenced_types: list[ReferencedType] = []

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert result == Success((symbol_type, package_type))
        assert referenced_types == [symbol_type, package_type]
        resolve_identity.assert_called_once_with(
            identity=parameter.callable_identity,
            workspace_context=workspace_context,
        )

    def test_returns_failure_when_call_parameter_identity_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        parameter = create_call_parameter()
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_collects_referenced_types_from_attribute_parameter(
        self,
        mocker: MockerFixture,
    ) -> None:
        call_parameter = create_call_parameter()
        parameter = create_attribute_parameter(value=call_parameter)
        symbol_type = create_symbol_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Success((symbol_type,)),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((symbol_type,))
        resolve_identity.assert_called_once_with(
            identity=call_parameter.callable_identity,
            workspace_context=workspace_context,
        )

    def test_collects_referenced_types_from_call_parameter_args(
        self,
        mocker: MockerFixture,
    ) -> None:
        arg_parameter = create_call_parameter()
        parameter = create_call_parameter(args=(arg_parameter,))
        callable_type = create_symbol_type()
        arg_type = create_package_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            side_effect=[
                Success((callable_type,)),
                Success((arg_type,)),
            ],
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((callable_type, arg_type))
        assert resolve_identity.call_count == 2

    def test_collects_referenced_types_from_call_parameter_kwargs(
        self,
        mocker: MockerFixture,
    ) -> None:
        kwarg_parameter = create_call_parameter()
        parameter = create_call_parameter(
            kwargs=(create_keyword_argument(value=kwarg_parameter),),
        )
        callable_type = create_symbol_type()
        kwarg_type = create_package_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            side_effect=[
                Success((callable_type,)),
                Success((kwarg_type,)),
            ],
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((callable_type, kwarg_type))
        assert resolve_identity.call_count == 2

    def test_collects_referenced_types_from_dict_parameter(
        self,
        mocker: MockerFixture,
    ) -> None:
        key_parameter = create_call_parameter()
        value_parameter = create_call_parameter()
        parameter = create_dict_parameter(
            entries=(create_dict_entry(key=key_parameter, value=value_parameter),),
        )
        key_type = create_symbol_type()
        value_type = create_package_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            side_effect=[
                Success((key_type,)),
                Success((value_type,)),
            ],
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((key_type, value_type))
        assert resolve_identity.call_count == 2

    def test_collects_referenced_types_from_tuple_parameter(
        self,
        mocker: MockerFixture,
    ) -> None:
        first_element = create_call_parameter()
        second_element = create_call_parameter()
        parameter = create_tuple_parameter(elements=(first_element, second_element))
        first_type = create_symbol_type()
        second_type = create_package_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            side_effect=[
                Success((first_type,)),
                Success((second_type,)),
            ],
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((first_type, second_type))
        assert resolve_identity.call_count == 2

    def test_collects_referenced_types_from_list_parameter(
        self,
        mocker: MockerFixture,
    ) -> None:
        first_element = create_call_parameter()
        second_element = create_call_parameter()
        parameter = create_list_parameter(elements=(first_element, second_element))
        first_type = create_symbol_type()
        second_type = create_package_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            side_effect=[
                Success((first_type,)),
                Success((second_type,)),
            ],
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((first_type, second_type))
        assert resolve_identity.call_count == 2

    def test_collects_referenced_types_from_lambda_body(
        self,
        mocker: MockerFixture,
    ) -> None:
        body_parameter = create_call_parameter()
        parameter = create_lambda_parameter(body=body_parameter)
        symbol_type = create_symbol_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Success((symbol_type,)),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((symbol_type,))
        resolve_identity.assert_called_once_with(
            identity=body_parameter.callable_identity,
            workspace_context=workspace_context,
        )

    def test_collects_referenced_types_from_lambda_posonlyarg_annotation(
        self,
        mocker: MockerFixture,
    ) -> None:
        annotation = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                posonlyargs=(create_argument(annotation=annotation),),
            ),
        )
        symbol_type = create_symbol_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Success((symbol_type,)),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((symbol_type,))
        resolve_identity.assert_called_once_with(
            identity=annotation.callable_identity,
            workspace_context=workspace_context,
        )

    def test_collects_referenced_types_from_lambda_arg_annotation(
        self,
        mocker: MockerFixture,
    ) -> None:
        annotation = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                args=(create_argument(annotation=annotation),),
            ),
        )
        symbol_type = create_symbol_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Success((symbol_type,)),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((symbol_type,))
        resolve_identity.assert_called_once_with(
            identity=annotation.callable_identity,
            workspace_context=workspace_context,
        )

    def test_collects_referenced_types_from_lambda_vararg_annotation(
        self,
        mocker: MockerFixture,
    ) -> None:
        annotation = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                vararg=create_argument(annotation=annotation),
            ),
        )
        symbol_type = create_symbol_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Success((symbol_type,)),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((symbol_type,))
        resolve_identity.assert_called_once_with(
            identity=annotation.callable_identity,
            workspace_context=workspace_context,
        )

    def test_collects_referenced_types_from_lambda_kwonlyarg_annotation(
        self,
        mocker: MockerFixture,
    ) -> None:
        annotation = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                kwonlyargs=(create_argument(annotation=annotation),),
            ),
        )
        symbol_type = create_symbol_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Success((symbol_type,)),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((symbol_type,))
        resolve_identity.assert_called_once_with(
            identity=annotation.callable_identity,
            workspace_context=workspace_context,
        )

    def test_collects_referenced_types_from_lambda_kwarg_annotation(
        self,
        mocker: MockerFixture,
    ) -> None:
        annotation = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                kwarg=create_argument(annotation=annotation),
            ),
        )
        symbol_type = create_symbol_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Success((symbol_type,)),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((symbol_type,))
        resolve_identity.assert_called_once_with(
            identity=annotation.callable_identity,
            workspace_context=workspace_context,
        )

    def test_collects_referenced_types_from_lambda_kw_default(
        self,
        mocker: MockerFixture,
    ) -> None:
        default = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                kw_defaults=(default,),
            ),
        )
        symbol_type = create_symbol_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Success((symbol_type,)),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((symbol_type,))
        assert resolve_identity.call_count == 1

    def test_collects_referenced_types_from_lambda_default(
        self,
        mocker: MockerFixture,
    ) -> None:
        default = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                defaults=(default,),
            ),
        )
        symbol_type = create_symbol_type()
        workspace_context = create_workspace_context()

        resolve_identity = mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Success((symbol_type,)),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=[],
            workspace_context=workspace_context,
        )

        assert result == Success((symbol_type,))
        resolve_identity.assert_called_once_with(
            identity=default.callable_identity,
            workspace_context=workspace_context,
        )

    def test_returns_failure_when_lambda_body_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        body = create_call_parameter()
        parameter = create_lambda_parameter(
            body=body,
            args=create_arguments(),
        )
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_call_parameter_arg_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        arg_parameter = create_call_parameter()
        parameter = create_call_parameter(args=(arg_parameter,))
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            side_effect=[
                Success((create_symbol_type(),)),
                Failure(resolve_error),
            ],
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_call_parameter_kwarg_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        kwarg_parameter = create_call_parameter()
        parameter = create_call_parameter(
            kwargs=(create_keyword_argument(value=kwarg_parameter),),
        )
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            side_effect=[
                Success((create_symbol_type(),)),
                Failure(resolve_error),
            ],
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_attribute_value_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        value = create_call_parameter()
        parameter = create_attribute_parameter(value=value)
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_dict_key_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        key = create_call_parameter()
        value = create_name_parameter()
        parameter = create_dict_parameter(
            entries=(create_dict_entry(key=key, value=value),),
        )
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_dict_value_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        key = create_name_parameter()
        value = create_call_parameter()
        parameter = create_dict_parameter(
            entries=(create_dict_entry(key=key, value=value),),
        )
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_tuple_element_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        element = create_call_parameter()
        parameter = create_tuple_parameter(elements=(element,))
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_list_element_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        element = create_call_parameter()
        parameter = create_list_parameter(elements=(element,))
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_lambda_posonlyarg_annotation_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        annotation = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                posonlyargs=(create_argument(annotation=annotation),),
            ),
        )
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_lambda_arg_annotation_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        annotation = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                args=(create_argument(annotation=annotation),),
            ),
        )
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_lambda_vararg_annotation_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        annotation = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                vararg=create_argument(annotation=annotation),
            ),
        )
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_lambda_kwonlyarg_annotation_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        annotation = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                kwonlyargs=(create_argument(annotation=annotation),),
            ),
        )
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_lambda_kwarg_annotation_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        annotation = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                kwarg=create_argument(annotation=annotation),
            ),
        )
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_lambda_kw_default_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        default = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                kw_defaults=(default,),
            ),
        )
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]

    def test_returns_failure_when_lambda_default_resolution_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        default = create_call_parameter()
        parameter = create_lambda_parameter(
            body=create_name_parameter(),
            args=create_arguments(
                defaults=(default,),
            ),
        )
        workspace_context = create_workspace_context()
        existing = create_symbol_type()
        referenced_types: list[ReferencedType] = [existing]
        resolve_error = create_resolve_error()

        mocker.patch(
            "gyomu_test.helper.defaults.referenced_types.resolve_identity",
            return_value=Failure(resolve_error),
        )

        result = aggregate_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuTestError)
        assert referenced_types == [existing]
