from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from gyomu_ai_compiler.pipelines.document.executor.object import build_section_object
from gyomu_schema.error.ai import AiError
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.document.content import BulletList, BulletListItem
from gyomu_schema.schemas.document.section import SectionPromptProvider
from pydantic import BaseModel, Field
from returns.result import Failure, Result, Success


class GeneratedBulletListItem(BaseModel):
    text: str = Field(description=("The text content of this bullet point."))
    children: tuple[GeneratedBulletListItem, ...] | None = Field(
        description=(
            "Nested bullet points. Omit this field when there are "
            "no nested bullet points."
        ),
        default=None,
    )


class GeneratedBulletList(BaseModel):
    kind: Literal["bullet-list"] = "bullet-list"
    items: tuple[GeneratedBulletListItem, ...]


def _create_translation_id_generator() -> Callable[[], int]:
    next_id = 0

    def create_translation_id() -> int:
        nonlocal next_id
        next_id += 1
        return next_id

    return create_translation_id


def _to_bullet_list(
    generated: GeneratedBulletList,
    create_translation_id: Callable[[], int],
) -> BulletList:
    return BulletList(
        items=tuple(
            _to_bullet_list_item(item, create_translation_id)
            for item in generated.items
        )
    )


def _to_bullet_list_item(
    item: GeneratedBulletListItem,
    create_translation_id: Callable[[], int],
) -> BulletListItem:
    translation_id = create_translation_id()
    children = (
        tuple(
            _to_bullet_list_item(child, create_translation_id)
            for child in item.children
        )
        if item.children is not None
        else None
    )

    return BulletListItem(
        translation_id=translation_id,
        text=item.text,
        children=children,
    )


async def build_bullet_list[TSectionId: str, TContext: BaseModel](
    section_id: TSectionId,
    context: TContext,
    provider: SectionPromptProvider[TSectionId, TContext],
) -> Result[BulletList, GyomuIOError | AiError]:
    generate_result = await build_section_object(
        section_id=section_id,
        context=context,
        provider=provider,
        schema=GeneratedBulletList,
    )
    if isinstance(generate_result, Failure):
        return generate_result

    return Success(
        _to_bullet_list(
            generated=generate_result.unwrap(),
            create_translation_id=_create_translation_id_generator(),
        )
    )
