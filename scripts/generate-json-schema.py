import json
from os import getcwd
from pathlib import Path

from gyomu_python_analysis.analysis.workspace import find_root
from gyomu_schema.schemas.knowledge.coding_guideline import CodingGuideline
from gyomu_schema.schemas.knowledge.development import Development
from gyomu_schema.schemas.knowledge.package import Package
from gyomu_schema.schemas.knowledge.roadmap import Roadmap
from gyomu_schema.schemas.knowledge.technical import Technical
from gyomu_schema.schemas.types import FullPath

schemas = {
    "Package": Package,
    "Technical": Technical,
    "Development": Development,
    "Roadmap": Roadmap,
    "Coding": CodingGuideline,
}


def write_json_schemas(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, schema in schemas.items():
        json_schema = schema.model_json_schema()

        (output_dir / f"{name}.json").write_text(
            json.dumps(json_schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


result = find_root(FullPath(Path(getcwd()))).unwrap()
write_json_schemas(result.path / "schemas")
