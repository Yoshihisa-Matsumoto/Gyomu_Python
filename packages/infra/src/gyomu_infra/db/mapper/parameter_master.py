from gyomu_schema.error.validation import ValidationError
from gyomu_schema.parameter.parameter_master import (
    ParameterMaster,
    ParameterMasterCreate,
    ParameterMasterUpdate,
)
from returns.result import Failure, Result, Success
from uuid6 import uuid7

from gyomu_infra.db.model.generated.models import GyomuParamMaster


def to_schema(model: GyomuParamMaster) -> ParameterMaster:
    """Convert GyomuParamMaster model to ParameterMaster schema.

    Converts a database model instance to a ParameterMaster schema.

    Args:
        model (GyomuParamMaster): The GyomuParamMaster database model instance.

    Returns:
        ParameterMaster: The converted ParameterMaster schema.
    """
    return ParameterMaster(
        id=model.id,
        item_key=model.item_key,
        item_fromdate=model.item_fromdate,
        item_value=model.item_value,
    )


def to_model_for_select(schema: ParameterMaster) -> GyomuParamMaster:
    """Convert ParameterMaster schema to GyomuParamMaster model.

    Converts a ParameterMaster schema to a database model instance.

    Args:
        schema (ParameterMaster): The ParameterMaster schema instance.

    Returns:
        GyomuParamMaster: The converted GyomuParamMaster database model instance.
    """
    return GyomuParamMaster(
        id=schema.id,
        item_key=schema.item_key,
        item_value=schema.item_value,
        item_fromdate=schema.item_fromdate,
    )


def to_model_for_insert(schema: ParameterMasterCreate) -> dict[str, object]:
    """Convert ParameterMasterCreate schema to insert values dictionary.

    Converts a ParameterMasterCreate schema to a dictionary of model values for
    insertion.

    Args:
        schema (ParameterMasterCreate): The ParameterMasterCreate schema instance.

    Returns:
        dict[str, object]: A dictionary of column values for insertion, including a
            generated ID.
    """
    return {
        "id": uuid7(),
        "item_key": schema.item_key,
        "item_value": schema.item_value,
        "item_fromdate": schema.item_fromdate,
    }


def to_model_for_update(
    schema: ParameterMasterUpdate,
) -> Result[dict[str, object], ValidationError]:
    """Convert ParameterMasterUpdate schema to update values dictionary with validation.

    Converts a ParameterMasterUpdate schema to a dictionary of update values, validating
    fields against the database model.

    Args:
        schema (ParameterMasterUpdate): The ParameterMasterUpdate schema instance.

    Returns:
        Result[dict[str, object], ValidationError]: A Result containing a dictionary of
            validated update values on success, or a ValidationError on failure.
    """
    values: dict[str, object] = {}

    for field_name in schema.model_fields_set:
        if field_name == "id":
            continue

        value = getattr(schema, field_name)

        column = GyomuParamMaster.__table__.columns.get(field_name)

        if column is None:
            return Failure(
                ValidationError(
                    f"Unknown field: {field_name}",
                    context="to_model_for_update",
                    details={
                        "field": field_name,
                    },
                )
            )

        if value is None and not column.nullable:
            return Failure(
                ValidationError(
                    f"Field '{field_name}' does not allow None",
                    context="to_model_for_update",
                    details={
                        "field": field_name,
                    },
                )
            )

        values[field_name] = value

    return Success(values)
