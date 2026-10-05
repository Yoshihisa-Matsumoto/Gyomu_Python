from unittest.mock import AsyncMock

import pytest
from gyomu_concept.document.builder.bullet_list import (
    GeneratedBulletList,
    GeneratedBulletListItem,
    build_bullet_list,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.document.content import BulletList
from gyomu_schema.schemas.document.section import SectionPromptProvider
from pydantic import BaseModel
from pytest_mock import MockerFixture
from returns.result import Failure, Success


class UserTest(BaseModel):
    user_id: str
    name: str


class TestBuildBulletList:
    @pytest.fixture
    def context(self) -> UserTest:
        return UserTest(user_id="uid", name="Alice")

    @pytest.mark.asyncio
    async def test_returns_generation_failure(
        self,
        mocker: MockerFixture,
        context: UserTest,
    ) -> None:
        error = GyomuIOError(
            "Failed to generate bullet list.",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
        )

        provider = mocker.Mock(spec=SectionPromptProvider)

        mocker.patch(
            "gyomu_concept.document.builder.bullet_list.build_section_object",
            new=AsyncMock(return_value=Failure(error)),
        )

        result = await build_bullet_list(
            "test-section",
            context,
            provider,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error

    @pytest.mark.asyncio
    async def test_returns_built_bullet_list(
        self,
        mocker: MockerFixture,
        context: UserTest,
    ) -> None:
        generated = GeneratedBulletList(
            items=(
                GeneratedBulletListItem(text="First"),
                GeneratedBulletListItem(text="Second"),
            )
        )

        provider = mocker.Mock(spec=SectionPromptProvider)

        mocker.patch(
            "gyomu_concept.document.builder.bullet_list.build_section_object",
            new=AsyncMock(return_value=Success(generated)),
        )

        result = await build_bullet_list(
            "test-section",
            context,
            provider,
        )

        assert isinstance(result, Success)

        bullet_list = result.unwrap()

        assert isinstance(bullet_list, BulletList)
        assert len(bullet_list.items) == 2

        assert bullet_list.items[0].translation_id == 1
        assert bullet_list.items[0].text == "First"
        assert bullet_list.items[0].children is None

        assert bullet_list.items[1].translation_id == 2
        assert bullet_list.items[1].text == "Second"
        assert bullet_list.items[1].children is None

    @pytest.mark.asyncio
    async def test_assigns_translation_ids_depth_first(
        self,
        mocker: MockerFixture,
        context: UserTest,
    ) -> None:
        generated = GeneratedBulletList(
            items=(
                GeneratedBulletListItem(
                    text="A",
                    children=(
                        GeneratedBulletListItem(text="B"),
                        GeneratedBulletListItem(
                            text="C",
                            children=(GeneratedBulletListItem(text="D"),),
                        ),
                    ),
                ),
                GeneratedBulletListItem(text="E"),
            )
        )

        provider = mocker.Mock(spec=SectionPromptProvider)

        mocker.patch(
            "gyomu_concept.document.builder.bullet_list.build_section_object",
            new=AsyncMock(return_value=Success(generated)),
        )

        result = await build_bullet_list(
            "test-section",
            context,
            provider,
        )

        assert isinstance(result, Success)

        items = result.unwrap().items

        assert items[0].translation_id == 1
        assert items[0].text == "A"

        assert items[0].children is not None
        assert items[0].children[0].translation_id == 2
        assert items[0].children[0].text == "B"

        assert items[0].children[1].translation_id == 3
        assert items[0].children[1].text == "C"

        assert items[0].children[1].children is not None
        assert items[0].children[1].children[0].translation_id == 4
        assert items[0].children[1].children[0].text == "D"

        assert items[1].translation_id == 5
        assert items[1].text == "E"

    @pytest.mark.asyncio
    async def test_passes_arguments_to_build_section_object(
        self,
        mocker: MockerFixture,
        context: UserTest,
    ) -> None:
        generated = GeneratedBulletList(items=(GeneratedBulletListItem(text="First"),))

        provider = mocker.Mock(spec=SectionPromptProvider)

        build_object = mocker.patch(
            "gyomu_concept.document.builder.bullet_list.build_section_object",
            new=AsyncMock(return_value=Success(generated)),
        )

        section_id = "test-section"

        await build_bullet_list(
            section_id,
            context,
            provider,
        )

        build_object.assert_awaited_once_with(
            section_id=section_id,
            context=context,
            provider=provider,
            schema=GeneratedBulletList,
        )
