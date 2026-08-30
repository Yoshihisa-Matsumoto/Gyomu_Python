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
    return ParameterMaster(
        id=model.id,
        item_key=model.item_key,
        item_fromdate=model.item_fromdate,
        item_value=model.item_value,
    )


def to_model_for_select(schema: ParameterMaster) -> GyomuParamMaster:
    return GyomuParamMaster(
        id=schema.id,
        item_key=schema.item_key,
        item_value=schema.item_value,
        item_fromdate=schema.item_fromdate,
    )


def to_model_for_insert(schema: ParameterMasterCreate) -> dict[str, object]:
    return {
        "id": uuid7(),
        "item_key": schema.item_key,
        "item_value": schema.item_value,
        "item_fromdate": schema.item_fromdate,
    }


def to_model_for_update(
    schema: ParameterMasterUpdate,
) -> Result[dict[str, object], ValidationError]:
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
