from pathlib import Path

from griffe import Module
from gyomu_schema.schemas.python.types import PythonPath, SourceRelativePath
from gyomu_schema.utility.returns import from_sync
from returns.result import Result

from gyomu_python_analysis.analysis.file.source_file_context import SourceFileContext
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext


def load_module(
    context: ProjectContext, module_path: PythonPath
) -> Result[SourceFileContext, AnalysisError]:

    def load_griffe() -> SourceFileContext:

        module = context.loader.load(module_path)
        if not isinstance(module, Module):
            raise ValueError(f"Invalid Module Path: {module_path}")
        full_path = module.filepath
        if not isinstance(full_path, Path):
            raise ValueError(f"module full path is Not Path: {full_path}")
        source_path = full_path.relative_to(context.project_root / context.source_root)
        return SourceFileContext(module=module, path=SourceRelativePath(source_path))

    return from_sync(
        load_griffe,
        build_error=lambda e: AnalysisError(
            message="fail to load source",
            file_path=module_path,
            phase="source-file-load",
            context="gyomu_python_analysis.analysis.load_sourde_file",
        ).chain(e),
    )


# def _get_module_name(
#     source_file_path: SourceRelativePath,
# ) -> str:
#     return source_file_path.with_suffix("").as_posix().replace("/", ".")
