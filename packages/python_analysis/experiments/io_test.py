import json
from pathlib import Path

from pydantic import TypeAdapter

from gyomu_schema.schemas.python.module import ModuleAnalysis


cache_path = Path("/home/yoshm/work/gyomu_python/packages/infra/.gyomu/cache/src/gyomu_infra/gyomu/variable/variable_translator.py.json")
data = cache_path.read_text()

print("1", len(data))

parsed = json.loads(data)

print("2")

adapter = TypeAdapter(ModuleAnalysis)

print("3")

result = adapter.validate_python(parsed)

print("4")
