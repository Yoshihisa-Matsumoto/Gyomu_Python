
from pathlib import Path

from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.analysis.load_module import load_module_analysis
from gyomu_schema.schemas.python.types import ProjectRelativePath, PythonPath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure

from gyomu_schema.utility.fromatting import format_object

# context = initialize_project_context(project_root=FullPath(Path("../../schema").resolve()),source_root=ProjectRelativePath(Path("src"))).unwrap()
context = initialize_project_context(project_root=FullPath(Path("..").resolve()),source_root=ProjectRelativePath(Path("experiments"))).unwrap()
result = load_module_analysis(context, module_path=PythonPath("sample.user2"))
# result = load_module_analysis(context,module_path=PythonPath("gyomu_schema.schemas.knowledge.roadmap"))
if isinstance(result,Failure):
    print(format_object(result.failure(),depth=6))
# else:
#     print(format_object(result.unwrap(),depth=6))
