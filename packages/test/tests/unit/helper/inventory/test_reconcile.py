from pathlib import Path

from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.utility.fromatting import format_object
from gyomu_test.helper.inventory.existing import collect_existing_helper_inventory
from gyomu_test.helper.inventory.expected import collect_model_helper_inventory
from gyomu_test.helper.inventory.reconcile import reconcile
from returns.result import Success

from packages.test.tests.unit.helper.inventory.helpers import get_project_context


class TestReconcile:
    def test_from_fixture(self, workspace_context: WorkspaceContext) -> None:
        project_context = get_project_context(workspace_context, "project-b")
        expected_result = collect_model_helper_inventory(
            project_context, workspace_context
        )

        assert isinstance(expected_result, Success)
        expected = expected_result.unwrap()

        root_context_result = initialize_project_context(
            project_root=workspace_context.path,
            source_root=ProjectRelativePath(Path(".")),
        )
        assert isinstance(root_context_result, Success)

        file = ProjectRelativePath(Path("test_support/helpers.py"))
        file2 = ProjectRelativePath(Path("test_support/another_helpers.py"))
        existing_result = collect_existing_helper_inventory(
            root=root_context_result.unwrap(),
            target_project=project_context,
            files=(
                file,
                file2,
            ),
        )
        assert isinstance(existing_result, Success)
        existing = existing_result.unwrap()

        reconcile_result = reconcile(existing=existing, expected=expected)

        print(format_object(reconcile_result, depth=4))

        assert len(reconcile_result.create) == 4
        assert len(reconcile_result.update) == 1
        assert len(reconcile_result.unchanged) == 2
        assert len(reconcile_result.delete_candidates) == 1

        assert {item.target_identity.symbol_id for item in reconcile_result.create} == {
            "project_b.inheritance::AnotherBase",
            "project_b.inheritance::ProductAudit",
            "project_b.inheritance::AuditedProduct",
            "project_b.inheritance::MultipleProduct",
        }

        assert {
            item.target_identity.symbol_id for item in reconcile_result.unchanged
        } == {
            "project_b.models::ProductBaseModel",
            "project_b.models::ProductSummary",
        }

        assert {
            item.target_identity.symbol_id
            for item in reconcile_result.delete_candidates
        } == {
            "project_b.non_models::NonHelper",
        }

        assert (
            reconcile_result.update[0].expected.target_identity
            == reconcile_result.update[0].existing.target_identity
        )
        assert (
            reconcile_result.update[0].expected.function_name
            == reconcile_result.update[0].existing.function_name
            == "create_product_model"
        )
