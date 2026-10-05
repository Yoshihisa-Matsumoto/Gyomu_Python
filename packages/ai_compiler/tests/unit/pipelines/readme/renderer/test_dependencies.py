from gyomu_ai_compiler.pipelines.readme.renderer.dependencies import (
    build_dependencies_messages,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.concept.base import Knowledge
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_compatibility,
    create_dependency,
    create_development,
    create_document_base_context,
    create_package,
    create_roadmap,
    create_technical,
)


class TestBuildDependenciesMessages:
    def test_builds_messages(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_document_base_context()

        load_prompt = mocker.patch(
            "gyomu_ai_compiler.pipelines.readme.renderer.dependencies.load_prompt",
            return_value=Success("dependencies prompt"),
        )

        result = build_dependencies_messages(context)

        assert isinstance(result, Success)

        conversation = result.unwrap()

        assert conversation.system
        assert conversation.system.parts[0].text == "dependencies prompt"
        assert conversation.request
        assert len(conversation.request.parts) == 1

        load_prompt.assert_called_once_with(name="readme/dependencies-assemble.md")

    def test_technical_information(
        self,
    ) -> None:
        context = create_document_base_context(
            knowledge=Knowledge(
                package=create_package(),
                technical=create_technical(
                    dependencies=(
                        create_dependency(
                            package="pydantic",
                            description="Data validation",
                        ),
                    ),
                    compatibility=(
                        create_compatibility(
                            name="Python",
                            supported=">=3.13",
                            description="Supported Python versions",
                        ),
                    ),
                ),
                development=create_development(),
                roadmap=create_roadmap(),
            ),
        )

        result = build_dependencies_messages(context)

        assert isinstance(result, Success)

        user_message = result.unwrap().request
        assert user_message
        assert user_message.parts[0] is not None

        msg = user_message.parts[0].text

        assert '"package": "pydantic"' in msg
        assert '"description": "Data validation"' in msg
        assert '"name": "Python"' in msg
        assert '"supported": ">=3.13"' in msg
        assert '"description": "Supported Python versions"' in msg

    def test_propagates_prompt_load_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        error = GyomuIOError(
            "failed to load prompt",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.readme.renderer.dependencies.load_prompt",
            return_value=Failure(error),
        )

        result = build_dependencies_messages(create_document_base_context())

        assert result == Failure(error)
