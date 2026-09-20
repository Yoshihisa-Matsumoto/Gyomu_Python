import asyncio
from pathlib import Path

from dotenv import load_dotenv
from gyomu_docstring.update.process import process_docstring_update
from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_schema.option.update import (
    UpdateDebugInfoOption,
    UpdateOption,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Success


async def update_with_real_llm(
    project_full_path: FullPath, source_project_relative_path: ProjectRelativePath
) -> None:
    load_dotenv()
    result = initialize_project_context(
        project_root=project_full_path,
        source_root=ProjectRelativePath(Path("src")),
    )
    if isinstance(result, Failure):
        print(repr(result.failure()))
        return

    assert isinstance(result, Success)

    project_context = result.unwrap()

    file_path = source_project_relative_path

    option = UpdateOption(
        debug_info=UpdateDebugInfoOption(
            dump_to_file=True,
            updated_symbol_docstring=True,
            file_update_plan=True,
            rendered_symbol_docstring=True,
            docstring_update_plan=True,
            docstring_update_context=True,
        ),
        # action=UpdateActionOption(no_llm_request=True),
        no_check_cache=True,
    )
    result = load_file_analysis_context(
        context=project_context, file_path=file_path, option=option
    )
    assert isinstance(result, Success)

    file_context = result.unwrap()
    result = await process_docstring_update(
        context=project_context, file_context=file_context, option=option
    )
    if isinstance(result, Failure):
        failure = result.failure()
        print(failure)
        if failure.__cause__:
            print(failure.__cause__)
    assert isinstance(result, Success)


async def main():
    package = FullPath(Path("../schema").resolve())
    print(package)
    await update_with_real_llm(
        package,
        ProjectRelativePath(Path("src/gyomu_schema/conversation/conversation.py")),
    )


if __name__ == "__main__":
    asyncio.run(main())
