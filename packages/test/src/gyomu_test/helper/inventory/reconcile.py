import io
import tokenize

from gyomu_infra.logger import logger
from gyomu_schema.schemas.testing.helper import (
    ExistingHelperInventoryItem,
    HelperFileInventory,
    HelperInventoryItem,
    HelperReconcileResult,
    HelperUpdate,
)

from gyomu_test.helper.inventory.function import (
    generate_function_code,
    read_function_code,
)


def _find_exising_inventory(
    existing: tuple[HelperFileInventory, ...], target_inventory: HelperInventoryItem
) -> HelperInventoryItem | None:
    for file in existing:
        inventory_candidate = next(
            (
                item
                for item in file.items
                if item.target_identity == target_inventory.target_identity
            ),
            None,
        )
        if inventory_candidate is not None:
            return inventory_candidate
    return None


def _normalize_python_tokens(source: str) -> tuple[tuple[int, str], ...]:
    tokens = tuple(
        token
        for token in tokenize.generate_tokens(io.StringIO(source).readline)
        if token.type
        not in (
            tokenize.NL,
            tokenize.COMMENT,
            tokenize.ENDMARKER,
        )
    )

    normalized: list[tuple[int, str]] = []

    for index, token in enumerate(tokens):
        if token.type == tokenize.OP and token.string == ",":
            next_token = tokens[index + 1] if index + 1 < len(tokens) else None
            if (
                next_token is not None
                and next_token.type == tokenize.OP
                and next_token.string in (")", "]", "}")
            ):
                continue

        normalized.append((token.type, token.string))

    return tuple(normalized)


def _is_equal(
    file_inventory: HelperFileInventory,
    existing: ExistingHelperInventoryItem,
    expected: HelperInventoryItem,
) -> bool:
    if existing.function_name != expected.function_name:
        return False

    if len(existing.parameters) != len(expected.parameters):
        return False

    if not all(
        existing_param.name == expected_param.name
        and existing_param.parameter_type.text == expected_param.parameter_type.text
        for existing_param, expected_param in zip(
            existing.parameters,
            expected.parameters,
            strict=True,
        )
    ):
        return False

    expected_function = generate_function_code(expected)
    existing_function = read_function_code(
        file_inventory=file_inventory, location=existing.location
    )
    is_same = _normalize_python_tokens(expected_function) == _normalize_python_tokens(
        existing_function
    )
    if not is_same:
        logger.debug(expected_function)
        logger.debug(existing_function)
    return is_same


def reconcile(
    existing: tuple[HelperFileInventory, ...], expected: tuple[HelperInventoryItem, ...]
) -> HelperReconcileResult:
    create: list[HelperInventoryItem] = []
    update: list[HelperUpdate] = []
    unchanged: list[ExistingHelperInventoryItem] = []
    delete_candidates: list[ExistingHelperInventoryItem] = []
    for file_inventory in existing:
        for existing_inventory in file_inventory.items:
            expected_inventory = next(
                (
                    item
                    for item in expected
                    if item.target_identity == existing_inventory.target_identity
                ),
                None,
            )
            if expected_inventory is None:
                delete_candidates.append(existing_inventory)
            else:
                # compare
                if _is_equal(
                    file_inventory=file_inventory,
                    expected=expected_inventory,
                    existing=existing_inventory,
                ):
                    unchanged.append(existing_inventory)
                else:
                    update.append(
                        HelperUpdate(
                            file_path=file_inventory.file_path,
                            expected=expected_inventory,
                            existing=existing_inventory,
                        )
                    )

    for expected_inventory in expected:
        target_existing_inventory = _find_exising_inventory(
            existing=existing, target_inventory=expected_inventory
        )
        if target_existing_inventory is None:
            create.append(expected_inventory)

    return HelperReconcileResult(
        create=tuple(create),
        update=tuple(update),
        unchanged=tuple(unchanged),
        delete_candidates=tuple(delete_candidates),
    )
