from dataclasses import dataclass
from pathlib import Path

from gyomu_python_analysis.analysis.file.source_file_context import SourceFileContext
from gyomu_python_analysis.analysis.load import load_module
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.python.types import ProjectRelativePath, PythonPath
from gyomu_schema.schemas.types import FullPath

FIXTURES_ROOT = FullPath(Path(__file__).parent / "fixtures")


def _create_context() -> ProjectContext:
    return ProjectContext(
        project_root=FIXTURES_ROOT,
        source_root=ProjectRelativePath(Path("src")),
    )


@dataclass
class BaseContext:
    project: ProjectContext
    source: SourceFileContext


class AnalysisTestBase:
    def _read_module_fixture(self, module_path: PythonPath) -> BaseContext:
        context = _create_context()
        # search_path = context.project_root / context.source_root
        # print("search:", search_path)
        # print("modulePath:", modulePath)

        # loader = GriffeLoader(
        #     search_paths=[search_path],
        # )
        # module = loader.load(modulePath)
        # if isinstance(module, Module):
        #     print("location:", module.filepath)
        #     return module
        # raise ValueError("Invalid:")
        result = load_module(context, module_path)

        source_file_context = result.unwrap()

        return BaseContext(project=context, source=source_file_context)
