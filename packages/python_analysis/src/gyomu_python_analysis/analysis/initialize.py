import ast
from pathlib import Path
from tomllib import loads

from gyomu_infra.filesystem.file_io import enumerate_files, read_text
from gyomu_schema.schemas.python.types import ProjectRelativePath, PythonPath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext


def initialize_project_context(
    project_root: FullPath, source_root: ProjectRelativePath
) -> Result[ProjectContext, AnalysisError]:
    pyproject_path = project_root / "pyproject.toml"
    read_result = read_text(pyproject_path)
    if isinstance(read_result, Failure):
        return Failure(
            AnalysisError(
                "fail to read pyproject.toml",
                file_path=PythonPath(""),
                phase="project-load",
                context="gyomu_python_analysis.analysis.initialize.initialize_project_context",
            ).chain(read_result.failure())
        )
    toml_data = loads(read_result.unwrap())
    # print(repr(toml_data))
    project = toml_data["project"]
    name = "" if "name" not in project else project["name"]
    description = None if "description" not in project else project["description"]
    is_version_dynamic = "dynamic" in project and "version" in project["dynamic"]
    version = "" if "version" not in project else project["version"]
    # print(version)
    # print(is_version_dynamic)
    if is_version_dynamic:
        backend = toml_data["build-system"]["requires"]
        # print(backend)
        if "hatchling" in backend:
            version_path = (
                None
                if "tool" not in toml_data
                else toml_data["tool"]["hatch"]["version"]["path"]
            )
            # print(version_path)
            if isinstance(version_path, str):
                version_result = read_version(project_root / Path(version_path))
                if isinstance(version_result, Failure):
                    return version_result
                version = version_result.unwrap()

    files = find_included_python_files(
        project_root=project_root, source_root=source_root
    )
    return Success(
        ProjectContext(
            project_root=project_root,
            source_root=source_root,
            name=name,
            description=description,
            version=str(version),
            included_files=files,
        )
    )


def find_included_python_files(
    project_root: FullPath, source_root: ProjectRelativePath
) -> frozenset[ProjectRelativePath]:
    source_path = project_root / source_root
    files = enumerate_files(source_path, _is_python_source_file, project_root)
    return frozenset(ProjectRelativePath(path) for path in files)


def _is_python_source_file(path: Path) -> bool:
    return path.suffix == ".py" and not _is_test_file(path)


def _is_test_file(path: Path) -> bool:
    return path.name.startswith("test_") or path.name.endswith("_test.py")


def read_version(path: Path) -> Result[str | None, AnalysisError]:
    # print(path)
    source_result = read_text(path)
    if isinstance(source_result, Failure):
        return Failure(
            AnalysisError(
                "fail to read version file",
                file_path=PythonPath(""),
                phase="project-load",
                context="gyomu_python_analysis.analysis.initialize.read_version",
                details={"path": path},
            )
        )
    tree = ast.parse(source_result.unwrap(), filename=str(path))

    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "__version__"
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            return Success(node.value.value)

    return Success(None)


# if __name__ == "__main__":
#     result = initialize_project_context(
#         project_root=FullPath(
#             Path("c:/data/program/python/gyomu-python/packages/docstring")
#         ),
#         source_root=ProjectRelativePath(Path("./src")),
#     )
#     if isinstance(result, Success):
#         print("Success")
#     else:
#         print(repr(result.failure()))
