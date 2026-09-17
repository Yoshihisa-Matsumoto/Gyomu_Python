from dataclasses import dataclass

from gyomu_ai_compiler.pipelines.docstring_update.context.declaration_context import (
    ContextEntry,
)
from gyomu_ai_compiler.pipelines.docstring_update.context.file_context import (
    DocstringFileContext,
)
from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    DocstringUpdatePlan,
)
from gyomu_schema.schemas.python.types import DeclarationIdentity


@dataclass(frozen=True)
class ValidResult:
    pass


@dataclass(frozen=True)
class InvalidResult:
    diff: tuple[DeclarationIdentity, ...]


ValidationResult = ValidResult | InvalidResult


def validate_docstring_update_plan(
    context: DocstringFileContext, plan: DocstringUpdatePlan
) -> ValidationResult:
    context_identities = get_docstring_identities_from_context(context)
    plan_identities = get_docstring_signature_from_update_plan(plan)
    print(context_identities)
    print(plan_identities)
    diff = tuple(context_identities - plan_identities)

    if diff:
        return InvalidResult(diff=diff)

    return ValidResult()


def get_docstring_signature_from_update_plan(
    plan: DocstringUpdatePlan,
) -> set[DeclarationIdentity]:
    return {entry.identity for entry in plan.entries}


def get_docstring_identities_from_context(
    context: DocstringFileContext,
) -> set[DeclarationIdentity]:
    identities: set[DeclarationIdentity] = set()

    for symbol in context.symbols:
        identities.add(symbol.target)

        if symbol.children:
            _collect_documentable_identities(
                symbol.children,
                identities,
                depth=0,
            )

    return identities


def _collect_documentable_identities(
    entries: tuple[ContextEntry, ...], identities: set[DeclarationIdentity], depth: int
) -> None:
    for member in entries:
        if not member.documentable.documentable:
            continue
        identities.add(member.target)
        depth = depth + 1
        if member.children and depth < 2:
            _collect_documentable_identities(
                member.children, identities=identities, depth=depth
            )
