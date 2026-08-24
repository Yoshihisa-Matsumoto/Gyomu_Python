from uuid import UUID

from gyomu_schema.error.validation import ValidationError
from gyomu_schema.parameter.parameter_master import ParameterMasterUpdate
from returns.result import Failure, Success

from gyomu_infra.db.mapper.parameter_master import to_model_for_update

id = UUID("019dbc9c-221b-7aa9-b2b7-3cacf8bcb8d6")


def test_to_model_for_update_excludes_unset_fields() -> None:
    schema = ParameterMasterUpdate(
        id=id,
        item_value="new-value",
    )

    result = to_model_for_update(schema)

    assert isinstance(result, Success)
    assert result.unwrap() == {
        "item_value": "new-value",
    }


def test_to_model_for_update_allows_explicit_none_for_nullable_field() -> None:
    schema = ParameterMasterUpdate(
        id=id,
        item_fromdate=None,
    )

    result = to_model_for_update(schema)

    assert isinstance(result, Success)
    assert result.unwrap() == {
        "item_fromdate": None,
    }


def test_to_model_for_update_rejects_none_for_non_nullable_field() -> None:
    schema = ParameterMasterUpdate(
        id=id,
        item_value=None,
    )

    result = to_model_for_update(schema)

    assert isinstance(result, Failure)

    error = result.failure()

    assert isinstance(error, ValidationError)


def test_to_model_for_update_returns_empty_dict_for_empty_update() -> None:
    schema = ParameterMasterUpdate(id=id)

    result = to_model_for_update(schema)

    assert isinstance(result, Success)
    assert result.unwrap() == {}
