# from os import getcwd
# from pathlib import Path

# from gyomu_python_analysis.analysis.initialize import initialize_project_context
# from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
# from gyomu_python_analysis.analysis.workspace import find_root
# from gyomu_schema.schemas.python.types import ProjectRelativePath
# from gyomu_schema.schemas.types import FullPath
# from gyomu_schema.utility.fromatting import format_object
# from returns.result import Failure, Success


# def test_load_test() -> None:
#     root_result = find_root(start_directory=FullPath(Path(getcwd())))
#     workspace_context = root_result.unwrap()
#     workspace_root_context = initialize_project_context(
#         project_root=workspace_context.workspace_root.path,
#         source_root=ProjectRelativePath(Path(".")),
#     ).unwrap()
#     load_result = load_file_analysis_context(
#         context=workspace_root_context,
#         file_path=ProjectRelativePath(
#             Path("packages/workflow/tests/unit/snapshot/conftest.py")
#         ),
#     )
#     assert isinstance(load_result, Success)
#     load_result = load_file_analysis_context(
#         context=workspace_root_context,
#         file_path=ProjectRelativePath(
#             Path(
#                 "packages/schema/tests/unit/schemas/config/test/test_model_defaults.py"
#             )
#         ),
#     )
#     if isinstance(load_result, Failure):
#         print(format_object(load_result.failure(), depth=8))
#     assert isinstance(load_result, Success)
def dummy() -> None:
    pass
