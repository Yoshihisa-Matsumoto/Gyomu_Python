from typing import get_args
from unittest.mock import MagicMock

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.resolve.file_analysis_cache import FileAnalysisCache
from gyomu_python_analysis.resolve.type_reference import _resolve_structure
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.type.structure import UnknownStructureAnalysis
from gyomu_schema.schemas.python.type.type_analysis import StructureAnalysis

from packages.schema.test_support.helpers import STRUCTURE_FACTORIES


def test_all_structure_types_have_handlers(mocker) -> None:
    structure_types: set[type[StructureAnalysis]] = set(
        get_args(StructureAnalysis.__value__)
    )
    factory_types: set[type[StructureAnalysis]] = set(STRUCTURE_FACTORIES)

    assert structure_types == factory_types
    module = MagicMock(spec=ModuleAnalysis)
    module.imports = {}
    module.symbols = tuple()

    project_context = MagicMock(spec=ProjectContext)
    file_analysis_cache = MagicMock(spec=FileAnalysisCache)
    for structure in STRUCTURE_FACTORIES.values():
        if not isinstance(structure, UnknownStructureAnalysis):
            result = _resolve_structure(
                structure=structure,
                parameter_name="param",
                type_text="type",
                module=module,
                project_context=project_context,
                file_analysis_cache=file_analysis_cache,
            )
