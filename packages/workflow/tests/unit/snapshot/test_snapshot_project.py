from gyomu_schema.error.gyomu import GyomuError
from gyomu_workflow.snapshot.project import find_project_by_name
from returns.result import Failure, Success

from packages.concept.test_support.helpers import (
    create_monorepo_workspace_context,
    create_workspace_context,
)
from packages.python_analysis.test_support.helpers import (
    create_py_project_config,
    create_workspace_project,
)


class TestFindProjectByName:
    def test_returns_matching_project(self) -> None:
        target_package = create_workspace_project(
            config=create_py_project_config(name="gyomu-ai")
        )

        other_package = create_workspace_project(
            config=create_py_project_config(name="gyomu-schema")
        )

        workspace_context = create_workspace_context(
            projects=(other_package, target_package)
        )

        assert [project.config.name for project in workspace_context.projects] == [
            "gyomu-schema",
            "gyomu-ai",
        ]
        result = find_project_by_name(
            workspace_context=workspace_context,
            project_name="gyomu-ai",
        )

        assert isinstance(result, Success)
        assert result.unwrap() is target_package

    def test_returns_failure_when_not_found(self) -> None:
        package = create_workspace_project()
        package.config.name = "gyomu-schema"

        workspace_context = create_monorepo_workspace_context()
        workspace_context.projects = (package,)

        result = find_project_by_name(
            workspace_context=workspace_context,
            project_name="gyomu-ai",
        )

        assert isinstance(result, Failure)

        error = result.failure()
        assert isinstance(error, GyomuError)
        assert error.message == "project not found"

    def test__returns_first_match_when_names_are_duplicated(
        self,
    ) -> None:
        first_package = create_workspace_project()
        first_package.config.name = "gyomu-ai"

        second_package = create_workspace_project()
        second_package.config.name = "gyomu-ai"

        workspace_context = create_monorepo_workspace_context()
        workspace_context.projects = (first_package, second_package)

        result = find_project_by_name(
            workspace_context=workspace_context,
            project_name="gyomu-ai",
        )

        assert isinstance(result, Success)
        assert result.unwrap() is first_package
