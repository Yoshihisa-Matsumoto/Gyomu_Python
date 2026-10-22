from gyomu_schema.schemas.testing.helper import (
    HelperFileInventory,
    HelperInventoryItem,
    HelperReconcileResult,
    HelperUpdate,
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


def _is_equal(existing: HelperInventoryItem, expected: HelperInventoryItem) -> bool:
    if existing.function_name != expected.function_name:
        return False
    if len(existing.parameters) != len(expected.parameters):
        return False

    return all(
        existing_param.name == expected_param.name
        and existing_param.parameter_type.text == expected_param.parameter_type.text
        for existing_param, expected_param in zip(
            existing.parameters,
            expected.parameters,
            strict=True,
        )
    )


def reconcile(
    existing: tuple[HelperFileInventory, ...], expected: tuple[HelperInventoryItem, ...]
) -> HelperReconcileResult:
    create: list[HelperInventoryItem] = []
    update: list[HelperUpdate] = []
    unchanged: list[HelperInventoryItem] = []
    delete_candidates: list[HelperInventoryItem] = []
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
                if _is_equal(expected=expected_inventory, existing=existing_inventory):
                    unchanged.append(existing_inventory)
                else:
                    update.append(
                        HelperUpdate(
                            expected=expected_inventory, existing=existing_inventory
                        )
                    )

    for expected_inventory in expected:
        existing_inventory = _find_exising_inventory(
            existing=existing, target_inventory=expected_inventory
        )
        if existing_inventory is None:
            create.append(expected_inventory)

    return HelperReconcileResult(
        create=tuple(create),
        update=tuple(update),
        unchanged=tuple(unchanged),
        delete_candidates=tuple(delete_candidates),
    )
