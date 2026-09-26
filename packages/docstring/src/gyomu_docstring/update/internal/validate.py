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
    """Represents a successful validation result."""

    pass


@dataclass(frozen=True)
class InvalidResult:
    """Represents a failed validation result containing a difference collection of
    declaration identities.
    """

    diff: tuple[DeclarationIdentity, ...]
    """Collection of differing declaration identities."""


ValidationResult = ValidResult | InvalidResult
"""Type alias representing the outcome of a validation operation, either valid or
invalid.
"""


def validate_docstring_update_plan(
    context: DocstringFileContext, plan: DocstringUpdatePlan
) -> ValidationResult:
    """Validates a docstring update plan against a file context.

    Args:
        context (DocstringFileContext): The file context containing expected symbol
            identities.
        plan (DocstringUpdatePlan): The docstring update plan to validate.

    Returns:
        ValidationResult: A ValidationResult indicating success or containing the
            identity difference.
    """
    context_identities = get_docstring_identities_from_context(context)
    plan_identities = get_docstring_signature_from_update_plan(plan)
    # print(context_identities)
    # print(plan_identities)
    diff = tuple(context_identities - plan_identities)

    if diff:
        return InvalidResult(diff=diff)

    return ValidResult()


def get_docstring_signature_from_update_plan(
    plan: DocstringUpdatePlan,
) -> set[DeclarationIdentity]:
    """Extracts a set of declaration identities from a docstring update plan.

    Args:
        plan (DocstringUpdatePlan): The docstring update plan to inspect.

    Returns:
        set[DeclarationIdentity]: A set of declaration identities present in the plan
            entries.
    """
    return {entry.identity for entry in plan.entries}


def get_docstring_identities_from_context(
    context: DocstringFileContext,
) -> set[DeclarationIdentity]:
    """Extracts all documentable declaration identities from a file context.

    Args:
        context (DocstringFileContext): The file context to extract identities from.

    Returns:
        set[DeclarationIdentity]: A set of documentable declaration identities.
    """
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
    """Recursively collects documentable identities from context entries.

    Args:
        entries (tuple[ContextEntry, ...]): Tuple of context entries to process.
        identities (set[DeclarationIdentity]): Set to accumulate collected identities.
        depth (int): Current recursion depth.

    Returns:
        None: None
    """
    for member in entries:
        if not member.documentable.documentable:
            continue
        identities.add(member.target)
        depth = depth + 1
        if member.children and depth < 2:
            _collect_documentable_identities(
                member.children, identities=identities, depth=depth
            )
