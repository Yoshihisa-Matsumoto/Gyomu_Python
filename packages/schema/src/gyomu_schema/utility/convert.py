import json

from pydantic import BaseModel


def to_json_schema(schema: type[BaseModel]) -> str:
    """Convert a Pydantic model to a JSON schema string.

    Converts a Pydantic model class into a formatted JSON schema string.

    Args:
        schema (type[BaseModel]): Pydantic BaseModel class to convert.

    Returns:
        str: A JSON-formatted string representing the model's schema.
    """
    return json.dumps(schema.model_json_schema(), indent=2, ensure_ascii=False)
