import json

from pydantic import BaseModel


def to_json_schema(schema: type[BaseModel]) -> str:
    return json.dumps(schema.model_json_schema(), indent=2, ensure_ascii=False)
