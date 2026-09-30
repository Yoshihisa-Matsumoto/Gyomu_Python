from gyomu_ai_compiler.pipelines.package_concept.context.input import (
    PackageConceptInput,
)
from gyomu_ai_compiler.pipelines.package_concept.renderer.package_analysis import (
    render_package_analysis,
)
from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis
from pytest_mock import MockerFixture


class TestRenderPackageAnalysis:
    def test(self, mocker: MockerFixture) -> None:
        context = mocker.Mock(spec=PackageAnalysis)
        package_input = mocker.Mock(spec=PackageConceptInput)

        build = mocker.patch(
            "gyomu_ai_compiler.pipelines.package_concept.renderer.package_analysis"
            ".build_package_concept_input",
            return_value=package_input,
        )

        dump = mocker.patch(
            "gyomu_ai_compiler.pipelines.package_concept.renderer.package_analysis"
            ".dump_json",
            return_value='{"test": true}',
        )

        result = render_package_analysis(context)

        assert result == '{"test": true}'
        build.assert_called_once_with(context=context)
        dump.assert_called_once_with(
            value=package_input,
            model_type=PackageConceptInput,
        )
